import React from 'react';
import { ShieldCheck, Zap, Headphones, ArrowRight, Award, Lock, CheckCircle2, Sparkles } from 'lucide-react';
import { FlightSearchWidget } from '../components/FlightSearchWidget';
import { TravelClass } from '../types';

interface LandingPageProps {
  onSearch: (params: {
    origin: string;
    destination: string;
    travelDate: string;
    passengerCount: number;
    travelClass: TravelClass;
  }) => void;
  onPopularRouteClick: (origin: string, destination: string) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onSearch, onPopularRouteClick }) => {
  return (
    <div className="space-y-10 pb-12">
      {/* Hero Banner Section */}
      <section className="bg-gradient-to-br from-slate-900 via-teal-950 to-slate-900 text-white pt-10 pb-16 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        <div className="max-w-5xl mx-auto text-center relative z-10 space-y-3">
          <div className="inline-flex items-center gap-1.5 bg-teal-800/60 border border-teal-500/30 px-3 py-1 rounded-full text-[11px] font-medium text-teal-300">
            <Sparkles className="w-3 h-3" /> Next-Gen AP2 Protocol Agent Flight Booking
          </div>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold tracking-tight max-w-3xl mx-auto leading-tight">
            Book Flights Across <span className="text-teal-400">5 Major Indian Cities</span>
          </h1>
          <p className="text-slate-300 text-xs sm:text-sm max-w-xl mx-auto font-normal leading-relaxed">
            Seamless AI-driven search between Bengaluru, Chennai, Hyderabad, Mumbai, and Delhi with simulated AP2 payment security.
          </p>
        </div>
      </section>

      {/* Flight Search Widget Container */}
      <div className="px-4 sm:px-6 lg:px-8">
        <FlightSearchWidget onSearch={onSearch} />
      </div>

      {/* Popular Routes Section */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Popular Domestic Routes</h2>
            <p className="text-xs text-slate-500">Frequently booked connections between our 5 hub cities</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { from: 'BLR', to: 'DEL', fromCity: 'Bengaluru', toCity: 'Delhi', price: '₹4,850' },
            { from: 'BOM', to: 'BLR', fromCity: 'Mumbai', toCity: 'Bengaluru', price: '₹3,950' },
            { from: 'MAA', to: 'HYD', fromCity: 'Chennai', toCity: 'Hyderabad', price: '₹3,200' },
            { from: 'DEL', to: 'BOM', fromCity: 'Delhi', toCity: 'Mumbai', price: '₹5,100' },
          ].map((route, idx) => (
            <div
              key={idx}
              onClick={() => onPopularRouteClick(route.from, route.to)}
              className="bg-white border border-slate-200 rounded-xl p-4 hover:border-teal-500 hover:shadow-md transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{route.from} → {route.to}</span>
                <span className="text-[11px] font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded">From {route.price}</span>
              </div>
              <div className="font-semibold text-slate-800 text-sm flex items-center justify-between">
                <span>{route.fromCity}</span>
                <ArrowRight className="w-3.5 h-3.5 text-teal-600 group-hover:translate-x-1 transition-transform" />
                <span>{route.toCity}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Why Choose Platform / Trust Section */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-teal-50/50 rounded-2xl p-6 md:p-8 border border-teal-100">
          <div className="text-center max-w-xl mx-auto mb-6">
            <h2 className="text-lg font-bold text-slate-900">Why Choose FlightAgent?</h2>
            <p className="text-xs text-slate-600 mt-0.5">Built with clean architecture, strict security, and AI agent integration.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs text-center">
              <div className="w-9 h-9 rounded-lg bg-teal-100 text-teal-800 flex items-center justify-center mx-auto mb-3">
                <Zap className="w-4 h-4" />
              </div>
              <h3 className="font-semibold text-slate-900 text-sm mb-1">Dual AI Agents</h3>
              <p className="text-[11px] text-slate-500 leading-relaxed">
                Separated Intent Agent and Booking Agent coordinate natural language requests without arbitrary direct SQL execution.
              </p>
            </div>

            <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs text-center">
              <div className="w-9 h-9 rounded-lg bg-teal-100 text-teal-800 flex items-center justify-center mx-auto mb-3">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <h3 className="font-semibold text-slate-900 text-sm mb-1">AP2 Payment Protocol</h3>
              <p className="text-[11px] text-slate-500 leading-relaxed">
                Simulates Agent Payments Protocol authorization consent tokens, mandates, and immutable transaction audit records.
              </p>
            </div>

            <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs text-center">
              <div className="w-9 h-9 rounded-lg bg-teal-100 text-teal-800 flex items-center justify-center mx-auto mb-3">
                <Award className="w-4 h-4" />
              </div>
              <h3 className="font-semibold text-slate-900 text-sm mb-1">100% Deterministic</h3>
              <p className="text-[11px] text-slate-500 leading-relaxed">
                Fares, configurable demo taxes, extra baggage, seat add-ons, and cancellation refunds are strictly computed by Python algorithms.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
