import React from 'react';
export const Badge = ({ className, variant, children }) => {
    const variantClasses = {
        default: 'bg-gray-700 text-gray-200',
        secondary: 'velocity-indicator-bg text-cyan-200 border border-cyan-500/50',
    };
    return <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variantClasses[variant || 'default']} ${className}`}>{children}</span>;
};