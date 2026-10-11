import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Search, Flame, ArrowRight } from 'lucide-react';
import { fetchPopularRecommendations, fetchHybridRecommendations } from '../services/api';
import { useUser } from '../context/UserContext';
import { BookCard } from '../components/BookCard';
import { RatingModal } from '../components/RatingModal';

export const HomePage = () => {
  const navigate = useNavigate();
  const { activeUser } = useUser();
  const [searchQuery, setSearchQuery] = useState('');
  const [popularBooks, setPopularBooks] = useState([]);
  const [personalizedBooks, setPersonalizedBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedBookForRating, setSelectedBookForRating] = useState(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const popRes = await fetchPopularRecommendations(6);
      setPopularBooks(popRes.items || []);

      if (activeUser?.user_id) {
        const hybRes = await fetchHybridRecommendations(activeUser.user_id, 6);
        setPersonalizedBooks(hybRes.items || []);
      }
    } catch (err) {
      console.error('Failed to load homepage data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [activeUser]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <div className="min-h-screen pb-12">
      {/* Hero Section with Y2K Aesthetic Accents */}
      <section className="relative overflow-hidden pt-12 pb-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-rose-100/50 via-cream-50 to-cream-50">
        
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/80 border border-rose-200 shadow-sm text-xs font-bold text-rose-600 mb-6 backdrop-blur-md">
            <Sparkles className="w-4 h-4 text-rose-500" /> Powered by Item-Item Collaborative Filtering & Weighted Ranking
          </div>

          <h1 className="font-display font-black text-4xl sm:text-6xl text-plum-900 leading-tight mb-6">
            Find your next <span className="gradient-text">favorite book.</span>
          </h1>

          <p className="text-base sm:text-lg text-gray-600 max-w-2xl mx-auto mb-8 leading-relaxed font-medium">
            Discover books based on what real readers actually love. Powered by statistical popularity ranking and personalized collaborative filtering.
          </p>

          {/* Search Input Bar */}
          <form onSubmit={handleSearchSubmit} className="max-w-xl mx-auto relative flex items-center">
            <input
              type="text"
              placeholder="Search by title, author, or ISBN..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-28 py-4 rounded-full bg-white border-2 border-rose-200 focus:border-rose-500 focus:outline-none shadow-soft text-sm font-medium text-plum-900 transition-all placeholder:text-gray-400"
            />
            <Search className="w-5 h-5 text-gray-400 absolute left-4" />
            <button
              type="submit"
              className="absolute right-2 btn-y2k text-white px-5 py-2.5 rounded-full font-bold text-xs shadow-soft flex items-center gap-1"
            >
              Search
            </button>
          </form>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-16">
        
        {/* Personalized Recommendations Section */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs uppercase font-bold tracking-widest text-rose-500">Personalized Engine</span>
              </div>
              <h2 className="font-display font-bold text-2xl text-plum-900">
                Recommended for {activeUser?.name || 'You'}
              </h2>
            </div>

            <button
              onClick={() => navigate('/recommendations')}
              className="text-xs font-bold text-rose-600 hover:text-rose-700 flex items-center gap-1 group"
            >
              Explore Hub <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>

          {loading ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="animate-pulse bg-rose-100/50 rounded-2xl h-64"></div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
              {personalizedBooks.map((book) => (
                <BookCard
                  key={book.isbn}
                  book={book}
                  onSelect={() => navigate(`/books/${encodeURIComponent(book.isbn)}`)}
                  onRate={(b) => setSelectedBookForRating(b)}
                />
              ))}
            </div>
          )}
        </section>

        {/* Popular Books Section */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <div>
              <span className="text-xs uppercase font-bold tracking-widest text-rose-500">Statistical Popularity</span>
              <h2 className="font-display font-bold text-2xl text-plum-900 flex items-center gap-2">
                Popular Right Now <Flame className="w-5 h-5 text-rose-500 fill-rose-500 animate-pulse" />
              </h2>
            </div>

            <button
              onClick={() => navigate('/recommendations')}
              className="text-xs font-bold text-rose-600 hover:text-rose-700 flex items-center gap-1 group"
            >
              View All Top Books <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
            {popularBooks.map((book) => (
              <BookCard
                key={book.isbn}
                book={book}
                onSelect={() => navigate(`/books/${encodeURIComponent(book.isbn)}`)}
                onRate={(b) => setSelectedBookForRating(b)}
              />
            ))}
          </div>
        </section>

      </div>

      {/* Rating Modal */}
      <RatingModal
        book={selectedBookForRating}
        isOpen={!!selectedBookForRating}
        onClose={() => setSelectedBookForRating(null)}
        onRatingSubmitted={loadData}
      />
    </div>
  );
};
