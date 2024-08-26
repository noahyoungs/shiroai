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
const marked_1 = require("marked");
const path_1 = __importDefault(require("path"));
const router = (0, express_1.Router)();
router.post('/', (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { markdown, title } = req.body;
    if (!markdown) {
        logger_1.default.warn('Markdown is required');
        return res.status(400).send('Markdown is required');
    }
    if (!title) {
        logger_1.default.warn('Title is required');
        return res.status(400).send('Title is required');
    }
    try {
        const cluster = yield (0, cluster_1.launchCluster)();
        const determineProseClass = (_a) => __awaiter(void 0, [_a], void 0, function* ({ page, data: { markdown, title } }) {
            const html = marked_1.marked.parse(markdown);
            yield page.setViewport({ width: 960, height: 540 });
            yield page.setContent(`
        <html>
        <head>
        <script src="https://cdn.tailwindcss.com?plugins=typography"></script>
        </head>
        <body>
        <div class="p-12 pb-0 flex flex-col relative text-foreground dark:bg-foreground/10 bg-foreground/5 box-border bg-content1 outline-none shadow-medium rounded-large w-full flex-none aspect-video overflow-scroll">
          <div class="flex-none">
            <div class="border-b-medium border-transparent rounded-none">
              <div class="pb-[8px] box-border text-4xl font-bold [overflow-wrap:anywhere]">
                ${title}
              </div>
            </div>
          </div>
          <div class="flex-auto"></div>
          <div class="slide-content flex flex-col justify-center w-full max-w-none prose">
            ${html}
          </div>
          <div class="flex-auto"></div>
        </div>
        </body>
        </html>
      `);
            const contentHeight = yield page.evaluate(() => {
                const content = document.querySelector('.slide-content');
                return content ? content.clientHeight : 0;
            });
            let proseClass = 'prose-2xl';
            if (contentHeight >= 570) {
                proseClass = 'overheight';
            }
            else if (contentHeight >= 500) {
                proseClass = 'prose-xs';
            }
            else if (contentHeight >= 400) {
                proseClass = 'prose-sm';
            }
            else if (contentHeight >= 375) {
                proseClass = 'prose-base';
            }
            else if (contentHeight >= 300) {
                proseClass = 'prose-lg';
            }
            else if (contentHeight > 190) {
                proseClass = 'prose-xl';
            }
            const screenshotPath = path_1.default.join(__dirname, '..', '..', 'screenshots', `screenshot-${Date.now()}.png`);
            yield page.screenshot({ path: screenshotPath });
            return { proseClass, screenshotPath };
        });
        const { proseClass, screenshotPath } = yield cluster.execute({ markdown, title }, determineProseClass);
        logger_1.default.info('Prose class determined and screenshot taken');
        res.json({ proseClass, screenshotPath });
    }
    catch (error) {
        logger_1.default.error(`Failed to determine prose class: ${error.message}`);
        res.status(500).send(`Failed to determine prose class: ${error.message}`);
    }
}));
exports.default = router;
