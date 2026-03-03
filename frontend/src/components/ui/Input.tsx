import React from 'react'
import { cn } from '../../utils/helpers'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    variant?: 'default' | 'glass' | 'neon'
    error?: string
    icon?: React.ReactNode
}

const Input: React.FC<InputProps> = ({
    variant = 'default',
    error,
    icon,
    className,
    ...props
}) => {
    const baseClasses = 'w-full rounded-lg border transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2'

    const variants = {
        default: 'bg-primary-100/50 border-primary-300 focus:border-accent-500 focus:ring-accent-500 text-primary-900 placeholder-primary-500',
        glass: 'glass-effect border-primary-300/30 focus:border-accent-500 focus:ring-accent-500 text-primary-900 placeholder-primary-500',
        neon: 'bg-primary-100/70 border-accent-500/30 focus:border-accent-500 focus:ring-accent-500 text-primary-900 placeholder-primary-500 neon-glow',
    }

    return (
        <div className="relative">
            {icon && (
                <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary-500">
                    {icon}
                </div>
            )}
            <input
                className={cn(
                    baseClasses,
                    variants[variant],
                    icon && 'pl-10',
                    error && 'border-danger focus:ring-danger',
                    className
                )}
                {...props}
            />
            {error && (
                <p className="mt-1 text-sm text-danger">{error}</p>
            )}
        </div>
    )
}

export default Input
