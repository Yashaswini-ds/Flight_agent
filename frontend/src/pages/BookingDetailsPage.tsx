import React, { useState, useEffect } from 'react';
import { ArrowLeft, Ticket, AlertCircle, Ban, RefreshCcw, ShieldCheck, User, Calendar, Luggage, CheckCircle2 } from 'lucide-react';
import { Booking, RefundResult } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { ETicketModal } from '../components/ETicketModal';
import api from '../services/api';

interface BookingDetailsPageProps {
  bookingId: string;
  onBack: () => void;
}

export const BookingDetailsPage: React.FC<BookingDetailsPageProps> = ({ bookingId, onBack }) => {
  const [booking, setBooking] = useState<Booking | null>(null);
  const [showETicket, setShowETicket] = useState(false);
  const [refundResult, setRefundResult] = useState<RefundResult | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isCancelling, setIsCancelling] = useState(false);
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchBooking = async () => {
    try {
      const res = await api.get(`/bookings/${bookingId}`);
      setBooking(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load booking");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBooking();
  }, [bookingId]);

  const handleCancelBooking = async () => {
    setIsCancelling(true);
    setError(null);
    try {
      const res = await api.post(`/bookings/${bookingId}/cancel`);
      setRefundResult(res.data);
      setShowCancelConfirm(false);
      await fetchBooking();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to cancel booking");
    } finally {
      setIsCancelling(false);
    }
  };

  if (isLoading || !booking) {
    return (
      <div className="max-w-md mx-auto my-20 p-8 bg-white rounded-2xl border border-slate-200 text-center">
        <div className="w-8 h-8 border-4 border-teal-700 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <div className="font-bold text-slate-900">Loading Booking Details...</div>
      </div>
    );
  }

  const isEligibleForCancel = booking.status === 'CONFIRMED' || booking.status === 'BOOKED';

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Navigation Header */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="p-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-extrabold text-slate-900 flex items-center gap-3">
              Booking Details
              <StatusBadge status={booking.status} />
            </h1>
            <p className="text-xs text-slate-500 font-medium">Ref: {booking.booking_reference}</p>
          </div>
        </div>

        <button
          onClick={() => setShowETicket(true)}
          className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold px-4 py-2.5 rounded-xl transition-all flex items-center gap-1.5 shadow-sm"
        >
          <Ticket className="w-4 h-4" /> View E-Ticket
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl font-medium flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
          {error}
        </div>
      )}

      {/* PNR Summary Header */}
      <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm flex flex-col md:flex-row justify-between items-center gap-6">
        <div>
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">AIRLINE & FLIGHT</div>
          <div className="text-xl font-black text-slate-900">{booking.airline_name} ({booking.flight_number})</div>
          <div className="text-xs text-slate-500 font-semibold mt-1">
            {booking.origin_city} ({booking.origin_code}) → {booking.destination_city} ({booking.destination_code})
          </div>
        </div>

        <div className="text-center md:text-right bg-teal-50 border border-teal-100 p-4 rounded-2xl min-w-[180px]">
          <div className="text-[11px] font-bold text-teal-800 uppercase tracking-widest">PNR CODE</div>
          <div className="text-3xl font-black text-teal-900 tracking-wider">{booking.pnr}</div>
        </div>
      </div>

      {/* Passenger & Seat Info */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
        <h3 className="font-bold text-slate-900 text-base border-b border-slate-100 pb-3 flex items-center gap-2">
          <User className="w-4 h-4 text-teal-700" /> Passenger Details
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {booking.passengers.map((p, idx) => (
            <div key={idx} className="bg-slate-50 border border-slate-200 p-4 rounded-xl flex justify-between items-center">
              <div>
                <div className="font-bold text-slate-900 text-sm">{p.first_name} {p.last_name}</div>
                <div className="text-xs text-slate-500">{p.gender}, {p.age} years old</div>
              </div>
              <div className="text-xs font-bold bg-white text-teal-800 px-2.5 py-1 rounded-md border border-slate-200">
                Seat: {p.seat_number || 'N/A'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Itemized Fare & Payment Audit */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
        <h3 className="font-bold text-slate-900 text-base border-b border-slate-100 pb-3">Financial Fare Breakdown</h3>
        <div className="space-y-2 text-xs sm:text-sm text-slate-600">
          <div className="flex justify-between">
            <span>Base Fare</span>
            <span className="font-semibold text-slate-900">₹{booking.base_fare.toLocaleString('en-IN')}</span>
          </div>
          {booking.seat_addons_fee > 0 && (
            <div className="flex justify-between">
              <span>Seat Selection Fee</span>
              <span className="font-semibold text-slate-900">₹{booking.seat_addons_fee.toLocaleString('en-IN')}</span>
            </div>
          )}
          {booking.baggage_addons_fee > 0 && (
            <div className="flex justify-between">
              <span>Extra Baggage Fee</span>
              <span className="font-semibold text-slate-900">₹{booking.baggage_addons_fee.toLocaleString('en-IN')}</span>
            </div>
          )}
          <div className="flex justify-between">
            <span>Demo Tax</span>
            <span className="font-semibold text-slate-900">₹{booking.taxes.toLocaleString('en-IN')}</span>
          </div>
          <div className="flex justify-between border-t border-slate-200 pt-2 font-bold text-sm text-slate-900">
            <span>Total Fare</span>
            <span className="text-teal-800 text-lg">₹{booking.total_fare.toLocaleString('en-IN')}</span>
          </div>
        </div>
      </div>

      {/* Cancel Booking Section */}
      {isEligibleForCancel && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
          <h3 className="font-bold text-slate-900 text-base text-red-700 flex items-center gap-2">
            <Ban className="w-4 h-4 text-red-600" /> Cancel Booking & Process Refund
          </h3>
          <p className="text-xs text-slate-500">
            Deterministic cancellation fee is applied based on departure time rules. The net refund will be calculated and processed immediately to your simulated AP2 account.
          </p>

          {!showCancelConfirm ? (
            <button
              onClick={() => setShowCancelConfirm(true)}
              className="bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 text-xs font-bold px-4 py-2.5 rounded-xl transition-colors"
            >
              Cancel Booking
            </button>
          ) : (
            <div className="bg-red-50/70 border border-red-200 p-4 rounded-xl space-y-3">
              <div className="text-xs font-bold text-red-900">Are you sure you want to cancel this booking?</div>
              <div className="flex gap-2">
                <button
                  onClick={handleCancelBooking}
                  disabled={isCancelling}
                  className="bg-red-600 hover:bg-red-700 text-white text-xs font-bold px-4 py-2 rounded-lg transition-colors"
                >
                  {isCancelling ? 'Processing Refund...' : 'Yes, Confirm Cancellation'}
                </button>
                <button
                  onClick={() => setShowCancelConfirm(false)}
                  className="bg-white text-slate-700 border border-slate-300 text-xs font-bold px-4 py-2 rounded-lg"
                >
                  Keep Booking
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Refund Result Display */}
      {refundResult && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-6 space-y-2">
          <div className="text-sm font-bold text-emerald-900 flex items-center gap-1.5">
            <CheckCircle2 className="w-5 h-5 text-emerald-600" /> Simulated Refund Processed Successfully!
          </div>
          <div className="text-xs text-emerald-800">
            Refund Ref: <span className="font-bold">{refundResult.refund_reference}</span> • Gross Amount: ₹{refundResult.gross_amount} • Cancellation Fee: ₹{refundResult.cancellation_fee} • <span className="font-bold">Net Refund: ₹{refundResult.net_refund_amount}</span>
          </div>
        </div>
      )}

      {showETicket && (
        <ETicketModal
          booking={booking}
          onClose={() => setShowETicket(false)}
        />
      )}
    </div>
  );
};
