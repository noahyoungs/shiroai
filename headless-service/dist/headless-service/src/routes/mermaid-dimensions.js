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
        const getDimensions = (_a) => __awaiter(void 0, [_a], void 0, function* ({ page, data: { code } }) {
            yield page.setContent(`
        <!DOCTYPE html>
        <html>
        <body>
        <div class="mermaid">${code}</div>
        <script type="module">
          import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@9/dist/mermaid.esm.min.mjs';
          mermaid.initialize({ startOnLoad: true });
        </script>
        </body>
        </html>
      `);
            yield page.waitForSelector('.mermaid > svg', { timeout: 3000 });
            const dimensions = yield page.evaluate(() => {
                const svg = document.querySelector('.mermaid > svg');
                const { width, height } = (svg === null || svg === void 0 ? void 0 : svg.getBoundingClientRect()) || { width: 0, height: 0 };
                return { width, height };
            });
            return dimensions;
        });
        const dimensions = yield cluster.execute({ code }, getDimensions);
        logger_1.default.info('Dimensions retrieved successfully');
        res.json(dimensions);
    }
    catch (error) {
        logger_1.default.error(`Failed to get dimensions: ${error.message}`);
        res.status(500).send(`Failed to get dimensions: ${error.message}`);
    }
}));
exports.default = router;
