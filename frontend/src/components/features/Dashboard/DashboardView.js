"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var react_1 = require("react");
var Card_1 = require("../../../components/ui/Card");
var Badge_1 = require("../../../components/ui/Badge");
var api_1 = require("../../../services/api");
var useApi_1 = require("../../../hooks/useApi");
var lucide_react_1 = require("lucide-react");
var DashboardView = function () {
    var _a = (0, useApi_1.useApi)(), loading = _a.loading, error = _a.error, execute = _a.execute;
    var _b = react_1.default.useState(null), stats = _b[0], setStats = _b[1];
    (0, react_1.useEffect)(function () {
        execute(function () { return api_1.apiService.getSystemStats(); }, function (data) { return setStats(data); });
    }, [execute]);
    if (loading && !stats) {
        return (<div className="flex items-center justify-center min-h-[400px]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-500"></div>
            </div>);
    }
    if (error && !stats) {
        return (<Card_1.default variant="danger" className="text-center p-8">
                <p className="text-danger">Error loading dashboard: {error}</p>
            </Card_1.default>);
    }
    if (!stats) {
        return null;
    }
    var statCards = [
        {
            title: 'Documents',
            value: stats.documentsCount,
            icon: lucide_react_1.FileText,
            color: 'accent',
            change: '+2 today',
        },
        {
            title: 'Vector DB Size',
            value: "".concat(stats.vectorDbSizeMb.toFixed(1), " MB"),
            icon: lucide_react_1.Database,
            color: 'success',
            change: '+0.5 MB',
        },
        {
            title: 'CPU Usage',
            value: "".concat(stats.systemHealth.cpuPercent.toFixed(1), "%"),
            icon: lucide_react_1.Cpu,
            color: 'warning',
            change: '-2%',
        },
        {
            title: 'Memory Usage',
            value: "".concat(stats.systemHealth.memoryPercent.toFixed(1), "%"),
            icon: lucide_react_1.HardDrive,
            color: 'danger',
            change: '+5%',
        },
    ];
    var getColorClasses = function (color) {
        var colors = {
            accent: 'text-accent-500',
            success: 'text-success',
            warning: 'text-warning',
            danger: 'text-danger',
        };
        return colors[color] || 'text-primary-500';
    };
    return (<div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold text-primary-900 mb-2">Dashboard</h2>
                <p className="text-primary-600">Monitor your RAG learning platform</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {statCards.map(function (stat, index) { return (<Card_1.default key={index} variant="glass" className="p-6">
                        <div className="flex items-center justify-between mb-4">
                            <stat.icon className={"h-8 w-8 ".concat(getColorClasses(stat.color))}/>
                            <Badge_1.default variant="success" size="sm">
                                {stat.change}
                            </Badge_1.default>
                        </div>
                        <h3 className="text-2xl font-bold text-primary-900 mb-1">
                            {stat.value}
                        </h3>
                        <p className="text-primary-600">{stat.title}</p>
                    </Card_1.default>); })}
            </div>

            {/* Recent Queries */}
            <Card_1.default variant="glass" className="p-6">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-2">
                        <lucide_react_1.Clock className="h-5 w-5 text-primary-600"/>
                        <h3 className="text-xl font-semibold text-primary-900">
                            Recent Queries
                        </h3>
                    </div>
                    <Badge_1.default variant="accent">
                        {stats.lastQueries.length} queries
                    </Badge_1.default>
                </div>

                <div className="space-y-3">
                    {stats.lastQueries.map(function (query, index) { return (<div key={index} className="flex items-center justify-between p-3 rounded-lg bg-primary-100/30">
                            <div className="flex items-center space-x-3">
                                <Search className="h-4 w-4 text-primary-500"/>
                                <span className="text-primary-900">{query.query}</span>
                            </div>
                            <span className="text-sm text-primary-600">
                                {new Date(query.timestamp).toLocaleTimeString()}
                            </span>
                        </div>); })}
                </div>
            </Card_1.default>

            {/* System Activity */}
            <Card_1.default variant="glass" className="p-6">
                <div className="flex items-center space-x-2 mb-6">
                    <lucide_react_1.Activity className="h-5 w-5 text-primary-600"/>
                    <h3 className="text-xl font-semibold text-primary-900">
                        System Activity
                    </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-primary-600">CPU Usage</span>
                            <span className="text-primary-900 font-semibold">
                                {stats.systemHealth.cpuPercent.toFixed(1)}%
                            </span>
                        </div>
                        <div className="w-full h-3 bg-primary-200 rounded-full overflow-hidden">
                            <div className="h-full bg-gradient-to-r from-accent-500 to-accent-600 transition-all duration-500" style={{ width: "".concat(stats.systemHealth.cpuPercent, "%") }}/>
                        </div>
                    </div>

                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-primary-600">Memory Usage</span>
                            <span className="text-primary-900 font-semibold">
                                {stats.systemHealth.memoryPercent.toFixed(1)}%
                            </span>
                        </div>
                        <div className="w-full h-3 bg-primary-200 rounded-full overflow-hidden">
                            <div className="h-full bg-gradient-to-r from-warning to-warning/80 transition-all duration-500" style={{ width: "".concat(stats.systemHealth.memoryPercent, "%") }}/>
                        </div>
                    </div>

                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-primary-600">Disk Usage</span>
                            <span className="text-primary-900 font-semibold">
                                {stats.systemHealth.diskPercent.toFixed(1)}%
                            </span>
                        </div>
                        <div className="w-full h-3 bg-primary-200 rounded-full overflow-hidden">
                            <div className="h-full bg-gradient-to-r from-success to-success/80 transition-all duration-500" style={{ width: "".concat(stats.systemHealth.diskPercent, "%") }}/>
                        </div>
                    </div>
                </div>
            </Card_1.default>
        </div>);
};
exports.default = DashboardView;
