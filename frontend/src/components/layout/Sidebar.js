"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var react_1 = require("react");
var react_router_dom_1 = require("react-router-dom");
var helpers_1 = require("../../utils/helpers");
var lucide_react_1 = require("lucide-react");
var react_2 = require("react");
var Sidebar = function () {
    var _a = (0, react_2.useState)(false), isOpen = _a[0], setIsOpen = _a[1];
    var location = (0, react_router_dom_1.useLocation)();
    var navigation = [
        {
            name: 'Dashboard',
            href: '/',
            icon: lucide_react_1.BarChart3,
        },
        {
            name: 'Upload',
            href: '/upload',
            icon: lucide_react_1.Upload,
        },
        {
            name: 'Search',
            href: '/search',
            icon: lucide_react_1.Search,
        },
        {
            name: 'Quiz',
            href: '/quiz',
            icon: lucide_react_1.Brain,
        },
    ];
    var isActive = function (href) {
        return location.pathname === href;
    };
    return (<>
            {/* Mobile menu button */}
            <button onClick={function () { return setIsOpen(!isOpen); }} className="fixed top-4 left-4 z-50 lg:hidden p-2 rounded-lg glass-effect">
                {isOpen ? (<lucide_react_1.X className="h-6 w-6 text-primary-900"/>) : (<lucide_react_1.Menu className="h-6 w-6 text-primary-900"/>)}
            </button>

            {/* Sidebar */}
            <div className={(0, helpers_1.cn)('fixed left-0 top-0 h-full w-64 glass-effect transform transition-transform duration-300 z-40', isOpen ? 'translate-x-0' : '-translate-x-full', 'lg:translate-x-0 lg:static lg:z-0')}>
                <div className="p-6">
                    <div className="flex items-center space-x-3 mb-8">
                        <div className="w-10 h-10 bg-gradient-to-br from-accent-500 to-accent-600 rounded-lg flex items-center justify-center">
                            <lucide_react_1.Brain className="h-6 w-6 text-white"/>
                        </div>
                        <h2 className="text-xl font-bold text-primary-900">Menu</h2>
                    </div>

                    <nav className="space-y-2">
                        {navigation.map(function (item) { return (<react_router_dom_1.NavLink key={item.name} to={item.href} onClick={function () { return setIsOpen(false); }} className={function (_a) {
                var isActive = _a.isActive;
                return (0, helpers_1.cn)('flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200', isActive
                    ? 'bg-accent-500/20 text-accent-500 border-r-2 border-accent-500'
                    : 'text-primary-700 hover:bg-primary-200/20');
            }}>
                                <item.icon className="h-5 w-5"/>
                                <span className="font-medium">{item.name}</span>
                            </react_router_dom_1.NavLink>); })}
                    </nav>
                </div>
            </div>

            {/* Overlay for mobile */}
            {isOpen && (<div className="fixed inset-0 bg-primary-900/50 z-30 lg:hidden" onClick={function () { return setIsOpen(false); }}/>)}
        </>);
};
exports.default = Sidebar;
