// headless-service/dist/headless-service/src/routes/generate-pdf.js
"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const jsx_runtime_1 = require("react/jsx-runtime");
const express_1 = __importDefault(require("express"));
const server_1 = __importDefault(require("react-dom/server"));
const puppeteer_1 = __importDefault(require("puppeteer"));
const client_s3_1 = require("@aws-sdk/client-s3");
const dynamodb_1 = require("../utils/dynamodb");
const slide_component_1 = require("../components/slide-component");
const logger_1 = __importDefault(require("../utils/logger"));
const router = express_1.default.Router();
function sanitizeFileName(input, maxLength = 100) {
    // Define a regex to match invalid characters for file names
    const invalidChars = /[<>:"/\\|?*\x00-\x1F]/g;
    const reservedNames = /^(CON|PRN|AUX|NUL|COM\d|LPT\d)(\..*)?$/i;
    // Replace invalid characters with an underscore
    let sanitized = input.replace(invalidChars, '_');
    // Remove trailing periods and spaces
    sanitized = sanitized.replace(/[. ]+$/, '');
    // Handle reserved names (e.g., CON, PRN, AUX, NUL, COM1, LPT1)
    if (reservedNames.test(sanitized)) {
        sanitized = sanitized.replace(reservedNames, '_$1');
    }
    // Cap the length of the sanitized string
    if (sanitized.length > maxLength) {
        // Try to preserve the file extension if it exists
        const extensionMatch = sanitized.match(/(\.[^.]+)$/);
        const extension = extensionMatch ? extensionMatch[0] : '';
        const baseLength = maxLength - extension.length;
        sanitized = sanitized.slice(0, baseLength) + extension;
    }
    return sanitized;
}
router.post('/:presentationId/pdf', (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { presentationId } = req.params;
    try {
        // Get head slide id
        const presentation = yield (0, dynamodb_1.getPresentationByID)(presentationId, ['head_slide_id', 'topic']);
        if (!presentation.topic) {
            res.status(404).send('Presentation not found, please check the presentation id');
            return;
        }
        if (!presentation.head_slide_id) {
            res.status(500).send('No head slide found for the presentation');
            return;
        }
        const unsortedSlidesArray = yield (0, dynamodb_1.getAllSlides)(presentationId);
        if (!unsortedSlidesArray.length) {
            res.status(500).send('No slides found for the presentation though the presentaton exists');
            return;
        }
        // Convert the slides to linked list map
        let slidesMap = {};
        try {
            unsortedSlidesArray.forEach((slide) => {
                slidesMap[slide.id] = slide;
            });
        }
        catch (error) {
            logger_1.default.error(`Failed to convert slides to linked list map: ${error.message}`);
            res.status(500).send(`Failed to convert slides to linked list map: ${error.message}`);
            return;
        }
        // Sort the slides and convert back to array, removing hidden slides
        let sortedSlidesArray = [];
        try {
            let currentId = presentation.head_slide_id;
            while (currentId) {
                const slide = slidesMap[currentId];
                if (!slide) {
                    break;
                }
                if (!slide.hidden) {
                    sortedSlidesArray.push(slide);
                }
                currentId = slide.next;
            }
        }
        catch (error) {
            logger_1.default.error(`Failed to sort slides: ${error.message}`);
            res.status(500).send(`Failed to sort slides: ${error.message}`);
            return;
        }
        // Render slides to HTML string
        const html = server_1.default.renderToString((0, jsx_runtime_1.jsx)("div", { children: sortedSlidesArray.map((slide, index) => ((0, jsx_runtime_1.jsx)(slide_component_1.SlideComponent, { slide: slide }, index))) }));
        // Generate PDF using Puppeteer
        const browser = yield puppeteer_1.default.launch();
        const page = yield browser.newPage();
        yield page.setContent(html, { waitUntil: 'networkidle0' });
        const pdfBuffer = yield page.pdf({ format: 'A4' });
        yield browser.close();
        // Upload PDF to S3
        const s3Client = new client_s3_1.S3Client({ region: process.env.AWS_REGION });
        const s3Key = `${presentationId}/${sanitizeFileName(presentation.topic)}.pdf`;
        const command = new client_s3_1.PutObjectCommand({
            Bucket: process.env.SOURCES_BUCKET_NAME,
            Key: s3Key,
            Body: pdfBuffer,
            ContentType: 'application/pdf',
        });
        yield s3Client.send(command);
        // Return the S3 key in the response
        res.json({ s3Key });
    }
    catch (error) {
        logger_1.default.error(`Failed to generate PDF: ${error.message}`);
        res.status(500).send(`Failed to generate PDF: ${error.message}`);
    }
}));
exports.default = router;
