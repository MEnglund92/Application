"use strict";
var __rest = (this && this.__rest) || function (s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
        t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function")
        for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
            if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
                t[p[i]] = s[p[i]];
        }
    return t;
};
Object.defineProperty(exports, "__esModule", { value: true });
var react_1 = require("react");
var helpers_1 = require("../../utils/helpers");
var lucide_react_1 = require("lucide-react");
var Button = function (_a) {
    var _b = _a.variant, variant = _b === void 0 ? 'primary' : _b, _c = _a.size, size = _c === void 0 ? 'md' : _c, _d = _a.loading, loading = _d === void 0 ? false : _d, icon = _a.icon, children = _a.children, className = _a.className, disabled = _a.disabled, props = __rest(_a, ["variant", "size", "loading", "icon", "children", "className", "disabled"]);
    var baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2';
    var variants = {
        primary: 'bg-accent-500 hover:bg-accent-600 text-white focus:ring-accent-500 gaming-button neon-glow',
        secondary: 'bg-primary-200 hover:bg-primary-300 text-primary-900 border border-primary-300',
        accent: 'bg-gradient-to-r from-accent-500 to-accent-600 hover:from-accent-600 hover:to-accent-700 text-white',
        danger: 'bg-danger hover:bg-red-600 text-white focus:ring-danger',
        ghost: 'bg-transparent hover:bg-primary-200/20 text-primary-700 border border-primary-300',
    };
    var sizes = {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg',
    };
    return (<button className={(0, helpers_1.cn)(baseClasses, variants[variant], sizes[size], (loading || disabled) && 'opacity-50 cursor-not-allowed', className)} disabled={loading || disabled} {...props}>
            {loading && <lucide_react_1.Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4"/>}
            {icon && !loading && <span className="mr-2">{icon}</span>}
            {children}
        </button>);
};
exports.default = Button;
