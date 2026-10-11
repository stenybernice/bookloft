import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Star, Heart, CheckCircle } from 'lucide-react';
import { submitRating } from '../services/api';
import { useUser } from '../context/UserContext';

export const RatingModal = ({ book, isOpen, onClose, onRatingSubmitted }) => {
  const { activeUser, updateUserRatingCount } = useUser();
  const [rating, setRating] = useState(8);
  const [hoverRating, setHoverRating] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  if (!isOpen || !book) return null;

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const res = await submitRating(activeUser.user_id, book.isbn, rating);
      setSuccess(true);
      if (res.user_total_ratings) {
        updateUserRatingCount(res.user_total_ratings);
      }
      setTimeout(() => {
        setSuccess(false);
        onClose();
        if (onRatingSubmitted) onRatingSubmitted();
      }, 1200);
    } catch (err) {
      console.error('Failed to submit rating:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const getRatingLabel = (val) => {
    const labels = {
      1: "1/10 — Disliked",
      2: "2/10 — Poor",
      3: "3/10 — Mediocre",
      4: "4/10 — Below Average",
      5: "5/10 — Average",
      6: "6/10 — Decent",
      7: "7/10 — Good",
      8: "8/10 — Very Good!",
      9: "9/10 — Excellent!",
      10: "10/10 — Masterpiece!"
    };
    return labels[val] || `${val}/10`;
  };

  const activeVal = hoverRating || rating;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-plum-900/40 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-rose-100 relative"
        >
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 text-gray-400 hover:text-plum-900 rounded-full hover:bg-rose-50 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>

          {success ? (
            <div className="py-8 flex flex-col items-center justify-center text-center">
              <CheckCircle className="w-16 h-16 text-rose-500 mb-3 animate-bounce" />
              <h3 className="font-display font-bold text-xl text-plum-900">Rating Saved!</h3>
              <p className="text-sm text-gray-600 mt-1">
                Your rating has updated your shelf and personalized hybrid recommendations.
              </p>
            </div>
          ) : (
            <>
              {/* Header */}
              <div className="flex items-center gap-4 mb-6">
                <img
                  src={book.image_url_m || "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&q=80"}
                  alt={book.title}
                  className="w-16 h-22 object-cover rounded-xl shadow-sm border border-rose-100"
                />
                <div>
                  <span className="text-xs uppercase font-bold tracking-wider text-rose-500">Rate this book</span>
                  <h3 className="font-display font-bold text-lg text-plum-900 line-clamp-1">{book.title}</h3>
                  <p className="text-xs text-gray-500">by {book.author}</p>
                </div>
              </div>

              {/* Star selector (1 to 10) */}
              <div className="mb-6 bg-cream-50 p-4 rounded-2xl border border-rose-100/60 text-center">
                <div className="flex justify-center items-center gap-1 mb-2">
                  {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
                    <button
                      key={num}
                      onMouseEnter={() => setHoverRating(num)}
                      onMouseLeave={() => setHoverRating(0)}
                      onClick={() => setRating(num)}
                      className="p-1 transition-transform hover:scale-125 focus:outline-none"
                    >
                      <Star
                        className={`w-6 h-6 ${
                          num <= activeVal
                            ? 'fill-rose-500 text-rose-500'
                            : 'fill-gray-100 text-gray-300'
                        }`}
                      />
                    </button>
                  ))}
                </div>
                <p className="text-sm font-bold text-rose-600">{getRatingLabel(activeVal)}</p>
              </div>

              {/* Submit Button */}
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="w-full btn-y2k text-white py-3 rounded-full font-bold text-sm shadow-soft flex items-center justify-center gap-2"
              >
                {submitting ? (
                  <span>Saving Rating...</span>
                ) : (
                  <>
                    <Heart className="w-4 h-4 fill-white" /> Submit Rating for User #{activeUser.user_id}
                  </>
                )}
              </button>
            </>
          )}

        </motion.div>
      </div>
    </AnimatePresence>
  );
};
