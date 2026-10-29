import React, { useState } from 'react';
import { FlightCard } from '../components/FlightCard';
import { Flight, TravelClass } from '../types';
import { ArrowLeft, SlidersHorizontal, ArrowUpDown } from 'lucide-react';

interface SearchResultsPageProps {
  flights: Flight[];
  travelClass: TravelClass;
  origin: string;
  destination: string;
  travelDate: string;
  passengerCount: number;
  onBack: () => void;
  onSelectFlight: (flight: Flight) => void;
}

export const SearchResultsPage: React.FC<SearchResultsPageProps> = ({
  flights,
  travelClass,
  origin,
  destination,
  travelDate,
  passengerCount,
  onBack,
  onSelectFlight
}) => {
  const [sortBy, setSortBy] = useState<'price' | 'duration' | 'departure'>('price');

  const sortedFlights = [...flights].sort((a, b) => {
    if (sortBy === 'price') {
      const fareA = a.fares.find((f) => f.travel_class === travelClass)?.base_fare || 0;
      const fareB = b.fares.find((f) => f.travel_class === travelClass)?.base_fare || 0;
      return fareA - fareB;
    } else if (sortBy === 'duration') {
      return a.duration_minutes - b.duration_minutes;
    } else {
      return new Date(a.departure_time).getTime() - new Date(b.departure_time).getTime();
    }
  });

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-4">
      {/* Top Header & Search Summary */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white border border-slate-200 p-3.5 sm:p-4 rounded-xl shadow-xs">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="p-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition-colors"
            title="Modify Search"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-base font-bold text-slate-900 leading-snug">
              {origin} → {destination}
            </h1>
            <p className="text-[11px] text-slate-500 font-medium">
              {new Date(travelDate).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })} • {passengerCount} Passenger(s) • {travelClass.replace('_', ' ')}
            </p>
          </div>
        </div>

        {/* Sort dropdown */}
        <div className="flex items-center gap-2">
          <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-[11px] font-semibold text-slate-500 uppercase">Sort:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="bg-slate-50 border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-semibold text-slate-800 focus:outline-none"
          >
            <option value="price">Cheapest Price</option>
            <option value="duration">Fastest Duration</option>
            <option value="departure">Earliest Departure</option>
          </select>
        </div>
      </div>

      {/* Flight Cards List */}
      {sortedFlights.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-xl p-8 text-center space-y-2.5">
          <div className="text-3xl">✈️</div>
          <h3 className="text-base font-bold text-slate-900">No Flights Available</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            No scheduled flights found for {origin} → {destination} on {travelDate}. Please try selecting a different date or route.
          </p>
          <button
            onClick={onBack}
            className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-semibold px-5 py-2 rounded-lg transition-all"
          >
            Modify Search Criteria
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Showing {sortedFlights.length} Available Flight Option(s)
          </div>
          {sortedFlights.map((flight) => (
            <FlightCard
              key={flight.id}
              flight={flight}
              travelClass={travelClass}
              onSelect={onSelectFlight}
            />
          ))}
        </div>
      )}
    </div>
  );
};
