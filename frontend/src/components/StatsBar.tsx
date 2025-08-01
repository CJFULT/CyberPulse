import React from 'react';
import { TrendingUp, Users, Zap, Globe } from 'lucide-react';

interface StatsBarProps {
  totalArticles: number;
  totalViews: number;
  totalCategories: number;
}

export const StatsBar: React.FC<StatsBarProps> = ({ totalArticles, totalViews, totalCategories }) => {
  const stats = [
    { icon: Globe, label: 'Articles', value: totalArticles.toLocaleString() },
    { icon: Users, label: 'Total Views', value: totalViews.toLocaleString() },
    { icon: TrendingUp, label: 'Categories', value: totalCategories.toString() },
    { icon: Zap, label: 'Live Sources', value: '24' }
  ];

  return (
    <div className="relative z-10 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 backdrop-blur-lg border border-cyan-500/20 rounded-xl p-6 mb-8">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <div key={index} className="text-center">
            <div className="flex justify-center mb-2">
              <div className="p-3 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-lg">
                <stat.icon className="h-6 w-6 text-white" />
              </div>
            </div>
            <div className="text-2xl font-bold text-white mb-1">{stat.value}</div>
            <div className="text-gray-400 text-sm">{stat.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
};