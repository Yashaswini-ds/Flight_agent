import React, { useState, useEffect } from 'react';
import { ArrowLeft, UserCheck, Armchair, Luggage, ShieldCheck, CreditCard, AlertCircle } from 'lucide-react';
import { Flight, TravelClass, Seat, Passenger, PaymentResult } from '../types';
import { SeatPicker } from '../components/SeatPicker';
import { FareSummary } from '../components/FareSummary';
import { AP2PaymentModal } from '../components/AP2PaymentModal';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

interface BookingFlowPageProps {
  flight: Flight;
  travelClass: TravelClass;
  travelDate: string;
  passengerCount: number;
  onBack: () => void;
  onBookingSuccess: (bookingId: string) => void;
}

export const BookingFlowPage: React.FC<BookingFlowPageProps> = ({
  flight,
  travelClass,
  travelDate,
  passengerCount,
  onBack,
  onBookingSuccess
}) => {
  const { user } = useAuth();

  const [passengers, setPassengers] = useState<Passenger[]>(() => {
    return Array.from({ length: passengerCount }, (_, i) => ({
      first_name: i === 0 && user ? user.full_name.split(' ')[0] || '' : '',
      last_name: i === 0 && user ? user.full_name.split(' ')[1] || 'Sharma' : '',
      age: 28,
      gender: 'Male',
      seat_number: ''
    }));
  });

  const [availableSeats, setAvailableSeats] = useState<Seat[]>([]);
  const [extraBaggageKg, setExtraBaggageKg] = useState<number>(0);
  const [selectedSeatNumbers, setSelectedSeatNumbers] = useState<string[]>([]);
  
  const [createdBookingId, setCreatedBookingId] = useState<string | null>(null);
  const [createdTotalFare, setCreatedTotalFare] = useState<number>(0);
  const [showPaymentModal, setShowPaymentModal] = useState<boolean>(false);

  const [isLoadingSeats, setIsLoadingSeats] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSeats = async () => {
      try {
        const res = await api.get(`/flights/${flight.id}/seats?travel_class=${travelClass}`);
        setAvailableSeats(res.data);
      } catch (err) {
        console.error("Failed to load seats", err);
      } finally {
        setIsLoadingSeats(false);
      }
    };
    fetchSeats();
  }, [flight.id, travelClass]);

  const handleSeatClick = (seatNumber: string) => {
    if (selectedSeatNumbers.includes(seatNumber)) {
      setSelectedSeatNumbers(selectedSeatNumbers.filter((s) => s !== seatNumber));
    } else {
      if (selectedSeatNumbers.length >= passengerCount) {
        // Replace first
        setSelectedSeatNumbers([...selectedSeatNumbers.slice(1), seatNumber]);
      } else {
        setSelectedSeatNumbers([...selectedSeatNumbers, seatNumber]);
      }
    }
  };

  const fareObj = flight.fares.find((f) => f.travel_class === travelClass) || flight.fares[0];
  
  // Calculate total seat fees
  const seatFeeTotal = selectedSeatNumbers.reduce((acc, sNum) => {
    const seatObj = availableSeats.find((s) => s.seat_number === sNum);
    return acc + (seatObj ? seatObj.price_extra : 0);
  }, 0);

  const baggageFeeTotal = extraBaggageKg * 300;

  const handlePassengerChange = (index: number, field: keyof Passenger, value: any) => {
    const updated = [...passengers];
    updated[index] = { ...updated[index], [field]: value };
    setPassengers(updated);
  };

  const handleCreateDraftBooking = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    // Attach seats to passenger objects
    const finalPassengers = passengers.map((p, idx) => ({
      ...p,
      seat_number: selectedSeatNumbers[idx] || undefined
    }));

    try {
      const res = await api.post('/bookings', {
        flight_id: flight.id,
        travel_class: travelClass,
        travel_date: travelDate,
        passengers: finalPassengers,
        extra_baggage_kg: extraBaggageKg
      });

      setCreatedBookingId(res.data.id);
      setCreatedTotalFare(res.data.total_fare);
      setShowPaymentModal(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create booking draft');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePaymentSuccess = (result: PaymentResult) => {
    setShowPaymentModal(false);
    if (createdBookingId) {
      onBookingSuccess(createdBookingId);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4 border-b border-slate-200 pb-4">
        <button
          onClick={onBack}
          className="p-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900">Passenger & Add-on Details</h1>
          <p className="text-xs text-slate-500 font-medium">
            Flight {flight.flight_number} • {flight.origin_code} to {flight.destination_code} • {travelDate}
          </p>
        </div>
      </div>

      <form onSubmit={handleCreateDraftBooking} className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column - Forms */}
        <div className="lg:col-span-7 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl font-medium flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
              {error}
            </div>
          )}

          {/* Passenger Information */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
            <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
              <UserCheck className="w-5 h-5 text-teal-700" />
              <h3 className="font-bold text-slate-900 text-base">Passenger Details ({passengerCount})</h3>
            </div>

            {passengers.map((p, idx) => (
              <div key={idx} className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-4">
                <div className="text-xs font-bold text-teal-800 uppercase tracking-wider">
                  Passenger {idx + 1}
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold uppercase text-slate-500 mb-1">First Name</label>
                    <input
                      type="text"
                      value={p.first_name}
                      onChange={(e) => handlePassengerChange(idx, 'first_name', e.target.value)}
                      className="w-full bg-white border border-slate-300 rounded-xl px-3.5 py-2 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-teal-600 focus:outline-none"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Last Name</label>
                    <input
                      type="text"
                      value={p.last_name}
                      onChange={(e) => handlePassengerChange(idx, 'last_name', e.target.value)}
                      className="w-full bg-white border border-slate-300 rounded-xl px-3.5 py-2 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-teal-600 focus:outline-none"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Age</label>
                    <input
                      type="number"
                      value={p.age}
                      min={1}
                      max={120}
                      onChange={(e) => handlePassengerChange(idx, 'age', Number(e.target.value))}
                      className="w-full bg-white border border-slate-300 rounded-xl px-3.5 py-2 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-teal-600 focus:outline-none"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Gender</label>
                    <select
                      value={p.gender}
                      onChange={(e) => handlePassengerChange(idx, 'gender', e.target.value)}
                      className="w-full bg-white border border-slate-300 rounded-xl px-3.5 py-2 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-teal-600 focus:outline-none"
                    >
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Seat Picker Section */}
          {!isLoadingSeats && availableSeats.length > 0 && (
            <SeatPicker
              seats={availableSeats}
              selectedSeats={selectedSeatNumbers}
              passengerCount={passengerCount}
              onSeatSelect={handleSeatClick}
            />
          )}

          {/* Extra Baggage Add-on */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center gap-2 border-b border-slate-100 pb-3 mb-4">
              <Luggage className="w-5 h-5 text-teal-700" />
              <h3 className="font-bold text-slate-900 text-base">Check-in Baggage Selection</h3>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-bold text-slate-900">Standard Allowance Included</div>
                <div className="text-xs text-slate-500 font-medium">Check-in {fareObj.baggage_allowance_kg}kg per passenger</div>
              </div>
              <div className="flex items-center gap-3">
                <label className="text-xs font-bold text-slate-600">Extra Baggage:</label>
                <select
                  value={extraBaggageKg}
                  onChange={(e) => setExtraBaggageKg(Number(e.target.value))}
                  className="bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs font-bold text-slate-900"
                >
                  <option value={0}>No Extra Baggage</option>
                  <option value={5}>+5 kg (₹1,500)</option>
                  <option value={10}>+10 kg (₹3,000)</option>
                  <option value={15}>+15 kg (₹4,500)</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Summary & Submit */}
        <div className="lg:col-span-5 space-y-6">
          <FareSummary
            baseFare={fareObj.base_fare}
            passengerCount={passengerCount}
            seatFee={seatFeeTotal}
            baggageFee={baggageFeeTotal}
          />

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-teal-700 hover:bg-teal-800 text-white font-extrabold text-base py-4 rounded-2xl transition-all shadow-lg hover:shadow-teal-700/20 flex items-center justify-center gap-2"
          >
            <ShieldCheck className="w-5 h-5" />
            Proceed to AP2 Payment Simulation
          </button>
        </div>
      </form>

      {/* AP2 Simulated Payment Modal */}
      {showPaymentModal && createdBookingId && (
        <AP2PaymentModal
          bookingId={createdBookingId}
          totalAmount={createdTotalFare}
          onSuccess={handlePaymentSuccess}
          onClose={() => setShowPaymentModal(false)}
        />
      )}
    </div>
  );
};
