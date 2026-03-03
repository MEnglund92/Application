import React, { useEffect } from 'react'
import Card from '../../../components/ui/Card'
import Badge from '../../../components/ui/Badge'
import { apiService } from '../../../services/api'
import { useApi } from '../../../hooks/useApi'
import { SystemStats } from '../../../types'
import {
    FileText,
    Database,
    Cpu,
    HardDrive,
    Activity,
    Clock,
    Search,
} from 'lucide-react'

const DashboardView: React.FC = () => {
    const { loading, error, execute } = useApi()
    const [stats, setStats] = React.useState<SystemStats | null>(null)

    useEffect(() => {
        execute(
            () => apiService.getSystemStats(),
            (data) => setStats(data)
        )
    }, [execute])

    if (loading && !stats) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-500"></div>
            </div>
        )
    }

    if (error && !stats) {
        return (
            <Card variant="default" className="text-center p-8">
                <p className="text-danger">Error loading dashboard: {error}</p>
            </Card>
        )
    }

    if (!stats) {
        return null
    }

    const statCards = [
        {
            title: 'Documents',
            value: stats.documentsCount,
            icon: FileText,
            color: 'accent',
            change: '+2 today',
        },
        {
            title: 'Vector DB Size',
            value: `${stats.vectorDbSizeMb.toFixed(1)} MB`,
            icon: Database,
            color: 'success',
            change: '+0.5 MB',
        },
        {
            title: 'CPU Usage',
            value: `${stats.systemHealth.cpuPercent.toFixed(1)}%`,
            icon: Cpu,
            color: 'warning',
            change: '-2%',
        },
        {
            title: 'Memory Usage',
            value: `${stats.systemHealth.memoryPercent.toFixed(1)}%`,
            icon: HardDrive,
            color: 'danger',
            change: '+5%',
        },
    ]

    const getColorClasses = (color: string) => {
        const colors = {
            accent: 'text-accent-500',
            success: 'text-success',
            warning: 'text-warning',
            danger: 'text-danger',
        }
        return colors[color as keyof typeof colors] || 'text-primary-500'
    }

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold text-primary-900 mb-2">Dashboard</h2>
                <p className="text-primary-600">Monitor your RAG learning platform</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {statCards.map((stat, index) => (
                    <Card key={index} variant="glass" className="p-6">
                        <div className="flex items-center justify-between mb-4">
                            <stat.icon className={`h-8 w-8 ${getColorClasses(stat.color)}`} />
                            <Badge variant="success" size="sm">
                                {stat.change}
                            </Badge>
                        </div>
                        <h3 className="text-2xl font-bold text-primary-900 mb-1">
                            {stat.value}
                        </h3>
                        <p className="text-primary-600">{stat.title}</p>
                    </Card>
                ))}
            </div>

            {/* Recent Queries */}
            <Card variant="glass" className="p-6">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-2">
                        <Clock className="h-5 w-5 text-primary-600" />
                        <h3 className="text-xl font-semibold text-primary-900">
                            Recent Queries
                        </h3>
                    </div>
                    <Badge variant="accent">
                        {stats.lastQueries.length} queries
                    </Badge>
                </div>

                <div className="space-y-3">
                    {stats.lastQueries.map((query, index) => (
                        <div
                            key={index}
                            className="flex items-center justify-between p-3 rounded-lg bg-primary-100/30"
                        >
                            <div className="flex items-center space-x-3">
                                <Search className="h-4 w-4 text-primary-500" />
                                <span className="text-primary-900">{query.query}</span>
                            </div>
                            <span className="text-sm text-primary-600">
                                {new Date(query.timestamp).toLocaleTimeString()}
                            </span>
                        </div>
                    ))}
                </div>
            </Card>

            {/* System Activity */}
            <Card variant="glass" className="p-6">
                <div className="flex items-center space-x-2 mb-6">
                    <Activity className="h-5 w-5 text-primary-600" />
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
                            <div
                                className="h-full bg-gradient-to-r from-accent-500 to-accent-600 transition-all duration-500"
                                style={{ width: `${stats.systemHealth.cpuPercent}%` }}
                            />
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
                            <div
                                className="h-full bg-gradient-to-r from-warning to-warning/80 transition-all duration-500"
                                style={{ width: `${stats.systemHealth.memoryPercent}%` }}
                            />
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
                            <div
                                className="h-full bg-gradient-to-r from-success to-success/80 transition-all duration-500"
                                style={{ width: `${stats.systemHealth.diskPercent}%` }}
                            />
                        </div>
                    </div>
                </div>
            </Card>
        </div>
    )
}

export default DashboardView
