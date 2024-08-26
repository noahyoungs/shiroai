"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ViewOnlyTitle = ViewOnlyTitle;
const jsx_runtime_1 = require("react/jsx-runtime");
const cn_1 = require("../../../utils/cn");
function ViewOnlyTitle({ title, classNames }) {
    return ((0, jsx_runtime_1.jsx)("div", { className: "border-b-medium border-transparent rounded-none", children: (0, jsx_runtime_1.jsx)("div", { className: (0, cn_1.cn)("pb-[8px] box-border text-4xl font-bold [overflow-wrap:anywhere]", classNames), children: title }) }));
}
