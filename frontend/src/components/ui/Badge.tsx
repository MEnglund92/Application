import React from 'react'
import { cn } from '../../utils/helpers'

interface BadgeProps {
    children: React.ReactNode
    variant?: 'default' | 'success' | 'warning' | 'danger' | 'accent'
    size?: 'sm' | 'md' | 'lg'
    className?: string
}

const Badge: React.FC<BadgeProps> = ({
    children,
    variant = 'default',
    size = 'md',
    className,
}) => {
    const baseClasses = 'inline-flex items-center justify-center font-semibold rounded-full'

    const variants = {
        default: 'bg-primary-200 text-primary-900',
        success: 'bg-success/20 text-success',
        warning: 'bg-warning/20 text-warning',
        danger: 'bg-danger/20 text-danger',
        accent: 'bg-accent-500/20 text-accent-500',
    }

    const sizes = {
        sm: 'px-2 py-0.5 text-xs',
        md: 'px-3 py-1 text-sm',
        lg: 'px-4 py-1.5 text-base',
    }

    return (
        <span
            className={cn(
                baseClasses,
                variants[variant],
                sizes[size],
                className
            )}
        >
            {children}
        </span>
    )
}

export default Badge
