"use strict";
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
Object.defineProperty(exports, "__esModule", { value: true });
var react_1 = require("react");
var react_dropzone_1 = require("react-dropzone");
var useUser_1 = require("../../../hooks/useUser");
var useApi_1 = require("../../../hooks/useApi");
var api_1 = require("../../../services/api");
var Card_1 = require("../../../components/ui/Card");
var Badge_1 = require("../../../components/ui/Badge");
var lucide_react_1 = require("lucide-react");
var react_hot_toast_1 = require("react-hot-toast");
var UploadZone = function () {
    var addXp = (0, useUser_1.useUser)().addXp;
    var _a = (0, useApi_1.useApi)(), loading = _a.loading, execute = _a.execute;
    var _b = (0, react_1.useState)([]), uploadedFiles = _b[0], setUploadedFiles = _b[1];
    var onDrop = (0, react_1.useCallback)(function (acceptedFiles) {
        acceptedFiles.forEach(function (file) {
            if (file.size > 10 * 1024 * 1024) {
                react_hot_toast_1.default.error('File size must be less than 10MB');
                return;
            }
            execute(function () { return api_1.apiService.uploadDocument(file); }, function (response) {
                setUploadedFiles(function (prev) { return __spreadArray([response], prev, true); });
                addXp(response.xpGained);
                react_hot_toast_1.default.success("Uploaded ".concat(file.name, "! +").concat(response.xpGained, " XP"));
            });
        });
    }, [execute, addXp]);
    var _c = (0, react_dropzone_1.useDropzone)({
        onDrop: onDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'text/plain': ['.txt'],
        },
        maxSize: 10 * 1024 * 1024, // 10MB
        multiple: true,
    }), getRootProps = _c.getRootProps, getInputProps = _c.getInputProps, isDragActive = _c.isDragActive;
    return (<div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold text-primary-900 mb-2">Upload Documents</h2>
                <p className="text-primary-600">
                    Add PDF or text files to build your knowledge base
                </p>
            </div>

            {/* Upload Area */}
            <Card_1.default variant="glass" className="p-8">
                <div {...getRootProps()} className={"\n            border-2 border-dashed rounded-xl p-12 text-center cursor-pointer\n            transition-all duration-200 hover:border-accent-500\n            ".concat(isDragActive ? 'border-accent-500 bg-accent-500/10' : 'border-primary-300', "\n          ")}>
                    <input {...getInputProps()}/>

                    <div className="flex flex-col items-center space-y-4">
                        <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
                            {loading ? (<div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-500"></div>) : (<lucide_react_1.Upload className="h-8 w-8 text-primary-600"/>)}
                        </div>

                        <div>
                            <p className="text-lg font-semibold text-primary-900 mb-1">
                                {isDragActive
            ? 'Drop your files here'
            : 'Drag & drop your files here'}
                            </p>
                            <p className="text-primary-600">
                                or click to browse (PDF, TXT up to 10MB)
                            </p>
                        </div>

                        <Badge_1.default variant="accent">+10 XP per document</Badge_1.default>
                    </div>
                </div>
            </Card_1.default>

            {/* Uploaded Files */}
            {uploadedFiles.length > 0 && (<Card_1.default variant="glass" className="p-6">
                    <h3 className="text-xl font-semibold text-primary-900 mb-4">
                        Recently Uploaded
                    </h3>

                    <div className="space-y-3">
                        {uploadedFiles.map(function (file, index) { return (<div key={index} className="flex items-center justify-between p-4 rounded-lg bg-primary-100/30">
                                <div className="flex items-center space-x-3">
                                    <div className="w-10 h-10 bg-success/20 rounded-full flex items-center justify-center">
                                        <lucide_react_1.CheckCircle className="h-5 w-5 text-success"/>
                                    </div>
                                    <div>
                                        <p className="font-medium text-primary-900">{file.filename}</p>
                                        <p className="text-sm text-primary-600">
                                            {file.chunksProcessed} chunks processed
                                        </p>
                                    </div>
                                </div>

                                <div className="flex items-center space-x-2">
                                    <Badge_1.default variant="success">+{file.xpGained} XP</Badge_1.default>
                                </div>
                            </div>); })}
                    </div>
                </Card_1.default>)}

            {/* Instructions */}
            <Card_1.default variant="glass" className="p-6">
                <h3 className="text-lg font-semibold text-primary-900 mb-3">
                    How it works
                </h3>

                <div className="space-y-3">
                    <div className="flex items-start space-x-3">
                        <div className="w-8 h-8 bg-accent-500/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                            <span className="text-accent-500 font-bold text-sm">1</span>
                        </div>
                        <div>
                            <p className="text-primary-900 font-medium">Upload your documents</p>
                            <p className="text-primary-600 text-sm">
                                Support for PDF and text files with automatic text extraction
                            </p>
                        </div>
                    </div>

                    <div className="flex items-start space-x-3">
                        <div className="w-8 h-8 bg-accent-500/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                            <span className="text-accent-500 font-bold text-sm">2</span>
                        </div>
                        <div>
                            <p className="text-primary-900 font-medium">Text is processed</p>
                            <p className="text-primary-600 text-sm">
                                Documents are chunked and embedded for semantic search
                            </p>
                        </div>
                    </div>

                    <div className="flex items-start space-x-3">
                        <div className="w-8 h-8 bg-accent-500/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                            <span className="text-accent-500 font-bold text-sm">3</span>
                        </div>
                        <div>
                            <p className="text-primary-900 font-medium">Ready for search</p>
                            <p className="text-primary-600 text-sm">
                                Use the search feature to find relevant information instantly
                            </p>
                        </div>
                    </div>
                </div>
            </Card_1.default>
        </div>);
};
exports.default = UploadZone;
