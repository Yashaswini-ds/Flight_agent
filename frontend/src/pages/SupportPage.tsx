import React, { useState, useEffect } from 'react';
import { Headphones, Send, CheckCircle2, HelpCircle, AlertCircle } from 'lucide-react';
import api from '../services/api';
import { SupportTicket } from '../types';

export const SupportPage: React.FC = () => {
  const [category, setCategory] = useState<'BOOKING' | 'PAYMENT' | 'CANCELLATION' | 'GENERAL'>('GENERAL');
  const [bookingRef, setBookingRef] = useState('');
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTickets = async () => {
    try {
      const res = await api.get('/support');
      setTickets(res.data);
    } catch (err) {
      console.error("Failed to load support tickets", err);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setSuccess(false);

    try {
      await api.post('/support', {
        category,
        booking_reference: bookingRef || undefined,
        subject,
        message
      });

      setSuccess(true);
      setSubject('');
      setMessage('');
      setBookingRef('');
      fetchTickets();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to submit support ticket");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 flex items-center gap-2">
          <Headphones className="w-6 h-6 text-teal-700" /> 24x7 Customer Support & Help Center
        </h1>
        <p className="text-xs text-slate-500 font-medium mt-1">
          Need assistance with your booking, AP2 payment authorization, or cancellation refund? Submit a support ticket.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
        {/* Support Ticket Submission Form */}
        <div className="md:col-span-7 bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-5">
          <h3 className="font-bold text-slate-900 text-lg border-b border-slate-100 pb-3">Submit Support Ticket</h3>

          {success && (
            <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs p-3.5 rounded-xl font-bold flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Your ticket has been submitted. Our team will respond shortly.
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-xs p-3.5 rounded-xl font-bold flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-600" /> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">Issue Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value as any)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-teal-600 focus:outline-none"
              >
                <option value="GENERAL">General Inquiry</option>
                <option value="BOOKING">Booking Assistance</option>
                <option value="PAYMENT">Payment / AP2 Authorization</option>
                <option value="CANCELLATION">Cancellation & Refund</option>
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
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">Subject</label>
              <input
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="Brief summary of issue"
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-teal-600 focus:outline-none"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">Detailed Message</label>
              <textarea
                rows={4}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Explain your request in detail..."
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
              {isSubmitting ? 'Submitting Ticket...' : 'Submit Support Ticket'}
            </button>
          </form>
        </div>

        {/* Existing Tickets */}
        <div className="md:col-span-5 space-y-4">
          <h3 className="font-bold text-slate-900 text-base">Your Support Tickets</h3>
          {tickets.length === 0 ? (
            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 text-center text-xs text-slate-500">
              No support tickets submitted yet.
            </div>
          ) : (
            <div className="space-y-3">
              {tickets.map((t) => (
                <div key={t.id} className="bg-white border border-slate-200 rounded-2xl p-4 space-y-2 shadow-sm">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-teal-800 bg-teal-50 px-2 py-0.5 rounded">{t.category}</span>
                    <span className="font-bold text-slate-500">{t.status}</span>
                  </div>
                  <div className="font-bold text-slate-900 text-sm">{t.subject}</div>
                  <p className="text-xs text-slate-600">{t.message}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
