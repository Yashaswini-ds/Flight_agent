import React, { useState } from 'react';
import { Plane, User as UserIcon, LogOut, ShieldCheck, HelpCircle, MessageSquare, Briefcase } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  openAuthModal: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, openAuthModal }) => {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-2xs">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-14 items-center">
          {/* Logo */}
          <div 
            onClick={() => setActiveTab('home')}
            className="flex items-center gap-2 cursor-pointer select-none group"
          >
            <div className="w-8 h-8 rounded-lg bg-teal-700 text-white flex items-center justify-center shadow-xs group-hover:bg-teal-600 transition-colors">
              <Plane className="w-4 h-4 transform -rotate-45" />
            </div>
            <div>
              <span className="text-base font-bold tracking-tight text-slate-900">Flight<span className="text-teal-700">Agent</span></span>
              <span className="block text-[9px] uppercase tracking-wider font-medium text-slate-400 -mt-1">GenAI Travel Platform</span>
            </div>
          </div>

          {/* Nav Links */}
          <nav className="hidden md:flex items-center gap-1">
            <button
              onClick={() => setActiveTab('home')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                activeTab === 'home' ? 'bg-teal-50 text-teal-800' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              Search Flights
            </button>
            {user && (
              <button
                onClick={() => setActiveTab('my-trips')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 ${
                  activeTab === 'my-trips' ? 'bg-teal-50 text-teal-800' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <Briefcase className="w-3.5 h-3.5" />
                My Trips
              </button>
            )}
            <button
              onClick={() => setActiveTab('support')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 ${
                activeTab === 'support' ? 'bg-teal-50 text-teal-800' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <HelpCircle className="w-3.5 h-3.5" />
              Support
            </button>
            <button
              onClick={() => setActiveTab('feedback')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 ${
                activeTab === 'feedback' ? 'bg-teal-50 text-teal-800' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5" />
              Feedback
            </button>
            {user && user.role === 'ADMIN' && (
              <button
                onClick={() => setActiveTab('admin')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 bg-amber-50 text-amber-900 hover:bg-amber-100 ${
                  activeTab === 'admin' ? 'ring-2 ring-amber-500' : ''
                }`}
              >
                <ShieldCheck className="w-3.5 h-3.5 text-amber-600" />
                Admin Dashboard
              </button>
            )}
          </nav>

          {/* User Auth Buttons */}
          <div className="flex items-center gap-2">
            {user ? (
              <div className="flex items-center gap-2">
                <div className="text-right hidden sm:block">
                  <div className="text-xs font-bold text-slate-800">{user.full_name}</div>
                  <div className="text-[10px] text-slate-500 flex items-center justify-end gap-1">
                    <span className={`w-1.5 h-1.5 rounded-full ${user.role === 'ADMIN' ? 'bg-amber-500' : 'bg-teal-500'}`}></span>
                    {user.role}
                  </div>
                </div>
                <button
                  onClick={logout}
                  className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <button
                onClick={openAuthModal}
                className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-semibold px-3.5 py-1.5 rounded-lg transition-all shadow-2xs flex items-center gap-1.5"
              >
                <UserIcon className="w-3.5 h-3.5" />
                Sign In
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
