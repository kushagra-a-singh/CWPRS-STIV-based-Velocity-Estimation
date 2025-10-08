import React from 'react';
export const Label = ({ className, children, ...props }) => <label className={`text-sm font-medium leading-none text-gray-300 ${className}`} {...props}>{children}</label>;
