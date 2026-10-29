import React from 'react';
import { Receipt, Info } from 'lucide-react';

interface FareSummaryProps {
  baseFare: number;
  passengerCount: number;
  seatFee: number;
  baggageFee: number;
  demoTaxRate?: number;
}

export const FareSummary: React.FC<FareSummaryProps> = ({
  baseFare,
  passengerCount,
  seatFee,
  baggageFee,
  demoTaxRate = 18.0
}) => {
  const totalBase = baseFare * passengerCount;
  const subtotal = totalBase + seatFee + baggageFee;
  const taxes = Math.round(subtotal * (demoTaxRate / 100.0));
  const grandTotal = subtotal + taxes;

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
      <div className="flex items-center gap-2 border-b border-slate-100 pb-4 mb-4">
        <Receipt className="w-5 h-5 text-teal-700" />
        <h3 className="font-bold text-slate-900 text-lg">Fare Breakdown</h3>
      </div>

      <div className="space-y-3 text-sm text-slate-600">
        <div className="flex justify-between">
          <span>Base Fare ({passengerCount} x ₹{baseFare.toLocaleString('en-IN')})</span>
          <span className="font-semibold text-slate-900">₹{totalBase.toLocaleString('en-IN')}</span>
        </div>

        {seatFee > 0 && (
          <div className="flex justify-between">
            <span>Seat Selection Add-on</span>
            <span className="font-semibold text-slate-900">₹{seatFee.toLocaleString('en-IN')}</span>
          </div>
        )}

        {baggageFee > 0 && (
          <div className="flex justify-between">
            <span>Extra Baggage Add-on</span>
            <span className="font-semibold text-slate-900">₹{baggageFee.toLocaleString('en-IN')}</span>
          </div>
        )}

        <div className="flex justify-between items-center text-xs text-slate-500 pt-1">
          <span className="flex items-center gap-1" title="Configurable demo tax for simulation">
            Simulated Demo Tax ({demoTaxRate}%)
            <Info className="w-3.5 h-3.5 text-slate-400" />
          </span>
          <span className="font-semibold text-slate-900">₹{taxes.toLocaleString('en-IN')}</span>
        </div>

        <div className="border-t border-slate-200 pt-4 mt-2 flex justify-between items-center">
          <span className="font-bold text-slate-900 text-base">Total Fare Amount</span>
          <span className="font-black text-2xl text-teal-800">₹{grandTotal.toLocaleString('en-IN')}</span>
        </div>
      </div>
    </div>
  );
};
