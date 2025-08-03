// frontend/src/components/PulseFeed.tsx
import React, { useState, useMemo } from 'react';
import { Search, TrendingUp, Clock } from 'lucide-react';
import { PulseCard } from './PulseCard';
import { Pulse } from '../types';

interface PulseFeedProps {
  pulses: Pulse[];
}

// Define the valid sort types
type SortByType = 'recent' | 'popular';

export const PulseFeed: React.FC<PulseFeedProps> = ({ pulses }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<SortByType>('recent');

  const filteredAndSortedPulses = useMemo(() => {
    let filtered = pulses;

    if (searchQuery) {
      filtered = pulses.filter(pulse =>
        pulse.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        pulse.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
        pulse.blurb.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    return [...filtered].sort((a, b) => { // Create a new array to avoid mutating the prop
      if (sortBy === 'popular') {
        return b.views - a.views;
      }
      // Default to 'recent'
      return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
    });
  }, [searchQuery, sortBy, pulses]);
  
  // New handler for the sort buttons
  const handleSortChange = (newSortBy: SortByType) => {
    // If the user clicks the currently active button, reset to 'recent'
    if (sortBy === newSortBy) {
      setSortBy('recent');
    } else {
      setSortBy(newSortBy);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-4xl md:text-5xl font-bold mb-4">
          <span className="bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
            Pulse Feed
          </span>
        </h1>
        <p className="text-xl text-gray-300 mb-6">
          Real-time insights from the tech world, categorized and summarized
        </p>

        {/* --- ADDED SORT BUTTONS AND SEARCH BAR --- */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search pulses..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-gray-900/50 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={() => handleSortChange('recent')}
              className={`flex items-center space-x-2 px-4 py-3 rounded-lg transition-colors ${
                sortBy === 'recent'
                  ? 'bg-cyan-500 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              <Clock className="h-4 w-4" />
              <span>Recent</span>
            </button>
            <button
              onClick={() => handleSortChange('popular')}
              className={`flex items-center space-x-2 px-4 py-3 rounded-lg transition-colors ${
                sortBy === 'popular'
                  ? 'bg-cyan-500 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              <TrendingUp className="h-4 w-4" />
              <span>Popular</span>
            </button>
          </div>
        </div>

        {searchQuery && (
          <div className="mb-6">
            <p className="text-gray-400">
              Found {filteredAndSortedPulses.length} pulses matching "{searchQuery}"
            </p>
          </div>
        )}
      </div>

      <div className="space-y-6">
        {filteredAndSortedPulses.map((pulse) => (
          <PulseCard
            key={pulse.id}
            pulse={pulse}
          />
        ))}
      </div>
    </div>
  );
};