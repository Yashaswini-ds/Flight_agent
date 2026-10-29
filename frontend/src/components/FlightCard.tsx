import React from 'react';
import { Plane, Clock, Luggage, CheckCircle2, ShieldAlert } from 'lucide-react';
import { Flight, TravelClass } from '../types';

interface FlightCardProps {
  flight: Flight;
  travelClass: TravelClass;
  onSelect: (flight: Flight) => void;
}

export const FlightCard: React.FC<FlightCardProps> = ({ flight, travelClass, onSelect }) => {
  const fare = flight.fares.find((f) => f.travel_class === travelClass) || flight.fares[0];

  const depTime = new Date(flight.departure_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const arrTime = new Date(flight.arrival_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 shadow-sm hover:shadow-md transition-all hover:border-teal-300">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Airline Info */}
        <div className="flex items-center gap-3 min-w-[160px]">
          <div className="w-10 h-10 rounded-lg bg-teal-50 border border-teal-100 text-teal-700 flex items-center justify-center font-bold text-sm shadow-xs">
            {flight.airline_code}
          </div>
          <div>
            <h3 className="font-semibold text-slate-800 text-sm leading-snug">{flight.airline_name}</h3>
            <span className="text-[11px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
              {flight.flight_number}
            </span>
          </div>
        </div>

        {/* Flight Time & Route */}
        <div className="flex-1 flex items-center justify-between gap-3 max-w-sm">
          <div className="text-left min-w-[70px]">
            <div className="text-lg font-bold text-slate-900 leading-tight">{depTime}</div>
            <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-tight">{flight.origin_code} • {flight.origin_city}</div>
          </div>

          <div className="flex-1 flex flex-col items-center px-2">
            <span className="text-[11px] font-medium text-slate-400 flex items-center gap-1 mb-0.5">
              <Clock className="w-3 h-3 text-teal-600" />
              {Math.floor(flight.duration_minutes / 60)}h {flight.duration_minutes % 60}m
            </span>
            <div className="w-full flex items-center gap-1.5">
              <div className="h-0.5 bg-slate-200 flex-1 relative">
                <div className="w-1.5 h-1.5 rounded-full bg-teal-600 absolute left-0 -top-0.5"></div>
              </div>
              <Plane className="w-3.5 h-3.5 text-teal-600 transform rotate-90" />
              <div className="h-0.5 bg-slate-200 flex-1 relative">
                <div className="w-1.5 h-1.5 rounded-full bg-teal-600 absolute right-0 -top-0.5"></div>
              </div>
            </div>
            <span className="text-[10px] font-medium text-emerald-600 mt-0.5">
              {flight.stops === 0 ? 'Direct Non-Stop' : `${flight.stops} Stop`}
            </span>
          </div>

          <div className="text-right min-w-[70px]">
            <div className="text-lg font-bold text-slate-900 leading-tight">{arrTime}</div>
            <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-tight">{flight.destination_code} • {flight.destination_city}</div>
          </div>
        </div>

        {/* Baggage & Pricing */}
        <div className="flex md:flex-col items-end justify-between md:justify-center border-t md:border-t-0 md:border-l border-slate-100 pt-3 md:pt-0 md:pl-5 gap-3">
          <div className="text-right">
            <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">{travelClass.replace('_', ' ')}</div>
            <div className="text-xl font-extrabold text-teal-700">₹{fare.base_fare.toLocaleString('en-IN')}</div>
            <div className="text-[10px] text-slate-400 font-medium flex items-center justify-end gap-1 mt-0.5">
              <Luggage className="w-3 h-3 text-teal-600" />
              {fare.baggage_allowance_kg}kg Check-in
            </div>
          </div>

          <button
            onClick={() => onSelect(flight)}
            className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-semibold px-4 py-2 rounded-lg transition-all shadow-xs flex items-center gap-1"
          >
            Select Flight
          </button>
        </div>
      </div>
    </div>
  );
};
