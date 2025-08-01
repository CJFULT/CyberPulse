import React from 'react';

export const PulseAnimation: React.FC = () => {
  return (
    <div className="fixed top-8 right-8 z-20">
      <div className="relative">
        <div className="w-4 h-4 bg-cyan-400 rounded-full animate-ping"></div>
        <div className="absolute top-0 left-0 w-4 h-4 bg-cyan-400 rounded-full animate-pulse"></div>
      </div>
      <div className="text-xs text-cyan-400 mt-1 font-medium">LIVE</div>
    </div>
  );
};