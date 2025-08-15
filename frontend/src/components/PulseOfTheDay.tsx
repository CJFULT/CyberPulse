import React from 'react';
import { Clock, Eye, Zap } from 'lucide-react';
import { Pulse } from '../types';

interface PulseOfTheDayProps {
  pulse: Pulse;
  onClick: () => void;
}

export const PulseOfTheDay: React.FC<PulseOfTheDayProps> = ({ pulse, onClick }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div 
      onClick={onClick}
      className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-gray-900/95 to-gray-800/95 border border-cyan-500/30 hover:border-cyan-400/60 transition-all duration-500 cursor-pointer hover:scale-[1.02] hover:shadow-2xl hover:shadow-cyan-500/25 p-8"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      
      <div className="relative">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-3 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-xl">
            <Zap className="h-6 w-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
              Pulse of the Day
            </h2>
            <p className="text-gray-400 text-sm">{formatDate(pulse.createdAt)}</p>
          </div>
          <div className="ml-auto flex items-center space-x-2 text-gray-400">
            <Eye className="h-5 w-5" />
            <span className="text-lg font-medium">{pulse.views.toLocaleString()}</span>
          </div>
        </div>

        <h3 className="text-3xl font-bold text-white mb-4 group-hover:text-cyan-400 transition-colors leading-tight">
          {pulse.title}
        </h3>

        <div className="flex items-center space-x-3 mb-4">
          <span className={`px-4 py-2 rounded-full text-sm font-medium text-white bg-gradient-to-r ${pulse.categoryGradient}`}>
            {pulse.category}
          </span>
        </div>

        <p className="text-gray-300 text-lg leading-relaxed">
          {pulse.blurb}
        </p>

        <div className="absolute bottom-0 right-0 w-24 h-24 bg-gradient-to-tl from-cyan-500/20 to-transparent rounded-tl-full opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      </div>
    </div>
  );
};