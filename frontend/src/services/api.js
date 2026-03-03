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
exports.apiService = void 0;
var axios_1 = require("axios");
var API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
var api = axios_1.default.create({
    baseURL: API_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});
// Request interceptor
api.interceptors.request.use(function (config) {
    var _a;
    console.log("API Request: ".concat((_a = config.method) === null || _a === void 0 ? void 0 : _a.toUpperCase(), " ").concat(config.url));
    return config;
}, function (error) {
    return Promise.reject(error);
});
// Response interceptor
api.interceptors.response.use(function (response) {
    return response.data;
}, function (error) {
    var _a, _b;
    console.error('API Error:', ((_a = error.response) === null || _a === void 0 ? void 0 : _a.data) || error.message);
    return Promise.reject(((_b = error.response) === null || _b === void 0 ? void 0 : _b.data) || error);
});
exports.apiService = {
    // Upload
    uploadDocument: function (file) { return __awaiter(void 0, void 0, void 0, function () {
        var formData;
        return __generator(this, function (_a) {
            formData = new FormData();
            formData.append('file', file);
            return [2 /*return*/, api.post('/api/v1/upload', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                })];
        });
    }); },
    // Search
    searchDocuments: function (query_1) {
        var args_1 = [];
        for (var _i = 1; _i < arguments.length; _i++) {
            args_1[_i - 1] = arguments[_i];
        }
        return __awaiter(void 0, __spreadArray([query_1], args_1, true), void 0, function (query, maxResults) {
            if (maxResults === void 0) { maxResults = 5; }
            return __generator(this, function (_a) {
                return [2 /*return*/, api.post('/api/v1/search', {
                        query: query,
                        maxResults: maxResults,
                    })];
            });
        });
    },
    // Quiz
    generateQuiz: function () { return __awaiter(void 0, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, api.get('/api/v1/quiz')];
        });
    }); },
    submitQuiz: function (answers) { return __awaiter(void 0, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, api.post('/api/v1/quiz/submit', answers)];
        });
    }); },
    // Stats
    getSystemStats: function () { return __awaiter(void 0, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, api.get('/api/v1/stats')];
        });
    }); },
    // Health
    healthCheck: function () { return __awaiter(void 0, void 0, void 0, function () {
        return __generator(this, function (_a) {
            return [2 /*return*/, api.get('/health')];
        });
    }); },
};
