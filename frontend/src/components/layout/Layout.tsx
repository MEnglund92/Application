import React from 'react'
import Sidebar from './Sidebar'
import Header from './Header'

interface LayoutProps {
    children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
    return (
        <div className="min-h-screen flex">
            <Sidebar />
            <div className="flex-1 lg:ml-0">
                <div className="p-6 lg:p-8">
                    <Header />
                    <main>{children}</main>
                </div>
            </div>
        </div>
    )
}

export default Layout
