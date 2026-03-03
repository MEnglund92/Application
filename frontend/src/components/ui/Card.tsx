import React from 'react'
import { cn } from '../../utils/helpers'

interface CardProps {
    children: React.ReactNode
    className?: string
    variant?: 'default' | 'glass' | 'neon'
    padding?: 'none' | 'sm' | 'md' | 'lg'
}

const Card: React.FC<CardProps> = ({
    children,
    className,
    variant = 'default',
    padding = 'md',
}) => {
    const baseClasses = 'rounded-xl transition-all duration-300'

    const variants = {
        default: 'bg-primary-100/50 border border-primary-200/30',
        glass: 'glass-effect',
        neon: 'bg-primary-100/70 border border-accent-500/30 neon-glow',
    }

    const paddings = {
        none: '',
        sm: 'p-3',
        md: 'p-5',
        lg: 'p-7',
    }

    return (
        <div
            className={cn(
                baseClasses,
                variants[variant],
                paddings[padding],
                className
            )}
        >
            {children}
        </div>
    )
}

export default Card
