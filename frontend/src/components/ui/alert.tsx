import React from 'react';
export const Alert = ({ className, children }) => <div className={`relative w-full rounded-lg border border-gray-700 bg-gray-800/60 px-4 py-3 text-sm text-gray-300 ${className}`}>{children}</div>;
export const AlertDescription = ({ className, children }) => <div className={`text-sm [&_p]:leading-relaxed ${className}`}>{children}</div>;
