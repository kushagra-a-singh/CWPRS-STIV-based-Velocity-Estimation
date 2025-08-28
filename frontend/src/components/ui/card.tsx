import React from 'react';
export const Card = ({ className, children }) => <div className={`bg-gray-800/50 border border-gray-700 rounded-xl shadow-lg ${className}`}>{children}</div>;
export const CardHeader = ({ className, children }) => <div className={`p-6 border-b border-gray-700 ${className}`}>{children}</div>;
export const CardTitle = ({ className, children }) => <h3 className={`text-lg font-semibold text-gray-100 ${className}`}>{children}</h3>;
export const CardContent = ({ className, children }) => <div className={`p-6 ${className}`}>{children}</div>;
