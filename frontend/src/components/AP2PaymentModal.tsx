import React, { useState } from 'react';
import { ShieldCheck, CreditCard, QrCode, Smartphone, Lock, AlertTriangle, CheckCircle } from 'lucide-react';
import api from '../services/api';
import { PaymentMethod, PaymentResult } from '../types';

interface AP2PaymentModalProps {
  bookingId: string;
  totalAmount: number;
  onSuccess: (result: PaymentResult) => void;
  onClose: () => void;
}

export const AP2PaymentModal: React.FC<AP2PaymentModalProps> = ({
  bookingId,
  totalAmount,
  onSuccess,
  onClose
}) => {
  const [method, setMethod] = useState<PaymentMethod>('UPI');
  const [demoIdentifier, setDemoIdentifier] = useState('demo@upi');
  const [demoPin, setDemoPin] = useState('1234');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePayment = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      // Step 1: Create AP2 Payment Intent
      const intentRes = await api.post('/payments/intent', {
        booking_id: bookingId,
        payment_method: method
      });

      const intentId = intentRes.data.payment_intent_id;

      // Step 2: Execute AP2 Payment Authorization
      const executeRes = await api.post('/payments/execute', {
        payment_intent_id: intentId,
        payment_method: method,
        demo_pin_or_auth: demoPin,
        demo_identifier: demoIdentifier
      });

      onSuccess(executeRes.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Payment authorization failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl max-w-lg w-full p-6 md:p-8 shadow-2xl border border-slate-100 relative">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-6">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-teal-100 text-teal-800 flex items-center justify-center">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-lg">AP2 Payment Simulation</h3>
              <p className="text-xs text-slate-500 font-medium">Agent Payments Protocol Sandbox</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 text-xl font-bold p-1"
          >
            ✕
          </button>
        </div>

        {/* Demo Warning Banner */}
        <div className="bg-amber-50 border border-amber-200 text-amber-900 text-xs p-3.5 rounded-xl mb-6 flex items-start gap-2.5">
          <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">DEMO PAYMENT ENVIRONMENT ONLY.</span> Do NOT enter real credit cards, UPI PINs, or sensitive financial data.
          </div>
        </div>

        <form onSubmit={handlePayment} className="space-y-5">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-xs p-3 rounded-xl">
              {error}
            </div>
          )}

          {/* Payment Method Selector */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Select Demo Method</label>
            <div className="grid grid-cols-3 gap-2.5">
              <button
                type="button"
                onClick={() => {
                  setMethod('UPI');
                  setDemoIdentifier('user@upi');
                }}
                className={`py-3 px-2 rounded-xl text-xs font-bold border transition-all flex flex-col items-center gap-1.5 ${
                  method === 'UPI' ? 'bg-teal-50 border-teal-600 text-teal-900 shadow-sm' : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                <Smartphone className="w-4 h-4" />
                UPI Payment
              </button>
              <button
                type="button"
                onClick={() => {
                  setMethod('QR');
                  setDemoIdentifier('flightagent-ap2-qr');
                }}
                className={`py-3 px-2 rounded-xl text-xs font-bold border transition-all flex flex-col items-center gap-1.5 ${
                  method === 'QR' ? 'bg-teal-50 border-teal-600 text-teal-900 shadow-sm' : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                <QrCode className="w-4 h-4" />
                QR Code
              </button>
              <button
                type="button"
                onClick={() => {
                  setMethod('CARD');
                  setDemoIdentifier('4111222233334444');
                }}
                className={`py-3 px-2 rounded-xl text-xs font-bold border transition-all flex flex-col items-center gap-1.5 ${
                  method === 'CARD' ? 'bg-teal-50 border-teal-600 text-teal-900 shadow-sm' : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                <CreditCard className="w-4 h-4" />
                Demo Card
              </button>
            </div>
          </div>

          {/* Identifier Input */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
              Demo {method === 'UPI' ? 'UPI ID' : method === 'CARD' ? 'Card Number' : 'QR Identifier'}
            </label>
            <input
              type="text"
              value={demoIdentifier}
              onChange={(e) => setDemoIdentifier(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-teal-600 focus:outline-none"
              required
            />
          </div>

          {/* Demo Authorization PIN */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1 flex items-center gap-1">
              <Lock className="w-3.5 h-3.5 text-teal-600" /> AP2 Mandate Consent PIN (Use "1234")
            </label>
            <input
              type="password"
              value={demoPin}
              onChange={(e) => setDemoPin(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-teal-600 focus:outline-none"
              required
            />
          </div>

          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 flex justify-between items-center">
            <span className="text-xs font-bold text-slate-600 uppercase">Amount Due</span>
            <span className="text-xl font-black text-teal-800">₹{totalAmount.toLocaleString('en-IN')}</span>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-teal-700 hover:bg-teal-800 text-white font-bold py-3.5 rounded-xl transition-all shadow-lg flex items-center justify-center gap-2 text-base"
          >
            {isLoading ? 'Authorizing AP2 Consent Token...' : 'Authorize Demo Payment'}
          </button>
        </form>
      </div>
    </div>
  );
};
