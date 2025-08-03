import React from 'react';
import { Link } from 'react-router-dom';
import { Clock, Eye } from 'lucide-react';
import { Pulse } from '../types';

interface PulseCardProps {
  pulse: Pulse;
}

export const PulseCard: React.FC<PulseCardProps> = ({ pulse }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Link to={`/pulses/${pulse.slug}`} className="block">
        <div
            className="group relative overflow-hidden rounded-xl bg-gradient-to-br from-gray-900/90 to-gray-800/90 border border-gray-700/50 hover:border-cyan-500/50 transition-all duration-300 cursor-pointer hover:scale-[1.02] hover:shadow-2xl hover:shadow-cyan-500/10 p-6"
        >
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      
            <div className="relative">
                <div className="flex items-start justify-between mb-3">
                <div className="flex-1 pr-4">
                    <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-xl font-bold text-white group-hover:text-cyan-400 transition-colors leading-tight">
                        {pulse.title}
                    </h3>
                    <span 
                        className={`px-3 py-1 rounded-full text-xs font-medium text-white bg-gradient-to-r ${pulse.categoryGradient} whitespace-nowrap`}
                    >
                        {pulse.category}
                    </span>
                    </div>
                </div>
                <div className="flex items-center space-x-2 text-gray-400 text-sm">
                    <Eye className="h-4 w-4" />
                    <span>{pulse.views.toLocaleString()}</span>
                </div>
                </div>

                <div className="flex items-center space-x-2 mb-4 text-gray-400 text-sm">
                    <Clock className="h-4 w-4" />
                    <span>{formatDate(pulse.createdAt)}</span>
                </div>

                <p className="text-gray-300 leading-relaxed">
                    {pulse.blurb}
                </p>

                <div className="absolute bottom-0 right-0 w-16 h-16 bg-gradient-to-tl from-cyan-500/20 to-transparent rounded-tl-full opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            </div>
        </div>
    </Link>
  );
};