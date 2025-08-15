import React from 'react';
import { Clock, Eye, Calendar } from 'lucide-react';
import { Pulse } from '../types';

interface WeeklyPulseProps {
  pulse: Pulse;
  onClick: () => void;
}

export const WeeklyPulse: React.FC<WeeklyPulseProps> = ({ pulse, onClick }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
  };

  return (
    <div 
      onClick={onClick}
      className="group relative overflow-hidden rounded-xl bg-gradient-to-br from-gray-900/90 to-gray-800/90 border border-purple-500/30 hover:border-purple-400/60 transition-all duration-300 cursor-pointer hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/20 p-6"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-pink-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      
      <div className="relative">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg">
            <Calendar className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
              Weekly Pulse
            </h3>
            <p className="text-gray-400 text-sm">Week of {formatDate(pulse.createdAt)}</p>
          </div>
          <div className="ml-auto flex items-center space-x-2 text-gray-400">
            <Eye className="h-4 w-4" />
            <span>{pulse.views.toLocaleString()}</span>
          </div>
        </div>

        <h4 className="text-xl font-bold text-white mb-3 group-hover:text-purple-400 transition-colors leading-tight">
          {pulse.title}
        </h4>

        <div className="flex items-center space-x-3 mb-3">
          <span className={`px-3 py-1 rounded-full text-xs font-medium text-white bg-gradient-to-r ${pulse.categoryGradient}`}>
            {pulse.category}
          </span>
        </div>

        <p className="text-gray-300 leading-relaxed">
          {pulse.blurb}
        </p>
      </div>
    </div>
  );
};