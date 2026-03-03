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
var Input = function (_a) {
    var _b = _a.variant, variant = _b === void 0 ? 'default' : _b, error = _a.error, icon = _a.icon, className = _a.className, props = __rest(_a, ["variant", "error", "icon", "className"]);
    var baseClasses = 'w-full rounded-lg border transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2';
    var variants = {
        default: 'bg-primary-100/50 border-primary-300 focus:border-accent-500 focus:ring-accent-500 text-primary-900 placeholder-primary-500',
        glass: 'glass-effect border-primary-300/30 focus:border-accent-500 focus:ring-accent-500 text-primary-900 placeholder-primary-500',
        neon: 'bg-primary-100/70 border-accent-500/30 focus:border-accent-500 focus:ring-accent-500 text-primary-900 placeholder-primary-500 neon-glow',
    };
    return (<div className="relative">
            {icon && (<div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary-500">
                    {icon}
                </div>)}
            <input className={(0, helpers_1.cn)(baseClasses, variants[variant], icon && 'pl-10', error && 'border-danger focus:ring-danger', className)} {...props}/>
            {error && (<p className="mt-1 text-sm text-danger">{error}</p>)}
        </div>);
};
exports.default = Input;
