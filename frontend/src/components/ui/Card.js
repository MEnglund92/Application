"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var react_1 = require("react");
var helpers_1 = require("../../utils/helpers");
var Card = function (_a) {
    var children = _a.children, className = _a.className, _b = _a.variant, variant = _b === void 0 ? 'default' : _b, _c = _a.padding, padding = _c === void 0 ? 'md' : _c;
    var baseClasses = 'rounded-xl transition-all duration-300';
    var variants = {
        default: 'bg-primary-100/50 border border-primary-200/30',
        glass: 'glass-effect',
        neon: 'bg-primary-100/70 border border-accent-500/30 neon-glow',
    };
    var paddings = {
        none: '',
        sm: 'p-3',
        md: 'p-5',
        lg: 'p-7',
    };
    return (<div className={(0, helpers_1.cn)(baseClasses, variants[variant], paddings[padding], className)}>
            {children}
        </div>);
};
exports.default = Card;
