import React, { useState } from 'react';
import { Search, MapPin, Calendar, Users, Award, ArrowRightLeft } from 'lucide-react';
import { TravelClass } from '../types';

interface FlightSearchWidgetProps {
  onSearch: (searchParams: {
    origin: string;
    destination: string;
    travelDate: string;
    passengerCount: number;
    travelClass: TravelClass;
  }) => void;
}

const CITIES = [
  { code: 'BLR', name: 'Bengaluru / Bangalore' },
  { code: 'MAA', name: 'Chennai' },
  { code: 'HYD', name: 'Hyderabad' },
  { code: 'BOM', name: 'Mumbai' },
  { code: 'DEL', name: 'Delhi' },
];

export const FlightSearchWidget: React.FC<FlightSearchWidgetProps> = ({ onSearch }) => {
  const [origin, setOrigin] = useState('BLR');
  const [destination, setDestination] = useState('DEL');
  const [travelDate, setTravelDate] = useState(() => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  });
  const [passengerCount, setPassengerCount] = useState(1);
  const [travelClass, setTravelClass] = useState<TravelClass>('ECONOMY');
  const [error, setError] = useState<string | null>(null);

  const handleSwap = () => {
    const temp = origin;
    setOrigin(destination);
    setDestination(temp);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (origin === destination) {
      setError('Origin and Destination cities cannot be identical');
      return;
    }
    setError(null);
    onSearch({
      origin,
      destination,
      travelDate,
      passengerCount,
      travelClass,
    });
  };

  return (
    <div className="bg-white rounded-xl shadow-md border border-slate-200 p-4 sm:p-5 max-w-4xl mx-auto -mt-8 relative z-20">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-xs p-2.5 rounded-lg font-medium">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 items-center">
          {/* Origin */}
          <div className="lg:col-span-5 relative">
            <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1 flex items-center gap-1">
              <MapPin className="w-3 h-3 text-teal-600" /> From City
            </label>
            <select
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-800 font-medium text-sm focus:ring-2 focus:ring-teal-600 focus:bg-white focus:outline-none transition-all"
            >
              {CITIES.map((c) => (
                <option key={c.code} value={c.code}>
                  {c.name} ({c.code})
                </option>
              ))}
            </select>
          </div>

          {/* Swap Button */}
          <div className="lg:col-span-2 flex justify-center pt-2 lg:pt-4">
            <button
              type="button"
              onClick={handleSwap}
              className="p-2 bg-teal-50 hover:bg-teal-100 text-teal-700 rounded-full border border-teal-200 shadow-xs transition-all transform hover:rotate-180 duration-300"
              title="Swap From and To cities"
            >
              <ArrowRightLeft className="w-4 h-4" />
            </button>
          </div>

          {/* Destination */}
          <div className="lg:col-span-5 relative">
            <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1 flex items-center gap-1">
              <MapPin className="w-3 h-3 text-teal-600" /> To City
            </label>
            <select
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-800 font-medium text-sm focus:ring-2 focus:ring-teal-600 focus:bg-white focus:outline-none transition-all"
            >
              {CITIES.map((c) => (
                <option key={c.code} value={c.code}>
                  {c.name} ({c.code})
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {/* Travel Date */}
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1 flex items-center gap-1">
              <Calendar className="w-3 h-3 text-teal-600" /> Departure Date
            </label>
            <input
              type="date"
              value={travelDate}
              min={new Date().toISOString().split('T')[0]}
              onChange={(e) => setTravelDate(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-800 font-medium text-sm focus:ring-2 focus:ring-teal-600 focus:bg-white focus:outline-none transition-all"
              required
            />
          </div>

          {/* Passengers */}
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1 flex items-center gap-1">
              <Users className="w-3 h-3 text-teal-600" /> Passengers
            </label>
            <select
              value={passengerCount}
              onChange={(e) => setPassengerCount(Number(e.target.value))}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-800 font-medium text-sm focus:ring-2 focus:ring-teal-600 focus:bg-white focus:outline-none transition-all"
            >
              {[1, 2, 3, 4, 5, 6].map((num) => (
                <option key={num} value={num}>
                  {num} Passenger{num > 1 ? 's' : ''}
                </option>
              ))}
            </select>
          </div>

          {/* Travel Class */}
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1 flex items-center gap-1">
              <Award className="w-3 h-3 text-teal-600" /> Cabin Class
            </label>
            <select
              value={travelClass}
              onChange={(e) => setTravelClass(e.target.value as TravelClass)}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-800 font-medium text-sm focus:ring-2 focus:ring-teal-600 focus:bg-white focus:outline-none transition-all"
            >
              <option value="ECONOMY">Economy</option>
              <option value="PREMIUM_ECONOMY">Premium Economy</option>
              <option value="BUSINESS">Business Class</option>
            </select>
          </div>
        </div>

        <div className="pt-1 flex justify-end">
          <button
            type="submit"
            className="w-full md:w-auto bg-teal-700 hover:bg-teal-800 text-white font-semibold text-xs px-6 py-2.5 rounded-lg transition-all shadow-md hover:shadow-teal-700/20 flex items-center justify-center gap-1.5"
          >
            <Search className="w-4 h-4" />
            Search Available Flights
          </button>
        </div>
      </form>
    </div>
  );
};
