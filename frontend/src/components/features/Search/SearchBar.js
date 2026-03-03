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
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
var react_1 = require("react");
var useUser_1 = require("../../../hooks/useUser");
var useApi_1 = require("../../../hooks/useApi");
var api_1 = require("../../../services/api");
var Card_1 = require("../../../components/ui/Card");
var Input_1 = require("../../../components/ui/Input");
var Button_1 = require("../../../components/ui/Button");
var Badge_1 = require("../../../components/ui/Badge");
var lucide_react_1 = require("lucide-react"); // Removed unused Loader2
var react_hot_toast_1 = require("react-hot-toast");
var SearchBar = function () {
    var addXp = (0, useUser_1.useUser)().addXp;
    var _a = (0, useApi_1.useApi)(), loading = _a.loading, execute = _a.execute;
    var _b = (0, react_1.useState)(''), query = _b[0], setQuery = _b[1];
    var _c = (0, react_1.useState)(null), results = _c[0], setResults = _c[1];
    var handleSearch = function (e) { return __awaiter(void 0, void 0, void 0, function () {
        return __generator(this, function (_a) {
            e.preventDefault();
            if (!query.trim()) {
                react_hot_toast_1.default.error('Please enter a search query');
                return [2 /*return*/];
            }
            execute(function () { return api_1.apiService.searchDocuments(query, 5); }, function (response) {
                setResults(response);
                addXp(response.xpGained);
                react_hot_toast_1.default.success("Found ".concat(response.results.length, " results! +").concat(response.xpGained, " XP"));
            });
            return [2 /*return*/];
        });
    }); };
    return (<div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold text-primary-900 mb-2">Search Documents</h2>
                <p className="text-primary-600">
                    Find relevant information from your uploaded documents using AI-powered search
                </p>
            </div>

            {/* Search Form */}
            <Card_1.default variant="glass" className="p-6">
                <form onSubmit={handleSearch} className="space-y-4">
                    <div className="flex gap-4">
                        <Input_1.default placeholder="Ask anything about your documents..." value={query} onChange={function (e) { return setQuery(e.target.value); }} variant="glass" className="flex-1" icon={<lucide_react_1.Search className="h-5 w-5"/>}/>
                        <Button_1.default type="submit" variant="accent" loading={loading} icon={<lucide_react_1.Search className="h-5 w-5"/>}>
                            Search
                        </Button_1.default>
                    </div>

                    <div className="flex items-center justify-between">
                        <p className="text-sm text-primary-600">
                            Use natural language to search through all your documents
                        </p>
                        <Badge_1.default variant="accent">+2 XP per search</Badge_1.default>
                    </div>
                </form>
            </Card_1.default>

            {/* Search Results */}
            {results && (<Card_1.default variant="glass" className="p-6">
                    <div className="mb-6">
                        <h3 className="text-xl font-semibold text-primary-900 mb-2">
                            Search Results
                        </h3>
                        <p className="text-primary-600">
                            Found {results.results.length} results for "{results.query}"
                        </p>
                    </div>

                    <div className="space-y-4">
                        {results.results.map(function (result, index) { return (<SearchResultItem key={index} result={result}/>); })}
                    </div>

                    {results.results.length === 0 && (<div className="text-center py-8">
                            <lucide_react_1.FileText className="h-12 w-12 text-primary-400 mx-auto mb-4"/>
                            <p className="text-primary-600">No results found</p>
                            <p className="text-primary-500 text-sm mt-2">
                                Try different keywords or upload more documents
                            </p>
                        </div>)}
                </Card_1.default>)}

            {/* Search Tips */}
            <Card_1.default variant="glass" className="p-6">
                <h3 className="text-lg font-semibold text-primary-900 mb-3">
                    Search Tips
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <p className="text-primary-900 font-medium">Use natural language</p>
                        <p className="text-primary-600 text-sm">
                            "What is machine learning?" works better than "machine learning definition"
                        </p>
                    </div>

                    <div className="space-y-2">
                        <p className="text-primary-900 font-medium">Be specific</p>
                        <p className="text-primary-600 text-sm">
                            Include context and details for better results
                        </p>
                    </div>

                    <div className="space-y-2">
                        <p className="text-primary-900 font-medium">Ask questions</p>
                        <p className="text-primary-600 text-sm">
                            Frame your queries as questions for more precise answers
                        </p>
                    </div>

                    <div className="space-y-2">
                        <p className="text-primary-900 font-medium">Explore topics</p>
                        <p className="text-primary-600 text-sm">
                            Search for themes, concepts, and relationships
                        </p>
                    </div>
                </div>
            </Card_1.default>
        </div>);
};
var SearchResultItem = function (_a) {
    var result = _a.result;
    return (<Card_1.default variant="default" className="p-4">
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                    <lucide_react_1.FileText className="h-4 w-4 text-accent-500"/>
                    <Badge_1.default variant="accent" size="sm">
                        {result.source}
                    </Badge_1.default>
                    {result.page && (<Badge_1.default variant="default" size="sm">  {/* Changed from secondary to default */}
                            Page {result.page}
                        </Badge_1.default>)}
                </div>

                <Badge_1.default variant="success" size="sm">
                    {(result.score * 100).toFixed(0)}% match
                </Badge_1.default>
            </div>

            <p className="text-primary-900 leading-relaxed mb-3">
                {result.content}
            </p>

            <div className="flex items-center justify-between">
                <p className="text-sm text-primary-600">
                    Relevance: {(result.score * 100).toFixed(1)}%
                </p>
                <Button_1.default variant="ghost" size="sm">
                    <lucide_react_1.ExternalLink className="h-4 w-4 mr-1"/>
                    View Source
                </Button_1.default>
            </div>
        </Card_1.default>);
};
exports.default = SearchBar;
