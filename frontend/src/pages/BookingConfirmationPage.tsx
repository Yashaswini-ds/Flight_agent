import React, { useState, useEffect } from 'react';
import { CheckCircle2, Ticket, Briefcase, ArrowRight, ShieldCheck } from 'lucide-react';
import { Booking } from '../types';
import { ETicketModal } from '../components/ETicketModal';
import api from '../services/api';

interface BookingConfirmationPageProps {
  bookingId: string;
  onGoToTrips: () => void;
}

export const BookingConfirmationPage: React.FC<BookingConfirmationPageProps> = ({
  bookingId,
  onGoToTrips
}) => {
  const [booking, setBooking] = useState<Booking | null>(null);
  const [showETicket, setShowETicket] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchBooking = async () => {
      try {
        const res = await api.get(`/bookings/${bookingId}`);
        setBooking(res.data);
      } catch (err) {
        console.error("Failed to load booking details", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchBooking();
  }, [bookingId]);

  if (isLoading || !booking) {
    return (
      <div className="max-w-md mx-auto my-20 p-8 bg-white rounded-2xl border border-slate-200 text-center">
        <div className="w-8 h-8 border-4 border-teal-700 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <div className="font-bold text-slate-900">Finalizing Booking & Generating PNR...</div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <div className="bg-white border border-slate-200 rounded-3xl p-8 md:p-10 shadow-xl text-center space-y-6">
        {/* Success Icon */}
        <div className="w-20 h-20 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto shadow-inner">
          <CheckCircle2 className="w-12 h-12" />
        </div>

        <div className="space-y-2">
          <h1 className="text-3xl font-black text-slate-900">Booking Confirmed!</h1>
          <p className="text-slate-500 text-sm font-medium">
            Your flight ticket has been issued and AP2 payment authorization completed successfully.
          </p>
        </div>

        {/* PNR Code Box */}
        <div className="bg-gradient-to-r from-teal-50 to-emerald-50 border border-teal-200/80 rounded-2xl p-6 max-w-md mx-auto space-y-2">
          <div className="text-xs font-bold text-teal-800 uppercase tracking-widest">Booking Reference / PNR</div>
          <div className="text-4xl font-black text-teal-900 tracking-wider">{booking.pnr}</div>
          <div className="text-xs text-slate-500 font-semibold">Ref Code: {booking.booking_reference}</div>
        </div>

        {/* Flight Details Card */}
        <div className="bg-slate-50 rounded-2xl p-6 border border-slate-200 text-left max-w-lg mx-auto space-y-3">
          <div className="flex justify-between items-center text-sm font-bold text-slate-900">
            <span>{booking.airline_name} ({booking.flight_number})</span>
            <span className="text-teal-700">{booking.travel_class.replace('_', ' ')}</span>
          </div>
          <div className="text-xs text-slate-600 font-medium flex justify-between">
            <span>Route: {booking.origin_city} ({booking.origin_code}) → {booking.destination_city} ({booking.destination_code})</span>
            <span>{new Date(booking.travel_date).toLocaleDateString('en-IN')}</span>
          </div>
          <div className="text-xs text-slate-500 border-t border-slate-200 pt-2 flex justify-between">
            <span>Passengers: {booking.passenger_count} Person(s)</span>
            <span className="font-bold text-slate-900">Paid: ₹{booking.total_fare.toLocaleString('en-IN')}</span>
          </div>
        </div>

        {/* AP2 Verification Badge */}
        <div className="inline-flex items-center gap-1.5 text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-full font-bold">
          <ShieldCheck className="w-4 h-4" /> AP2 Protocol Verified Mandate & Consent Token Issued
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row justify-center gap-4 pt-4">
          <button
            onClick={() => setShowETicket(true)}
            className="bg-teal-700 hover:bg-teal-800 text-white font-bold text-sm px-6 py-3 rounded-xl transition-all shadow-md flex items-center justify-center gap-2"
          >
            <Ticket className="w-4 h-4" /> View E-Ticket
          </button>
          <button
            onClick={onGoToTrips}
            className="bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-sm px-6 py-3 rounded-xl transition-all flex items-center justify-center gap-2"
          >
            <Briefcase className="w-4 h-4" /> View My Trips
          </button>
        </div>
      </div>

      {showETicket && (
        <ETicketModal
          booking={booking}
          onClose={() => setShowETicket(false)}
        />
      )}
    </div>
  );
};
