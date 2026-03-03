"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var react_1 = require("react");
var helpers_1 = require("../../utils/helpers");
var Badge = function (_a) {
    var children = _a.children, _b = _a.variant, variant = _b === void 0 ? 'default' : _b, _c = _a.size, size = _c === void 0 ? 'md' : _c, className = _a.className;
    var baseClasses = 'inline-flex items-center justify-center font-semibold rounded-full';
    var variants = {
        default: 'bg-primary-200 text-primary-900',
        success: 'bg-success/20 text-success',
        warning: 'bg-warning/20 text-warning',
        danger: 'bg-danger/20 text-danger',
        accent: 'bg-accent-500/20 text-accent-500',
    };
    var sizes = {
        sm: 'px-2 py-0.5 text-xs',
        md: 'px-3 py-1 text-sm',
        lg: 'px-4 py-1.5 text-base',
    };
    return (<span className={(0, helpers_1.cn)(baseClasses, variants[variant], sizes[size], className)}>
            {children}
        </span>);
};
exports.default = Badge;
