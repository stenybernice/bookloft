import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Flame, Users, Sliders } from 'lucide-react';
import { fetchPopularRecommendations, fetchCollaborativeRecommendations, fetchHybridRecommendations } from '../services/api';
import { useUser } from '../context/UserContext';
import { BookCard } from '../components/BookCard';
import { RatingModal } from '../components/RatingModal';

export const RecommendationsPage = () => {
  const navigate = useNavigate();
  const { activeUser } = useUser();
  
  const [activeTab, setActiveTab] = useState('hybrid'); // 'hybrid', 'collaborative', 'popular'
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Configurable Hybrid Weights
  const [cfWeight, setCfWeight] = useState(0.7);
  const [popWeight, setPopWeight] = useState(0.3);
  const [selectedBookForRating, setSelectedBookForRating] = useState(null);

  const loadRecommendations = async () => {
    setLoading(true);
    try {
      if (activeTab === 'popular') {
        const res = await fetchPopularRecommendations(12);
        setBooks(res.items || []);
      } else if (activeTab === 'collaborative') {
        const res = await fetchCollaborativeRecommendations(activeUser.user_id, 12);
        setBooks(res.items || []);
      } else {
        // Hybrid
        const res = await fetchHybridRecommendations(activeUser.user_id, 12, cfWeight, popWeight);
        setBooks(res.items || []);
      }
    } catch (err) {
      console.error('Failed to load recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecommendations();
  }, [activeTab, activeUser, cfWeight, popWeight]);

  const handleCfSliderChange = (e) => {
    const val = parseFloat(e.target.value);
    setCfWeight(val);
    setPopWeight(parseFloat((1.0 - val).toFixed(2)));
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      
      {/* Page Title */}
      <div className="mb-8 text-center max-w-2xl mx-auto">
        <span className="text-xs font-bold uppercase tracking-widest text-rose-500">ML Recommendation Engine</span>
        <h1 className="font-display font-black text-3xl sm:text-4xl text-plum-900 mt-1 mb-3">
          Recommendation Hub
        </h1>
        <p className="text-sm text-gray-600 font-medium">
          Compare recommendation strategies for <span className="font-bold text-plum-900">{activeUser?.name}</span>.
        </p>
      </div>

      {/* Strategy Tabs */}
      <div className="flex justify-center mb-8">
        <div className="inline-flex p-1.5 bg-cream-100/80 rounded-2xl border border-rose-100 shadow-sm gap-1">
          <button
            onClick={() => setActiveTab('hybrid')}
            className={`px-5 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeTab === 'hybrid'
                ? 'bg-rose-500 text-white shadow-soft'
                : 'text-plum-900 hover:bg-white/60'
            }`}
          >
            <Sparkles className="w-4 h-4" /> Just For You (Hybrid)
          </button>

          <button
            onClick={() => setActiveTab('collaborative')}
            className={`px-5 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeTab === 'collaborative'
                ? 'bg-rose-500 text-white shadow-soft'
                : 'text-plum-900 hover:bg-white/60'
            }`}
          >
            <Users className="w-4 h-4" /> Collaborative Filtering
          </button>

          <button
            onClick={() => setActiveTab('popular')}
            className={`px-5 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeTab === 'popular'
                ? 'bg-rose-500 text-white shadow-soft'
                : 'text-plum-900 hover:bg-white/60'
            }`}
          >
            <Flame className="w-4 h-4" /> Popular Right Now
          </button>
        </div>
      </div>

      {/* Configurable Hybrid Weights Panel */}
      {activeTab === 'hybrid' && (
        <div className="max-w-xl mx-auto mb-8 bg-white p-4 rounded-2xl border border-rose-100 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-plum-900 flex items-center gap-1">
              <Sliders className="w-3.5 h-3.5 text-rose-500" /> Configurable Hybrid Weight Blend
            </span>
            <span className="text-xs font-bold text-rose-600 bg-rose-50 px-2.5 py-0.5 rounded-full">
              CF: {(cfWeight * 100).toFixed(0)}% | Popularity: {(popWeight * 100).toFixed(0)}%
            </span>
          </div>

          <input
            type="range"
            min="0.0"
            max="1.0"
            step="0.05"
            value={cfWeight}
            onChange={handleCfSliderChange}
            className="w-full accent-rose-500 cursor-pointer"
          />

          <div className="flex justify-between text-[10px] font-bold text-gray-500 mt-1">
            <span>100% Popularity</span>
            <span>Balanced 50/50</span>
            <span>100% Collaborative Filtering</span>
          </div>
        </div>
      )}

      {/* Recommendation Results Grid */}
      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((i) => (
            <div key={i} className="animate-pulse bg-rose-100/50 rounded-2xl h-64"></div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
          {books.map((book) => (
            <BookCard
              key={book.isbn}
              book={book}
              onSelect={() => navigate(`/books/${encodeURIComponent(book.isbn)}`)}
              onRate={(b) => setSelectedBookForRating(b)}
            />
          ))}
        </div>
      )}

      {/* Rating Modal */}
      <RatingModal
        book={selectedBookForRating}
        isOpen={!!selectedBookForRating}
        onClose={() => setSelectedBookForRating(null)}
        onRatingSubmitted={loadRecommendations}
      />
    </div>
  );
};
