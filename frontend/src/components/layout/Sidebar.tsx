import React from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { cn } from '../../utils/helpers'
import {
    BarChart3,
    Upload,
    Search,
    Brain,
    Menu,
    X,
} from 'lucide-react'
import { useState } from 'react'

const Sidebar: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false)
    const location = useLocation()

    const navigation = [
        {
            name: 'Dashboard',
            href: '/',
            icon: BarChart3,
        },
        {
            name: 'Upload',
            href: '/upload',
            icon: Upload,
        },
        {
            name: 'Search',
            href: '/search',
            icon: Search,
        },
        {
            name: 'Quiz',
            href: '/quiz',
            icon: Brain,
        },
    ]

    const isActive = (href: string) => {
        return location.pathname === href
    }

    return (
        <>
            {/* Mobile menu button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="fixed top-4 left-4 z-50 lg:hidden p-2 rounded-lg glass-effect"
            >
                {isOpen ? (
                    <X className="h-6 w-6 text-primary-900" />
                ) : (
                    <Menu className="h-6 w-6 text-primary-900" />
                )}
            </button>

            {/* Sidebar */}
            <div
                className={cn(
                    'fixed left-0 top-0 h-full w-64 glass-effect transform transition-transform duration-300 z-40',
                    isOpen ? 'translate-x-0' : '-translate-x-full',
                    'lg:translate-x-0 lg:static lg:z-0'
                )}
            >
                <div className="p-6">
                    <div className="flex items-center space-x-3 mb-8">
                        <div className="w-10 h-10 bg-gradient-to-br from-accent-500 to-accent-600 rounded-lg flex items-center justify-center">
                            <Brain className="h-6 w-6 text-white" />
                        </div>
                        <h2 className="text-xl font-bold text-primary-900">Menu</h2>
                    </div>

                    <nav className="space-y-2">
                        {navigation.map((item) => (
                            <NavLink
                                key={item.name}
                                to={item.href}
                                onClick={() => setIsOpen(false)}
                                className={({ isActive }) =>
                                    cn(
                                        'flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200',
                                        isActive
                                            ? 'bg-accent-500/20 text-accent-500 border-r-2 border-accent-500'
                                            : 'text-primary-700 hover:bg-primary-200/20'
                                    )
                                }
                            >
                                <item.icon className="h-5 w-5" />
                                <span className="font-medium">{item.name}</span>
                            </NavLink>
                        ))}
                    </nav>
                </div>
            </div>

            {/* Overlay for mobile */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-primary-900/50 z-30 lg:hidden"
                    onClick={() => setIsOpen(false)}
                />
            )}
        </>
    )
}

export default Sidebar
