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
    const { code } = req.body;
    if (!code) {
        logger_1.default.warn('Mermaid code is required');
        return res.status(400).send('Mermaid code is required');
    }
    try {
        const cluster = yield (0, cluster_1.launchCluster)();
        const generateSvg = (_a) => __awaiter(void 0, [_a], void 0, function* ({ page, data: { theme, code } }) {
            yield page.setContent(`
        <!DOCTYPE html>
        <html>
        <body>
        <div class="mermaid">${code}</div>
        <script type="module">
          import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@9/dist/mermaid.esm.min.mjs';
          mermaid.initialize({ startOnLoad: true, theme: '${theme}' });
        </script>
        </body>
        </html>
      `);
            yield page.waitForSelector('.mermaid > svg', { timeout: 3000 });
            return yield page.$eval('.mermaid', (el) => el.innerHTML);
        });
        const lightSvg = yield cluster.execute({ theme: 'default', code }, generateSvg);
        const darkSvg = yield cluster.execute({ theme: 'dark', code }, generateSvg);
        logger_1.default.info('SVG generated successfully');
        res.json({ lightSvg, darkSvg });
    }
    catch (error) {
        logger_1.default.error(`Failed to generate SVG: ${error.message}`);
        res.status(500).send(`Failed to generate SVG: ${error.message}`);
    }
}));
exports.default = router;
