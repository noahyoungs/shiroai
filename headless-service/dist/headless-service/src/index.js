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
require("dotenv/config"); // Load environment variables from .env file
const express_1 = __importDefault(require("express"));
const https_1 = __importDefault(require("https"));
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const logger_1 = __importDefault(require("./utils/logger"));
const mermaid_1 = __importDefault(require("./routes/mermaid"));
const prose_class_1 = __importDefault(require("./routes/prose-class"));
const validate_mermaid_1 = __importDefault(require("./routes/validate-mermaid"));
const mermaid_dimensions_1 = __importDefault(require("./routes/mermaid-dimensions"));
const generate_pdf_1 = __importDefault(require("./routes/generate-pdf")); // Assuming you renamed it to .tsx
const app = (0, express_1.default)();
app.use(express_1.default.json());
// Use the routes
app.use('/mermaid', mermaid_1.default);
app.use('/prose-class', prose_class_1.default);
app.use('/validate-mermaid', validate_mermaid_1.default);
app.use('/mermaid-dimensions', mermaid_dimensions_1.default);
app.use('/generate-pdf', generate_pdf_1.default);
const PORT = process.env.PORT || 3003;
const httpsOptions = {
    key: fs_1.default.readFileSync(path_1.default.join(__dirname, '../localhost+2-key.pem')),
    cert: fs_1.default.readFileSync(path_1.default.join(__dirname, '../localhost+2.pem')),
};
https_1.default.createServer(httpsOptions, app).listen(PORT, () => __awaiter(void 0, void 0, void 0, function* () {
    logger_1.default.info(`Server is running on port ${PORT} with HTTPS`);
}));
process.on('exit', () => __awaiter(void 0, void 0, void 0, function* () {
    // Clean up resources if necessary
    logger_1.default.info('Server is shutting down');
}));
