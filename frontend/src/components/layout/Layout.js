"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var react_1 = require("react");
var Sidebar_1 = require("./Sidebar");
var Header_1 = require("./Header");
var Layout = function (_a) {
    var children = _a.children;
    return (<div className="min-h-screen flex">
            <Sidebar_1.default />
            <div className="flex-1 lg:ml-0">
                <div className="p-6 lg:p-8">
                    <Header_1.default />
                    <main>{children}</main>
                </div>
            </div>
        </div>);
};
exports.default = Layout;
