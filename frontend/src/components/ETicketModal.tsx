import React from 'react';
import { Plane, CheckCircle2, QrCode, Download, Printer, UserCheck, Calendar, Luggage } from 'lucide-react';
import { Booking } from '../types';

interface ETicketModalProps {
  booking: Booking;
  onClose: () => void;
}

export const ETicketModal: React.FC<ETicketModalProps> = ({ booking, onClose }) => {
  const handlePrint = () => {
    window.print();
  };

  const depTime = new Date(booking.departure_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const arrTime = new Date(booking.arrival_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const travelDateFormatted = new Date(booking.travel_date).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  });

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl max-w-lg w-full p-4 sm:p-5 shadow-xl border border-slate-200 relative my-6">
        {/* Header bar */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4 print:hidden">
          <div className="flex items-center gap-2">
            <span className="bg-emerald-100 text-emerald-800 text-[11px] font-bold px-2.5 py-0.5 rounded-full flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" /> CONFIRMED E-TICKET
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handlePrint}
              className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold px-2.5 py-1.5 rounded-lg transition-all flex items-center gap-1"
            >
              <Printer className="w-3.5 h-3.5" /> Print
            </button>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-slate-600 text-lg font-bold px-1.5"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Ticket Container */}
        <div className="border border-teal-600/30 rounded-xl p-4 bg-gradient-to-b from-teal-50/30 to-white relative overflow-hidden space-y-4">
          {/* Top Brand Banner */}
          <div className="flex items-center justify-between pb-4 border-b border-slate-200">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-lg bg-teal-700 text-white flex items-center justify-center font-bold text-sm">
                {booking.flight_number.substring(0, 2)}
              </div>
              <div>
                <h2 className="text-sm font-bold text-slate-900 leading-tight">{booking.airline_name}</h2>
                <div className="text-[11px] font-medium text-slate-500">Flight: {booking.flight_number}</div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">PNR CODE</div>
              <div className="text-lg font-extrabold text-teal-800 tracking-wider">{booking.pnr}</div>
              <div className="text-[10px] text-slate-500 font-medium">Ref: {booking.booking_reference}</div>
            </div>
          </div>

          {/* Route & Times */}
          <div className="grid grid-cols-3 gap-2 py-3 border-b border-slate-200 text-center items-center">
            <div className="text-left">
              <div className="text-[10px] font-bold text-teal-700 uppercase">{booking.origin_city}</div>
              <div className="text-xl font-black text-slate-900 leading-tight">{booking.origin_code}</div>
              <div className="text-xs font-bold text-slate-600">{depTime}</div>
            </div>

            <div className="flex flex-col items-center">
              <span className="text-[10px] font-semibold text-slate-500 flex items-center gap-1 mb-0.5">
                <Calendar className="w-3 h-3 text-teal-600" />
                {travelDateFormatted}
              </span>
              <div className="w-full flex items-center gap-1">
                <div className="h-0.5 bg-slate-300 flex-1"></div>
                <Plane className="w-3.5 h-3.5 text-teal-700 transform rotate-90" />
                <div className="h-0.5 bg-slate-300 flex-1"></div>
              </div>
              <span className="text-[10px] font-bold text-slate-500 uppercase mt-0.5">
                {booking.travel_class.replace('_', ' ')}
              </span>
            </div>

            <div className="text-right">
              <div className="text-[10px] font-bold text-teal-700 uppercase">{booking.destination_city}</div>
              <div className="text-xl font-black text-slate-900 leading-tight">{booking.destination_code}</div>
              <div className="text-xs font-bold text-slate-600">{arrTime}</div>
            </div>
          </div>

          {/* Passenger Details */}
          <div className="py-2 border-b border-slate-200">
            <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1">
              <UserCheck className="w-3.5 h-3.5 text-teal-600" /> Passenger Information
            </h4>
            <div className="space-y-1.5">
              {booking.passengers.map((p, idx) => (
                <div key={idx} className="bg-white p-2 rounded-lg border border-slate-200 flex justify-between items-center text-xs font-semibold text-slate-800">
                  <div>
                    <span>{idx + 1}. {p.first_name} {p.last_name}</span>
                    <span className="text-[10px] text-slate-500 ml-1.5">({p.gender}, {p.age} yrs)</span>
                  </div>
                  <div className="text-right">
                    <span className="bg-teal-50 text-teal-800 text-[10px] px-2 py-0.5 rounded border border-teal-200 font-bold">
                      Seat: {p.seat_number || 'Auto-Assigned'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Payment & QR Footer */}
          <div className="pt-2 flex justify-between items-center">
            <div>
              <div className="text-[10px] text-slate-400 font-medium">Total Paid</div>
              <div className="text-lg font-bold text-slate-900">₹{booking.total_fare.toLocaleString('en-IN')}</div>
              <div className="text-[10px] text-emerald-600 font-semibold">✓ AP2 Verified Transaction</div>
            </div>

            <div className="flex items-center gap-2">
              <div className="p-1.5 bg-white rounded-lg border border-slate-200 shadow-2xs">
                <QrCode className="w-9 h-9 text-slate-800" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
