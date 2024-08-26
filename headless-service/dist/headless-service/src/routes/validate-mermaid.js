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
const express_1 = require("express");
const cluster_1 = require("../utils/cluster");
const logger_1 = __importDefault(require("../utils/logger"));
const router = (0, express_1.Router)();
router.post('/', (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { diagram } = req.body;
    if (!diagram) {
        logger_1.default.warn('Mermaid diagram is required');
        return res.status(400).send('Mermaid diagram is required');
    }
    function removeStacktrace(errorMessage) {
        if (!errorMessage)
            return '';
        const lines = errorMessage.split('\n');
        const newLines = lines.filter(line => !line.includes('w1.parseError'));
        return newLines.join('\n');
    }
    try {
        const cluster = yield (0, cluster_1.launchCluster)();
        const validateMermaid = (_a) => __awaiter(void 0, [_a], void 0, function* ({ page, data: { diagram } }) {
            yield page.setContent(`
        <!DOCTYPE html>
        <html>
        <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        </head>
        <body>
        <script>
        const diagram = \`${diagram.trim()}\`;
        window.isValid = false;
        window.errorMessage = '';
        try {
            window.isValid = mermaid.parse(diagram);
        } catch (err) {
            window.errorMessage = err.message;
        }
        </script>
        </body>
        </html>
      `);
            const parsingResult = yield page.evaluate(() => window.isValid);
            let errorMessage = '';
            if (!parsingResult) {
                errorMessage = yield page.evaluate(() => window.errorMessage);
            }
            return { parsingResult, errorMessage: removeStacktrace(errorMessage) };
        });
        const { parsingResult, errorMessage } = yield cluster.execute({ diagram }, validateMermaid);
        if (parsingResult) {
            logger_1.default.info('Valid Mermaid diagram');
            res.json({ valid: true, message: 'Valid Mermaid diagram' });
        }
        else {
            logger_1.default.warn(`Invalid Mermaid diagram: ${errorMessage}`);
            res.json({ valid: false, message: errorMessage || 'Invalid Mermaid diagram' });
        }
    }
    catch (error) {
        logger_1.default.error(`Failed to validate Mermaid diagram: ${removeStacktrace(error.message)}`);
        res.json({ valid: false, message: removeStacktrace(error.message) || 'Invalid Mermaid diagram' });
    }
}));
exports.default = router;
