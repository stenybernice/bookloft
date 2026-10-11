import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Star, Sparkles, Heart, ArrowLeft, Building2, Calendar, Hash, BookOpen } from 'lucide-react';
import { fetchBookDetails, fetchSimilarBooks } from '../services/api';
import { BookCard } from '../components/BookCard';
import { RatingModal } from '../components/RatingModal';

export const BookDetailPage = () => {
  const { isbn } = useParams();
  const navigate = useNavigate();

  const [book, setBook] = useState(null);
  const [similarBooks, setSimilarBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedBookForRating, setSelectedBookForRating] = useState(null);

  const loadDetails = async () => {
    setLoading(true);
    try {
      const details = await fetchBookDetails(isbn);
      setBook(details);

      const similar = await fetchSimilarBooks(isbn, 6);
      setSimilarBooks(similar || []);
    } catch (err) {
      console.error('Failed to load book details:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isbn) {
      loadDetails();
    }
  }, [isbn]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="animate-pulse bg-rose-100/50 rounded-3xl h-96"></div>
      </div>
    );
  }

  if (!book) {
    return (
      <div className="max-w-md mx-auto py-20 text-center">
        <h2 className="font-display font-bold text-xl text-plum-900">Book Not Found</h2>
        <button onClick={() => navigate(-1)} className="mt-4 btn-y2k text-white px-4 py-2 rounded-full text-xs font-bold">
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      
      {/* Back Button */}
      <button
        onClick={() => navigate(-1)}
        className="mb-6 flex items-center gap-1.5 text-xs font-bold text-rose-600 hover:text-rose-700 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to discovery
      </button>

      {/* Book Metadata Main Showcase */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-rose-100 shadow-soft mb-12 flex flex-col md:flex-row gap-8 items-start">
        
        {/* Large Cover Image */}
        <div className="w-full md:w-64 aspect-[3/4] rounded-2xl overflow-hidden bg-rose-50 shadow-md shrink-0 relative">
          <img
            src={book.image_url_m || "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&q=80"}
            alt={book.title}
            className="w-full h-full object-cover"
          />
        </div>

        {/* Detailed Info */}
        <div className="flex-1 space-y-4">
          <div>
            <span className="text-xs uppercase font-extrabold tracking-widest text-rose-500">Book Metadata</span>
            <h1 className="font-display font-black text-2xl sm:text-4xl text-plum-900 mt-1">{book.title}</h1>
            <p className="text-base text-gray-600 font-medium">by <span className="font-bold text-plum-900">{book.author}</span></p>
          </div>

          {/* Stats Bar */}
          <div className="flex flex-wrap gap-3 py-3 border-y border-rose-100">
            <div className="flex items-center gap-1.5 bg-rose-50 px-3 py-1.5 rounded-full text-xs font-bold text-plum-900">
              <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
              <span>{book.avg_rating > 0 ? book.avg_rating.toFixed(1) : 'New'} / 10</span>
              <span className="text-gray-400 font-normal">({book.rating_count} ratings)</span>
            </div>

            {book.popularity_score > 0 && (
              <div className="flex items-center gap-1.5 bg-purple-50 px-3 py-1.5 rounded-full text-xs font-bold text-purple-700">
                <Sparkles className="w-4 h-4 text-purple-500" />
                <span>Popularity Score: {book.popularity_score.toFixed(2)}</span>
              </div>
            )}
          </div>

          {/* Metadata Specs Grid */}
          <div className="grid grid-cols-2 gap-4 text-xs font-medium text-gray-600 pt-2">
            <div className="flex items-center gap-2">
              <Building2 className="w-4 h-4 text-rose-400" />
              <span>Publisher: <strong className="text-plum-900">{book.publisher}</strong></span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-rose-400" />
              <span>Publication Year: <strong className="text-plum-900">{book.year}</strong></span>
            </div>
            <div className="flex items-center gap-2">
              <Hash className="w-4 h-4 text-rose-400" />
              <span>ISBN: <strong className="text-plum-900 font-mono">{book.isbn}</strong></span>
            </div>
          </div>

          {/* Action Trigger */}
          <div className="pt-4">
            <button
              onClick={() => setSelectedBookForRating(book)}
              className="btn-y2k text-white px-6 py-3 rounded-full font-bold text-sm shadow-soft flex items-center gap-2"
            >
              <Heart className="w-4 h-4 fill-white" /> Rate This Book
            </button>
          </div>
        </div>

      </div>

      {/* "You May Also Like" Item-Item Collaborative Similarity Section */}
      {similarBooks.length > 0 && (
        <section>
          <div className="mb-6">
            <span className="text-xs uppercase font-extrabold tracking-widest text-rose-500">Item Similarity</span>
            <h2 className="font-display font-bold text-2xl text-plum-900">You May Also Like</h2>
            <p className="text-xs text-gray-500">Books with similar reading profiles based on cosine similarity matrices.</p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
            {similarBooks.map((simBook) => (
              <BookCard
                key={simBook.isbn}
                book={simBook}
                onSelect={() => navigate(`/books/${encodeURIComponent(simBook.isbn)}`)}
                onRate={(b) => setSelectedBookForRating(b)}
              />
            ))}
          </div>
        </section>
      )}

      {/* Rating Modal */}
      <RatingModal
        book={selectedBookForRating}
        isOpen={!!selectedBookForRating}
        onClose={() => setSelectedBookForRating(null)}
        onRatingSubmitted={loadDetails}
      />
    </div>
  );
};
