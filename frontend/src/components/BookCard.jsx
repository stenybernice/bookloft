import React, { useState } from 'react';
import { Star, Sparkles, Heart, BookOpen, Layers } from 'lucide-react';

export const BookCard = ({ book, onSelect, onRate }) => {
  const [imgSrc, setImgSrc] = useState(
    book.image_url_m || "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&q=80"
  );

  const handleImgError = () => {
    setImgSrc("https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&q=80");
  };

  return (
    <div className="glass-card rounded-2xl p-4 flex flex-col justify-between hover:shadow-soft hover:-translate-y-1 transition-all duration-300 group border border-rose-100/80 relative">
      
      {/* Cover Image Container */}
      <div 
        onClick={() => onSelect && onSelect(book)} 
        className="relative aspect-[3/4] w-full rounded-xl overflow-hidden mb-3 bg-rose-50 cursor-pointer shadow-sm group-hover:shadow-md transition-shadow"
      >
        <img
          src={imgSrc}
          alt={book.title}
          onError={handleImgError}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          loading="lazy"
        />
        
        {/* Rating Badge */}
        <div className="absolute top-2 right-2 bg-white/90 backdrop-blur-md px-2.5 py-1 rounded-full text-xs font-bold text-plum-900 shadow-sm flex items-center gap-1">
          <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
          <span>{book.avg_rating > 0 ? book.avg_rating.toFixed(1) : 'New'}</span>
          {book.rating_count > 0 && (
            <span className="text-[10px] text-gray-500 font-normal">({book.rating_count})</span>
          )}
        </div>

        {/* Popularity Score Pill */}
        {book.popularity_score > 0 && (
          <div className="absolute bottom-2 left-2 bg-rose-500/90 backdrop-blur-md text-white text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 shadow-sm">
            <Sparkles className="w-3 h-3 text-amber-300" />
            <span>Score: {book.popularity_score.toFixed(1)}</span>
          </div>
        )}
      </div>

      {/* Book Metadata */}
      <div className="flex-1 flex flex-col justify-between">
        <div onClick={() => onSelect && onSelect(book)} className="cursor-pointer">
          <h3 className="font-display font-bold text-base text-plum-900 line-clamp-1 group-hover:text-rose-600 transition-colors">
            {book.title}
          </h3>
          <p className="text-xs text-gray-600 font-medium line-clamp-1 mb-2">
            by {book.author}
          </p>
        </div>

        {/* Recommendation Reason Badge */}
        {book.recommendation_reason && (
          <div className="bg-rose-50/80 border border-rose-200/60 rounded-xl p-2 mb-3 text-[11px] text-rose-800 font-medium flex items-start gap-1.5 leading-tight">
            <Sparkles className="w-3.5 h-3.5 text-rose-500 shrink-0 mt-0.5" />
            <span className="line-clamp-2">{book.recommendation_reason}</span>
          </div>
        )}

        {/* Card Footer Actions */}
        <div className="flex items-center gap-2 pt-2 border-t border-rose-100/60">
          <button
            onClick={() => onSelect && onSelect(book)}
            className="flex-1 py-1.5 px-3 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 hover:bg-rose-100 transition-colors flex items-center justify-center gap-1"
          >
            <BookOpen className="w-3.5 h-3.5" /> Details
          </button>
          
          {onRate && (
            <button
              onClick={() => onRate(book)}
              className="py-1.5 px-3 rounded-full text-xs font-semibold bg-rose-500 text-white hover:bg-rose-600 shadow-sm transition-colors flex items-center justify-center gap-1"
            >
              <Heart className="w-3.5 h-3.5 fill-white" /> Rate
            </button>
          )}
        </div>
      </div>

    </div>
  );
};
