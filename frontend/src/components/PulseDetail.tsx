import React from 'react';
import { ArrowLeft, Clock, Eye } from 'lucide-react';
import { Pulse } from '../types';

interface PulseDetailProps {
  pulse: Pulse;
  onBack: () => void;
}

export const PulseDetail: React.FC<PulseDetailProps> = ({ pulse, onBack }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <button
        onClick={onBack}
        className="flex items-center space-x-2 text-cyan-400 hover:text-cyan-300 transition-colors mb-8 group"
      >
        <ArrowLeft className="h-5 w-5 group-hover:-translate-x-1 transition-transform" />
        <span>Back to Pulse Feed</span>
      </button>

      <article className="bg-gradient-to-br from-gray-900/90 to-gray-800/90 border border-gray-700/50 rounded-xl p-8">
        <header className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-4 leading-tight">
            {pulse.title}
          </h1>
          
          <div className="flex flex-wrap items-center gap-4 mb-4">
            <span 
              className={`px-4 py-2 rounded-full text-sm font-medium text-white bg-gradient-to-r ${pulse.categoryGradient}`}
            >
              {pulse.category}
            </span>
            
            <div className="flex items-center space-x-2 text-gray-400">
              <Clock className="h-4 w-4" />
              <span>{formatDate(pulse.createdAt)}</span>
            </div>
            
            <div className="flex items-center space-x-2 text-gray-400">
              <Eye className="h-4 w-4" />
              <span>{pulse.views.toLocaleString()} views</span>
            </div>
          </div>
        </header>

        {/* <div className="prose prose-invert prose-lg max-w-none"> */}
        <div className="text-gray-300 text-lg leading-relaxed whitespace-pre-line">
            {pulse.content}
        </div>
        {/* </div> */}

        <footer className="mt-8 pt-6 border-t border-gray-700">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-400">
              Published {formatDate(pulse.createdAt)}
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-400">
              <Eye className="h-4 w-4" />
              <span>{pulse.views.toLocaleString()} views</span>
            </div>
          </div>
        </footer>
      </article>
    </div>
  );
};