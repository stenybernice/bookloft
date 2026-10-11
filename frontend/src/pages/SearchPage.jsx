import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Search, BookOpen, AlertCircle } from 'lucide-react';
import { searchBooks } from '../services/api';
import { BookCard } from '../components/BookCard';
import { RatingModal } from '../components/RatingModal';

export const SearchPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const queryParam = searchParams.get('q') || '';

  const [query, setQuery] = useState(queryParam);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedBookForRating, setSelectedBookForRating] = useState(null);

  const performSearch = async (searchTerm) => {
    if (!searchTerm.trim()) {
      setResults([]);
      return;
    }
    setLoading(true);
    try {
      const data = await searchBooks(searchTerm.trim(), 24);
      setResults(data || []);
    } catch (err) {
      console.error('Search failed:', err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setQuery(queryParam);
    if (queryParam) {
      performSearch(queryParam);
    } else {
      // Default initial query
      performSearch('a');
    }
  }, [queryParam]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      setSearchParams({ q: query.trim() });
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      
      {/* Search Header */}
      <div className="max-w-2xl mx-auto text-center mb-8">
        <h1 className="font-display font-black text-3xl text-plum-900 mb-2">Book Catalogue Search</h1>
        <p className="text-xs text-gray-500 mb-6">Search over 800+ books by title, author, or ISBN number.</p>

        <form onSubmit={handleSearchSubmit} className="relative flex items-center">
          <input
            type="text"
            placeholder="Type book title, author, or ISBN..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-12 pr-28 py-3.5 rounded-full bg-white border-2 border-rose-200 focus:border-rose-500 focus:outline-none shadow-soft text-sm font-medium text-plum-900 transition-all"
          />
          <Search className="w-5 h-5 text-gray-400 absolute left-4" />
          <button
            type="submit"
            className="absolute right-2 btn-y2k text-white px-5 py-2 rounded-full font-bold text-xs shadow-soft"
          >
            Search
          </button>
        </form>
      </div>

      {/* Results Section */}
      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((i) => (
            <div key={i} className="animate-pulse bg-rose-100/50 rounded-2xl h-64"></div>
          ))}
        </div>
      ) : results.length > 0 ? (
        <div>
          <div className="text-xs text-gray-500 font-bold mb-4">
            Found {results.length} book results {queryParam ? `for "${queryParam}"` : ''}
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
            {results.map((book) => (
              <BookCard
                key={book.isbn}
                book={book}
                onSelect={() => navigate(`/books/${encodeURIComponent(book.isbn)}`)}
                onRate={(b) => setSelectedBookForRating(b)}
              />
            ))}
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-3xl p-12 text-center max-w-md mx-auto border border-rose-100 shadow-sm mt-8">
          <AlertCircle className="w-12 h-12 text-rose-400 mx-auto mb-3" />
          <h3 className="font-display font-bold text-lg text-plum-900">No books found</h3>
          <p className="text-xs text-gray-500 mt-1">
            No titles or authors matched "{queryParam}". Try searching for another keyword like "Harry", "Rowling", or "Dragon".
          </p>
        </div>
      )}

      {/* Rating Modal */}
      <RatingModal
        book={selectedBookForRating}
        isOpen={!!selectedBookForRating}
        onClose={() => setSelectedBookForRating(null)}
        onRatingSubmitted={() => performSearch(query)}
      />
    </div>
  );
};
