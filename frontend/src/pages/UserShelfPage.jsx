import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bookmark, Star, MapPin, User, Sparkles } from 'lucide-react';
import { fetchUserProfile } from '../services/api';
import { useUser } from '../context/UserContext';
import { BookCard } from '../components/BookCard';
import { RatingModal } from '../components/RatingModal';

export const UserShelfPage = () => {
  const navigate = useNavigate();
  const { activeUser } = useUser();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedBookForRating, setSelectedBookForRating] = useState(null);

  const loadProfile = async () => {
    if (!activeUser?.user_id) return;
    setLoading(true);
    try {
      const data = await fetchUserProfile(activeUser.user_id);
      setProfile(data);
    } catch (err) {
      console.error('Failed to load user profile:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, [activeUser]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      
      {/* Profile Header Card */}
      <div className="bg-gradient-to-r from-rose-500 to-rose-400 rounded-3xl p-6 sm:p-8 text-white shadow-soft mb-10 relative overflow-hidden">
        
        <div className="relative z-10 max-w-xl">
          <div className="inline-block bg-white/20 backdrop-blur-md px-3 py-1 rounded-full text-xs font-bold text-white mb-3">
            Active Demo Persona
          </div>
          <h1 className="font-display font-black text-2xl sm:text-3xl mb-1">{activeUser?.name}</h1>
          <p className="text-xs text-rose-100 font-medium mb-4">{activeUser?.persona}</p>

          <div className="flex flex-wrap gap-4 text-xs font-semibold text-rose-50 pt-2 border-t border-white/20">
            <div className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5" /> {activeUser?.location || 'New York, USA'}
            </div>
            <div className="flex items-center gap-1">
              <User className="w-3.5 h-3.5" /> Age: {activeUser?.age || 25}
            </div>
            <div className="flex items-center gap-1 bg-white/20 px-2.5 py-0.5 rounded-full">
              <Bookmark className="w-3.5 h-3.5" /> {activeUser?.rating_count || 0} Rated Books
            </div>
          </div>
        </div>
      </div>

      {/* Shelf Section */}
      <div>
        <div className="mb-6">
          <h2 className="font-display font-bold text-2xl text-plum-900 flex items-center gap-2">
            My Rated Books Shelf <Sparkles className="w-5 h-5 text-rose-500" />
          </h2>
          <p className="text-xs text-gray-500">
            Books rated by {activeUser?.name}. These ratings actively drive personalized collaborative filtering.
          </p>
        </div>

        {loading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="animate-pulse bg-rose-100/50 rounded-2xl h-64"></div>
            ))}
          </div>
        ) : profile?.recent_ratings && profile.recent_ratings.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
            {profile.recent_ratings.map((item) => (
              <div
                key={item.isbn}
                onClick={() => navigate(`/books/${encodeURIComponent(item.isbn)}`)}
                className="glass-card rounded-2xl p-3 cursor-pointer hover:shadow-soft transition-all"
              >
                <div className="aspect-[3/4] w-full rounded-xl overflow-hidden mb-2 bg-rose-50 relative">
                  <img
                    src={item.image_url_m || "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&q=80"}
                    alt={item.title}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-2 right-2 bg-rose-500 text-white font-bold text-xs px-2 py-0.5 rounded-full flex items-center gap-1 shadow-sm">
                    <Star className="w-3 h-3 fill-white" /> {item.user_rating}/10
                  </div>
                </div>
                <h3 className="font-display font-bold text-xs text-plum-900 line-clamp-1">{item.title}</h3>
                <p className="text-[10px] text-gray-500 line-clamp-1">by {item.author}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-3xl p-12 text-center max-w-md mx-auto border border-rose-100 shadow-sm">
            <Bookmark className="w-12 h-12 text-rose-300 mx-auto mb-3" />
            <h3 className="font-display font-bold text-lg text-plum-900">Your shelf is empty</h3>
            <p className="text-xs text-gray-500 mt-1 mb-4">
              You haven't rated any books as {activeUser?.name} yet. Rate any book from Search or Recommendations to add it to your shelf!
            </p>
            <button
              onClick={() => navigate('/search')}
              className="btn-y2k text-white px-5 py-2.5 rounded-full font-bold text-xs shadow-soft"
            >
              Browse & Rate Books
            </button>
          </div>
        )}
      </div>

      {/* Rating Modal */}
      <RatingModal
        book={selectedBookForRating}
        isOpen={!!selectedBookForRating}
        onClose={() => setSelectedBookForRating(null)}
        onRatingSubmitted={loadProfile}
      />
    </div>
  );
};
