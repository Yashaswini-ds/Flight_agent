import React, { useState, useEffect } from 'react';
import { MessageSquare, Star, Send, CheckCircle2 } from 'lucide-react';
import api from '../services/api';
import { Feedback } from '../types';

export const FeedbackPage: React.FC = () => {
  const [rating, setRating] = useState(5);
  const [category, setCategory] = useState('Booking Experience');
  const [bookingRef, setBookingRef] = useState('');
  const [comments, setComments] = useState('');
  
  const [feedbackList, setFeedbackList] = useState<Feedback[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  const fetchFeedback = async () => {
    try {
      const res = await api.get('/feedback');
      setFeedbackList(res.data);
    } catch (err) {
      console.error("Failed to load feedback", err);
    }
  };

  useEffect(() => {
    fetchFeedback();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSuccess(false);

    try {
      await api.post('/feedback', {
        rating,
        category,
        booking_reference: bookingRef || undefined,
        comments
      });

      setSuccess(true);
      setComments('');
      setBookingRef('');
      fetchFeedback();
    } catch (err) {
      console.error("Failed to submit feedback", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 flex items-center gap-2">
          <MessageSquare className="w-6 h-6 text-teal-700" /> Platform Feedback & Reviews
        </h1>
        <p className="text-xs text-slate-500 font-medium mt-1">
          Share your feedback on our flight search, AI assistant, and AP2 payment experience.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
        {/* Form */}
        <div className="md:col-span-6 bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-5">
          <h3 className="font-bold text-slate-900 text-lg border-b border-slate-100 pb-3">Submit Your Feedback</h3>

          {success && (
            <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs p-3.5 rounded-xl font-bold flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Thank you! Your feedback has been recorded.
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Overall Rating</label>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setRating(star)}
                    className={`p-2 text-2xl transition-transform ${star <= rating ? 'text-amber-400 scale-110' : 'text-slate-200'}`}
                  >
                    ★
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">Feedback Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-teal-600 focus:outline-none"
              >
                <option value="Booking Experience">Booking Experience</option>
                <option value="AI Assistant">AI Assistant Feature</option>
                <option value="Payment Simulation">AP2 Payment Simulation</option>
                <option value="Cancellation / Refund">Cancellation & Refund</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">Booking Reference (Optional)</label>
              <input
                type="text"
                value={bookingRef}
                onChange={(e) => setBookingRef(e.target.value)}
                placeholder="e.g. BK-1234"
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-teal-600 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">Comments</label>
              <textarea
                rows={4}
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                placeholder="Tell us what you liked or how we can improve..."
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-teal-600 focus:outline-none"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-teal-700 hover:bg-teal-800 text-white font-bold py-3 rounded-xl transition-all shadow-md flex items-center justify-center gap-2 text-sm"
            >
              <Send className="w-4 h-4" />
              {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </form>
        </div>

        {/* History */}
        <div className="md:col-span-6 space-y-4">
          <h3 className="font-bold text-slate-900 text-base">Recent Reviews</h3>
          {feedbackList.length === 0 ? (
            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 text-center text-xs text-slate-500">
              No feedback submitted yet.
            </div>
          ) : (
            <div className="space-y-3">
              {feedbackList.map((f) => (
                <div key={f.id} className="bg-white border border-slate-200 rounded-2xl p-4 space-y-1.5 shadow-sm">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-teal-800">{f.category}</span>
                    <span className="text-amber-400 font-bold">{'★'.repeat(f.rating)}</span>
                  </div>
                  <p className="text-xs text-slate-700 font-medium">{f.comments}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
