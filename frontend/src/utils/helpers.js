"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.cn = exports.truncateText = exports.formatTimeAgo = exports.formatBytes = void 0;
var formatBytes = function (bytes, decimals) {
    if (decimals === void 0) { decimals = 2; }
    if (bytes === 0)
        return '0 Bytes';
    var k = 1024;
    var dm = decimals < 0 ? 0 : decimals;
    var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    var i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};
exports.formatBytes = formatBytes;
var formatTimeAgo = function (timestamp) {
    var date = new Date(timestamp);
    var now = new Date();
    var seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    if (seconds < 60)
        return 'just now';
    if (seconds < 3600)
        return "".concat(Math.floor(seconds / 60), "m ago");
    if (seconds < 86400)
        return "".concat(Math.floor(seconds / 3600), "h ago");
    return "".concat(Math.floor(seconds / 86400), "d ago");
};
exports.formatTimeAgo = formatTimeAgo;
var truncateText = function (text, maxLength) {
    if (text.length <= maxLength)
        return text;
    return text.substring(0, maxLength) + '...';
};
exports.truncateText = truncateText;
var cn = function () {
    var inputs = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        inputs[_i] = arguments[_i];
    }
    return inputs.filter(Boolean).join(' ');
};
exports.cn = cn;
