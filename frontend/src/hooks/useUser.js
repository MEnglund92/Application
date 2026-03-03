"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.useUser = void 0;
var react_1 = require("react");
var STORAGE_KEY = 'rag-learning-user';
var useUser = function () {
    var _a = (0, react_1.useState)(function () {
        var stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            return JSON.parse(stored);
        }
        return {
            level: 1,
            totalXp: 0,
            xpToNextLevel: 100,
            achievements: [],
        };
    }), user = _a[0], setUser = _a[1];
    var addXp = function (amount) {
        setUser(function (prev) {
            var newTotalXp = prev.totalXp + amount;
            var newLevel = Math.floor(newTotalXp / 100) + 1;
            var newXpToNextLevel = (newLevel * 100) - newTotalXp;
            var updatedUser = __assign(__assign({}, prev), { totalXp: newTotalXp, level: newLevel, xpToNextLevel: newXpToNextLevel });
            localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedUser));
            return updatedUser;
        });
    };
    var resetUser = function () {
        var defaultUser = {
            level: 1,
            totalXp: 0,
            xpToNextLevel: 100,
            achievements: [],
        };
        setUser(defaultUser);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(defaultUser));
    };
    return {
        user: user,
        addXp: addXp,
        resetUser: resetUser,
    };
};
exports.useUser = useUser;
