import React, { useState, useEffect } from 'react';
import { Briefcase, Plane, ChevronRight, Calendar, AlertCircle } from 'lucide-react';
import { Booking } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import api from '../services/api';

interface MyTripsPageProps {
  onSelectBooking: (bookingId: string) => void;
}

export const MyTripsPage: React.FC<MyTripsPageProps> = ({ onSelectBooking }) => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [filter, setFilter] = useState<'ALL' | 'UPCOMING' | 'CANCELLED'>('ALL');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchBookings = async () => {
      try {
        const res = await api.get('/bookings');
        setBookings(res.data);
      } catch (err) {
        console.error("Failed to load user trips", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchBookings();
  }, []);

  const filteredBookings = bookings.filter((b) => {
    if (filter === 'UPCOMING') {
      return b.status === 'CONFIRMED' || b.status === 'BOOKED' || b.status === 'PAYMENT_PENDING';
    } else if (filter === 'CANCELLED') {
      return b.status === 'CANCELLED' || b.status === 'REFUNDED' || b.status === 'REFUND_PENDING';
    }
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 flex items-center gap-2">
            <Briefcase className="w-6 h-6 text-teal-700" /> My Trips & Booking History
          </h1>
          <p className="text-xs text-slate-500 font-medium">
            Manage your booked flights, view interactive e-tickets, or modify/cancel bookings.
          </p>
        </div>

        {/* Filters */}
        <div className="flex gap-2 bg-slate-100 p-1 rounded-xl">
          <button
            onClick={() => setFilter('ALL')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
              filter === 'ALL' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            All Bookings ({bookings.length})
          </button>
          <button
            onClick={() => setFilter('UPCOMING')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
              filter === 'UPCOMING' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Upcoming
          </button>
          <button
            onClick={() => setFilter('CANCELLED')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
              filter === 'CANCELLED' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Cancelled / Refunded
          </button>
        </div>
      </div>

      {/* Bookings Compact List */}
      {isLoading ? (
        <div className="py-12 text-center text-sm font-semibold text-slate-500">
          Loading your travel history...
        </div>
      ) : filteredBookings.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center space-y-3">
          <Briefcase className="w-10 h-10 text-slate-300 mx-auto" />
          <h3 className="text-base font-bold text-slate-900">No Trips Found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            You don't have any matching flight bookings in your account history yet.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredBookings.map((b) => (
            <div
              key={b.id}
              onClick={() => onSelectBooking(b.id)}
              className="bg-white border border-slate-200 rounded-2xl p-5 hover:border-teal-500 hover:shadow-md transition-all cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-4 group"
            >
              {/* Left Column: Date & Route */}
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-teal-50 border border-teal-100 text-teal-800 flex items-center justify-center font-bold text-sm shrink-0">
                  <Plane className="w-5 h-5 text-teal-700" />
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-500 flex items-center gap-1.5 mb-0.5">
                    <Calendar className="w-3.5 h-3.5 text-teal-600" />
                    {new Date(b.travel_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                  </div>
                  <div className="text-base font-extrabold text-slate-900">
                    {b.origin_city} ({b.origin_code}) → {b.destination_city} ({b.destination_code})
                  </div>
                  <div className="text-xs text-slate-500 font-medium">
                    Flight: <span className="font-semibold text-slate-700">{b.flight_number}</span> • Class: <span className="font-semibold text-slate-700">{b.travel_class.replace('_', ' ')}</span>
                  </div>
                </div>
              </div>

              {/* Right Column: Status & Price */}
              <div className="flex items-center justify-between sm:justify-end gap-6 border-t sm:border-t-0 border-slate-100 pt-3 sm:pt-0">
                <div className="text-left sm:text-right">
                  <StatusBadge status={b.status} />
                  <div className="text-sm font-extrabold text-slate-900 mt-1">₹{b.total_fare.toLocaleString('en-IN')}</div>
                </div>

                <div className="w-8 h-8 rounded-full bg-slate-50 group-hover:bg-teal-50 text-slate-400 group-hover:text-teal-700 flex items-center justify-center transition-colors">
                  <ChevronRight className="w-5 h-5" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
