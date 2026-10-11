import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BookOpen, Sparkles, UserCheck, Search, Compass, Bookmark } from 'lucide-react';
import { useUser } from '../context/UserContext';

export const Navbar = () => {
  const location = useLocation();
  const { activeUser, demoUsers, switchUser } = useUser();

  const isActive = (path) => location.pathname === path;

  return (
    <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-rose-100 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-2 group">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-rose-500 to-rose-400 flex items-center justify-center text-white shadow-soft group-hover:scale-105 transition-transform">
            <BookOpen className="w-5 h-5" />
          </div>
          <div className="flex flex-col">
            <span className="font-display font-extrabold text-xl tracking-tight text-plum-900 flex items-center gap-1">
              Book reccomender <Sparkles className="w-4 h-4 text-rose-500 animate-pulse" />
            </span>
            <span className="text-[10px] uppercase tracking-widest text-rose-500 font-bold -mt-1">
              Hybrid ML Discovery
            </span>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-1 bg-cream-100/60 p-1.5 rounded-full border border-rose-100/60">
          <Link
            to="/"
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-1.5 ${
              isActive('/') 
                ? 'bg-white text-rose-600 shadow-sm font-semibold' 
                : 'text-plum-800 hover:text-rose-600 hover:bg-white/50'
            }`}
          >
            <BookOpen className="w-4 h-4" /> Home
          </Link>
          
          <Link
            to="/recommendations"
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-1.5 ${
              isActive('/recommendations')
                ? 'bg-white text-rose-600 shadow-sm font-semibold'
                : 'text-plum-800 hover:text-rose-600 hover:bg-white/50'
            }`}
          >
            <Compass className="w-4 h-4" /> Recommendations
          </Link>

          <Link
            to="/search"
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-1.5 ${
              isActive('/search')
                ? 'bg-white text-rose-600 shadow-sm font-semibold'
                : 'text-plum-800 hover:text-rose-600 hover:bg-white/50'
            }`}
          >
            <Search className="w-4 h-4" /> Search
          </Link>

          <Link
            to="/shelf"
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-1.5 ${
              isActive('/shelf')
                ? 'bg-white text-rose-600 shadow-sm font-semibold'
                : 'text-plum-800 hover:text-rose-600 hover:bg-white/50'
            }`}
          >
            <Bookmark className="w-4 h-4" /> My Shelf ({activeUser?.rating_count || 0})
          </Link>
        </nav>

        {/* Demo User Switcher Selector */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-rose-50 border border-rose-200 px-3 py-1.5 rounded-full shadow-sm">
            <UserCheck className="w-4 h-4 text-rose-600" />
            <div className="flex flex-col">
              <select
                value={activeUser?.user_id || 99999}
                onChange={(e) => switchUser(e.target.value)}
                className="bg-transparent text-xs font-bold text-plum-900 cursor-pointer focus:outline-none pr-1"
              >
                {demoUsers.map((u) => (
                  <option key={u.user_id} value={u.user_id}>
                    {u.name} ({u.rating_count} ratings)
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

      </div>
    </header>
  );
};
