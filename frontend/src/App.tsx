import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { AuthModal } from './components/AuthModal';
import { AIAssistantWidget } from './components/AIAssistantWidget';

import { LandingPage } from './pages/LandingPage';
import { SearchResultsPage } from './pages/SearchResultsPage';
import { BookingFlowPage } from './pages/BookingFlowPage';
import { BookingConfirmationPage } from './pages/BookingConfirmationPage';
import { MyTripsPage } from './pages/MyTripsPage';
import { BookingDetailsPage } from './pages/BookingDetailsPage';
import { AdminDashboardPage } from './pages/AdminDashboardPage';
import { SupportPage } from './pages/SupportPage';
import { FeedbackPage } from './pages/FeedbackPage';

import { Flight, TravelClass } from './types';
import api from './services/api';

const MainAppContent: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<string>('home');
  const [showAuthModal, setShowAuthModal] = useState<boolean>(false);

  // Search state
  const [searchOrigin, setSearchOrigin] = useState('BLR');
  const [searchDestination, setSearchDestination] = useState('DEL');
  const [searchDate, setSearchDate] = useState(() => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  });
  const [searchPassengers, setSearchPassengers] = useState(1);
  const [searchClass, setSearchClass] = useState<TravelClass>('ECONOMY');
  
  const [searchResults, setSearchResults] = useState<Flight[]>([]);
  const [selectedFlight, setSelectedFlight] = useState<Flight | null>(null);
  const [confirmedBookingId, setConfirmedBookingId] = useState<string | null>(null);
  const [inspectBookingId, setInspectBookingId] = useState<string | null>(null);

  const handleExecuteSearch = async (params: {
    origin: string;
    destination: string;
    travelDate: string;
    passengerCount: number;
    travelClass: TravelClass;
  }) => {
    setSearchOrigin(params.origin);
    setSearchDestination(params.destination);
    setSearchDate(params.travelDate);
    setSearchPassengers(params.passengerCount);
    setSearchClass(params.travelClass);

    try {
      const res = await api.get('/flights/search', {
        params: {
          origin: params.origin,
          destination: params.destination,
          travel_date: params.travelDate,
          passenger_count: params.passengerCount,
          travel_class: params.travelClass
        }
      });
      setSearchResults(res.data);
      setActiveTab('search-results');
    } catch (err) {
      console.error("Flight search failed", err);
    }
  };

  const handlePopularRouteClick = (origin: string, destination: string) => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateStr = tomorrow.toISOString().split('T')[0];

    handleExecuteSearch({
      origin,
      destination,
      travelDate: dateStr,
      passengerCount: 1,
      travelClass: 'ECONOMY'
    });
  };

  const handleSelectFlight = (flight: Flight) => {
    if (!user) {
      setShowAuthModal(true);
      return;
    }
    setSelectedFlight(flight);
    setActiveTab('booking-flow');
  };

  const handleBookingSuccess = (bookingId: string) => {
    setConfirmedBookingId(bookingId);
    setActiveTab('confirmation');
  };

  const handleOpenBookingDetails = (bookingId: string) => {
    setInspectBookingId(bookingId);
    setActiveTab('booking-details');
  };

  return (
    <div className="min-h-screen flex flex-col bg-white text-slate-900 font-sans">
      <Navbar
        activeTab={activeTab}
        setActiveTab={(tab) => {
          setActiveTab(tab);
          if (tab === 'home') {
            setSelectedFlight(null);
          }
        }}
        openAuthModal={() => setShowAuthModal(true)}
      />

      <main className="flex-1">
        {activeTab === 'home' && (
          <LandingPage
            onSearch={handleExecuteSearch}
            onPopularRouteClick={handlePopularRouteClick}
          />
        )}

        {activeTab === 'search-results' && (
          <SearchResultsPage
            flights={searchResults}
            travelClass={searchClass}
            origin={searchOrigin}
            destination={searchDestination}
            travelDate={searchDate}
            passengerCount={searchPassengers}
            onBack={() => setActiveTab('home')}
            onSelectFlight={handleSelectFlight}
          />
        )}

        {activeTab === 'booking-flow' && selectedFlight && (
          <BookingFlowPage
            flight={selectedFlight}
            travelClass={searchClass}
            travelDate={searchDate}
            passengerCount={searchPassengers}
            onBack={() => setActiveTab('search-results')}
            onBookingSuccess={handleBookingSuccess}
          />
        )}

        {activeTab === 'confirmation' && confirmedBookingId && (
          <BookingConfirmationPage
            bookingId={confirmedBookingId}
            onGoToTrips={() => setActiveTab('my-trips')}
          />
        )}

        {activeTab === 'my-trips' && (
          <MyTripsPage
            onSelectBooking={handleOpenBookingDetails}
          />
        )}

        {activeTab === 'booking-details' && inspectBookingId && (
          <BookingDetailsPage
            bookingId={inspectBookingId}
            onBack={() => setActiveTab('my-trips')}
          />
        )}

        {activeTab === 'admin' && (
          <AdminDashboardPage />
        )}

        {activeTab === 'support' && (
          <SupportPage />
        )}

        {activeTab === 'feedback' && (
          <FeedbackPage />
        )}
      </main>

      <Footer />

      {/* Floating AI Assistant */}
      <AIAssistantWidget
        onSelectFlightFromAgent={(flight) => {
          handleSelectFlight(flight);
        }}
        onSearchFlightsFromAgent={(flights) => {
          setSearchResults(flights);
          setActiveTab('search-results');
        }}
      />


      {/* Auth Modal */}
      {showAuthModal && (
        <AuthModal onClose={() => setShowAuthModal(false)} />
      )}
    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <MainAppContent />
    </AuthProvider>
  );
}

export default App;
