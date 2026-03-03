import React from 'react'
import { cn } from '../../utils/helpers'
import { Loader2 } from 'lucide-react'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'accent' | 'danger' | 'ghost'
    size?: 'sm' | 'md' | 'lg'
    loading?: boolean
    icon?: React.ReactNode
    children: React.ReactNode
}

const Button: React.FC<ButtonProps> = ({
    variant = 'primary',
    size = 'md',
    loading = false,
    icon,
    children,
    className,
    disabled,
    ...props
}) => {
    const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2'

    const variants = {
        primary: 'bg-accent-500 hover:bg-accent-600 text-white focus:ring-accent-500 gaming-button neon-glow',
        secondary: 'bg-primary-200 hover:bg-primary-300 text-primary-900 border border-primary-300',
        accent: 'bg-gradient-to-r from-accent-500 to-accent-600 hover:from-accent-600 hover:to-accent-700 text-white',
        danger: 'bg-danger hover:bg-red-600 text-white focus:ring-danger',
        ghost: 'bg-transparent hover:bg-primary-200/20 text-primary-700 border border-primary-300',
    }

    const sizes = {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg',
    }

    return (
        <button
            className={cn(
                baseClasses,
                variants[variant],
                sizes[size],
                (loading || disabled) && 'opacity-50 cursor-not-allowed',
                className
            )}
            disabled={loading || disabled}
            {...props}
        >
            {loading && <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" />}
            {icon && !loading && <span className="mr-2">{icon}</span>}
            {children}
        </button>
    )
}

export default Button
