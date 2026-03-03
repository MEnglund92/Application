"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var react_1 = require("react");
var react_router_dom_1 = require("react-router-dom");
var Layout_1 = require("./components/layout/Layout");
var DashboardView_1 = require("./components/features/Dashboard/DashboardView");
var UploadZone_1 = require("./components/features/Upload/UploadZone");
var SearchBar_1 = require("./components/features/Search/SearchBar");
var QuizComponent_1 = require("./components/features/Quiz/QuizComponent");
function App() {
    return (<div className="min-h-screen bg-gradient-to-br from-primary-50 via-primary-100 to-primary-50">
            <Layout_1.default>
                <react_router_dom_1.Routes>
                    <react_router_dom_1.Route path="/" element={<DashboardView_1.default />}/>
                    <react_router_dom_1.Route path="/upload" element={<UploadZone_1.default />}/>
                    <react_router_dom_1.Route path="/search" element={<SearchBar_1.default />}/>
                    <react_router_dom_1.Route path="/quiz" element={<QuizComponent_1.default />}/>
                </react_router_dom_1.Routes>
            </Layout_1.default>
        </div>);
}
exports.default = App;
