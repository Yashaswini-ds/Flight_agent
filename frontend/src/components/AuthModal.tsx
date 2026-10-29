import React, { useState } from 'react';
import { User, Lock, Mail, Phone, ShieldCheck, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

interface AuthModalProps {
  onClose: () => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ onClose }) => {
  const { login } = useAuth();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      if (isRegister) {
        const res = await api.post('/auth/register', {
          email,
          password,
          full_name: fullName,
          phone: phone || undefined
        });
        login(res.data.access_token, res.data.role, res.data.user_id, res.data.full_name);
        onClose();
      } else {
        const res = await api.post('/auth/login', {
          email,
          password
        });
        login(res.data.access_token, res.data.role, res.data.user_id, res.data.full_name);
        onClose();
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed');
    } finally {
      setIsLoading(false);
    }
  };

  const fillDemoUser = () => {
    setEmail('user@flightagent.com');
    setPassword('user123');
    setIsRegister(false);
  };

  const fillDemoAdmin = () => {
    setEmail('admin@flightagent.com');
    setPassword('admin123');
    setIsRegister(false);
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl max-w-md w-full p-6 md:p-8 shadow-2xl border border-slate-200 relative">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-6">
          <h3 className="font-extrabold text-slate-900 text-xl">
            {isRegister ? 'Create Account' : 'Sign In to FlightAgent'}
          </h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-xl font-bold p-1">
            ✕
          </button>
        </div>

        {/* Demo Fast Login Buttons */}
        {!isRegister && (
          <div className="bg-slate-50 border border-slate-200 p-3 rounded-2xl mb-5 space-y-2">
            <div className="text-[11px] font-bold uppercase text-slate-400 tracking-wider">Fast Demo Accounts:</div>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={fillDemoUser}
                className="bg-white hover:bg-teal-50 border border-slate-200 text-teal-800 text-xs font-bold py-2 rounded-xl transition-colors shadow-sm"
              >
                Demo User
              </button>
              <button
                type="button"
                onClick={fillDemoAdmin}
                className="bg-amber-50 hover:bg-amber-100 border border-amber-200 text-amber-900 text-xs font-bold py-2 rounded-xl transition-colors shadow-sm"
              >
                Demo Admin
              </button>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-xs p-3 rounded-xl font-medium">
              {error}
            </div>
          )}

          {isRegister && (
            <div>
              <label className="block text-xs font-bold uppercase text-slate-500 mb-1 flex items-center gap-1">
                <User className="w-3.5 h-3.5 text-teal-600" /> Full Name
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-teal-600 focus:outline-none"
                required
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-bold uppercase text-slate-500 mb-1 flex items-center gap-1">
              <Mail className="w-3.5 h-3.5 text-teal-600" /> Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-teal-600 focus:outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-bold uppercase text-slate-500 mb-1 flex items-center gap-1">
              <Lock className="w-3.5 h-3.5 text-teal-600" /> Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-teal-600 focus:outline-none"
              required
            />
          </div>

          {isRegister && (
            <div>
              <label className="block text-xs font-bold uppercase text-slate-500 mb-1 flex items-center gap-1">
                <Phone className="w-3.5 h-3.5 text-teal-600" /> Phone Number (Optional)
              </label>
              <input
                type="text"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-teal-600 focus:outline-none"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-teal-700 hover:bg-teal-800 text-white font-bold py-3.5 rounded-xl transition-all shadow-lg flex items-center justify-center gap-2 text-sm"
          >
            {isLoading ? 'Processing...' : isRegister ? 'Create Account' : 'Sign In'}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-5 text-center text-xs text-slate-500">
          {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
          <button
            onClick={() => {
              setIsRegister(!isRegister);
              setError(null);
            }}
            className="text-teal-700 font-bold underline"
          >
            {isRegister ? 'Sign In' : 'Register now'}
          </button>
        </div>
      </div>
    </div>
  );
};
