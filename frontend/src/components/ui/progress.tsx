import React from 'react';
export const Progress = ({ value, className }) => (
    <div className={`w-full bg-gray-700 rounded-full h-2.5 ${className}`}>
        <div className="bg-cyan-500 h-2.5 rounded-full transition-all duration-300" style={{ width: `${value}%` }}></div>
    </div>
);