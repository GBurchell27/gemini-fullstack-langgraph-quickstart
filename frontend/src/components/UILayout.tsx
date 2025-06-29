import React from 'react';

interface UILayoutProps {
  leftPanel: React.ReactNode;
  rightPanel: React.ReactNode;
}

export const UILayout: React.FC<UILayoutProps> = ({ leftPanel, rightPanel }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 h-full gap-4 p-4">
      <div className="md:col-span-1 h-full bg-black bg-opacity-20 backdrop-blur-md rounded-lg p-4 border border-white/10 overflow-y-auto">
        {leftPanel}
      </div>
      <div className="md:col-span-2 h-full bg-black bg-opacity-20 backdrop-blur-md rounded-lg border-white/10 flex flex-col overflow-hidden">
        {rightPanel}
      </div>
    </div>
  );
}; 