import React from 'react';
import { Seat, TravelClass } from '../types';

interface SeatPickerProps {
  seats: Seat[];
  selectedSeats: string[];
  passengerCount: number;
  onSeatSelect: (seatNumber: string) => void;
}

export const SeatPicker: React.FC<SeatPickerProps> = ({
  seats,
  selectedSeats,
  passengerCount,
  onSeatSelect
}) => {
  return (
    <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h4 className="font-bold text-slate-900 text-base">Select Seat(s)</h4>
          <p className="text-xs text-slate-500">
            Selected: <span className="font-bold text-teal-700">{selectedSeats.join(', ') || 'None'}</span> (Need {passengerCount})
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs font-semibold">
          <div className="flex items-center gap-1.5">
            <span className="w-4 h-4 rounded bg-white border border-slate-300"></span> Available
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-4 h-4 rounded bg-teal-600 text-white"></span> Selected
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-4 h-4 rounded bg-slate-300 cursor-not-allowed"></span> Booked
          </div>
        </div>
      </div>

      <div className="grid grid-cols-6 gap-2.5 max-w-sm mx-auto bg-white p-4 rounded-xl border border-slate-200 shadow-inner">
        {seats.map((seat) => {
          const isSelected = selectedSeats.includes(seat.seat_number);
          const isBooked = seat.is_booked;

          return (
            <button
              key={seat.id}
              disabled={isBooked}
              onClick={() => onSeatSelect(seat.seat_number)}
              className={`h-10 rounded-lg text-xs font-bold transition-all flex flex-col items-center justify-center ${
                isBooked
                  ? 'bg-slate-200 text-slate-400 cursor-not-allowed border border-slate-300'
                  : isSelected
                  ? 'bg-teal-700 text-white shadow-md ring-2 ring-teal-600 scale-105'
                  : 'bg-white text-slate-700 hover:bg-teal-50 border border-slate-300 hover:border-teal-400'
              }`}
            >
              <span>{seat.seat_number}</span>
              {seat.price_extra > 0 && !isSelected && !isBooked && (
                <span className="text-[9px] text-teal-600 font-semibold">+₹{seat.price_extra}</span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};
