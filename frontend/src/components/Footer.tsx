import React from 'react';
import { Plane, ShieldCheck, Lock, Headphones, CreditCard } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-900 text-slate-400 pt-12 pb-8 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 pb-8 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2 text-white mb-4">
              <div className="w-8 h-8 rounded-lg bg-teal-600 flex items-center justify-center">
                <Plane className="w-5 h-5 text-white transform -rotate-45" />
              </div>
              <span className="text-lg font-bold">Flight<span className="text-teal-400">Agent</span></span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed mb-4">
              Next-generation AI-assisted flight booking platform connecting 5 major Indian tech and financial hubs.
            </p>
            <div className="flex items-center gap-2 text-xs text-teal-400 bg-slate-800/80 p-2.5 rounded-lg border border-slate-700">
              <ShieldCheck className="w-4 h-4" />
              AP2 Protocol Payment Simulation Enabled
            </div>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">Predefined Cities</h4>
            <ul className="space-y-2 text-sm">
              <li>1. Bengaluru / Bangalore (BLR)</li>
              <li>2. Chennai (MAA)</li>
              <li>3. Hyderabad (HYD)</li>
              <li>4. Mumbai (BOM)</li>
              <li>5. Delhi (DEL)</li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">Travel Classes</h4>
            <ul className="space-y-2 text-sm">
              <li>• Economy Class</li>
              <li>• Premium Economy</li>
              <li>• Business Class</li>
              <li>• Interactive Seat Map Selection</li>
              <li>• Deterministic Refund Calculation</li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">Safety & Trust</h4>
            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-2">
                <Lock className="w-4 h-4 text-teal-400" />
                <span>JWT RBAC Protected</span>
              </div>
              <div className="flex items-center gap-2">
                <CreditCard className="w-4 h-4 text-teal-400" />
                <span>Demo Payment Sandbox (AP2)</span>
              </div>
              <div className="flex items-center gap-2">
                <Headphones className="w-4 h-4 text-teal-400" />
                <span>24x7 Customer Support</span>
              </div>
            </div>
          </div>
        </div>

        <div className="pt-6 flex flex-col md:flex-row items-center justify-between text-xs text-slate-500 gap-4">
          <p>© 2026 FlightAgent Platform. Built for Hands-on Practice Project – 2.</p>
          <p className="italic">Demo environment only. No real financial transactions processed.</p>
        </div>
      </div>
    </footer>
  );
};
