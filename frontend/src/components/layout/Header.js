"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var react_1 = require("react");
var useUser_1 = require("../../hooks/useUser");
var lucide_react_1 = require("lucide-react");
var Card_1 = require("../ui/Card");
var Header = function () {
    var user = (0, useUser_1.useUser)().user;
    return (<Card_1.default variant="glass" className="mb-6">
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                        <lucide_react_1.Brain className="h-8 w-8 text-accent-500"/>
                        <div>
                            <h1 className="text-2xl font-bold text-primary-900">
                                RAG Learning Platform
                            </h1>
                            <p className="text-sm text-primary-600">
                                Master knowledge through AI-powered learning
                            </p>
                        </div>
                    </div>
                </div>

                <div className="flex items-center space-x-6">
                    {/* XP Progress */}
                    <div className="flex items-center space-x-3">
                        <lucide_react_1.Zap className="h-5 w-5 text-accent-500"/>
                        <div>
                            <p className="text-sm font-semibold text-primary-900">
                                Level {user.level}
                            </p>
                            <div className="flex items-center space-x-2">
                                <div className="w-24 h-2 bg-primary-200 rounded-full overflow-hidden">
                                    <div className="h-full bg-gradient-to-r from-accent-500 to-accent-600 transition-all duration-500" style={{
            width: "".concat(((100 - user.xpToNextLevel) / 100) * 100, "%"),
        }}/>
                                </div>
                                <span className="text-xs text-primary-600">
                                    {100 - user.xpToNextLevel} XP
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Total XP */}
                    <div className="flex items-center space-x-2">
                        <lucide_react_1.Trophy className="h-5 w-5 text-warning"/>
                        <span className="font-semibold text-primary-900">
                            {user.totalXp} Total XP
                        </span>
                    </div>
                </div>
            </div>
        </Card_1.default>);
};
exports.default = Header;
