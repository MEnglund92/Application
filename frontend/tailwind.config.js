/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    50: '#1e293b',
                    100: '#334155',
                    200: '#475569',
                    300: '#64748b',
                    400: '#94a3b8',
                    500: '#cbd5e1',
                    600: '#e2e8f0',
                    700: '#f1f5f9',
                    800: '#f8fafc',
                    900: '#ffffff',
                },
                accent: {
                    50: '#7c3aed',
                    100: '#8b5cf6',
                    200: '#a78bfa',
                    300: '#c4b5fd',
                    400: '#ddd6fe',
                    500: '#ede9fe',
                    600: '#f5f3ff',
                    700: '#faf7ff',
                },
                success: '#10b981',
                warning: '#f59e0b',
                danger: '#ef4444',
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
            animation: {
                'glow': 'glow 2s ease-in-out infinite alternate',
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            keyframes: {
                glow: {
                    '0%': { boxShadow: '0 0 5px #8b5cf6, 0 0 10px #8b5cf6' },
                    '100%': { boxShadow: '0 0 10px #8b5cf6, 0 0 20px #8b5cf6' },
                }
            }
        },
    },
    plugins: [],
}
