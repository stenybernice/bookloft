import React from 'react';
import { BookOpen, Sparkles, Github } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="bg-white border-t border-rose-100 mt-20 py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-rose-500 flex items-center justify-center text-white font-bold text-sm">
            <BookOpen className="w-4 h-4" />
          </div>
          <span className="font-display font-extrabold text-lg text-plum-900 flex items-center gap-1">
            Book reccomender <Sparkles className="w-4 h-4 text-rose-500" />
          </span>
          <span className="text-xs text-gray-500 ml-2">
            Full-Stack Hybrid Book Recommendation Engine
          </span>
        </div>

        <div className="text-xs text-gray-500 text-center md:text-right">
          Built with React, FastAPI, MongoDB, scikit-learn, and Item-Item Collaborative Filtering.
        </div>
      </div>
    </footer>
  );
};
