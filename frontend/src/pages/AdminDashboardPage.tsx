import React, { useState, useEffect } from 'react';
import { ShieldCheck, Users, Plane, Briefcase, CreditCard, MessageSquare, Headphones, RefreshCcw } from 'lucide-react';
import api from '../services/api';
import { StatusBadge } from '../components/StatusBadge';

export const AdminDashboardPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'bookings' | 'support' | 'feedback'>('overview');
  const [stats, setStats] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [bookings, setBookings] = useState<any[]>([]);
  const [tickets, setTickets] = useState<any[]>([]);
  const [feedback, setFeedback] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchAdminData = async () => {
    setIsLoading(true);
    try {
      const [statsRes, usersRes, bookingsRes, ticketsRes, feedbackRes] = await Promise.all([
        api.get('/admin/overview'),
        api.get('/admin/users'),
        api.get('/admin/bookings'),
        api.get('/admin/tickets'),
        api.get('/admin/feedback')
      ]);

      setStats(statsRes.data);
      setUsers(usersRes.data);
      setBookings(bookingsRes.data);
      setTickets(ticketsRes.data);
      setFeedback(feedbackRes.data);
    } catch (err) {
      console.error("Failed to load admin dashboard data", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Admin Banner */}
      <div className="bg-gradient-to-r from-amber-900 to-slate-900 text-white rounded-3xl p-6 md:p-8 shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 bg-amber-500/20 text-amber-300 text-xs font-extrabold px-3 py-1 rounded-full mb-2 border border-amber-500/30">
            <ShieldCheck className="w-4 h-4" /> Role Authorization Protected
          </div>
          <h1 className="text-2xl sm:text-3xl font-black">System Administration Console</h1>
          <p className="text-slate-300 text-xs sm:text-sm mt-1">Platform management across users, flights, bookings, AP2 payments, support & feedback.</p>
        </div>

        <button
          onClick={fetchAdminData}
          className="bg-white/10 hover:bg-white/20 text-white text-xs font-bold px-4 py-2.5 rounded-xl transition-colors flex items-center gap-1.5"
        >
          <RefreshCcw className="w-4 h-4" /> Refresh System Stats
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-200 pb-2 overflow-x-auto custom-scrollbar">
        {[
          { id: 'overview', label: 'Platform Overview', icon: ShieldCheck },
          { id: 'users', label: `Users (${users.length})`, icon: Users },
          { id: 'bookings', label: `System Bookings (${bookings.length})`, icon: Briefcase },
          { id: 'support', label: `Support Tickets (${tickets.length})`, icon: Headphones },
          { id: 'feedback', label: `User Feedback (${feedback.length})`, icon: MessageSquare }
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-4 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center gap-2 shrink-0 ${
                activeTab === tab.id
                  ? 'bg-teal-700 text-white shadow-md'
                  : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {isLoading ? (
        <div className="py-12 text-center text-sm font-semibold text-slate-500">Loading Administrator Records...</div>
      ) : (
        <div>
          {/* Overview Tab */}
          {activeTab === 'overview' && stats && (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
                <div className="text-xs font-bold text-slate-500 uppercase">Registered Users</div>
                <div className="text-3xl font-black text-slate-900 mt-2">{stats.total_users}</div>
              </div>
              <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
                <div className="text-xs font-bold text-slate-500 uppercase">Active Flights</div>
                <div className="text-3xl font-black text-teal-700 mt-2">{stats.total_flights}</div>
              </div>
              <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
                <div className="text-xs font-bold text-slate-500 uppercase">Total Bookings</div>
                <div className="text-3xl font-black text-slate-900 mt-2">{stats.total_bookings}</div>
              </div>
              <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
                <div className="text-xs font-bold text-slate-500 uppercase">Support Tickets</div>
                <div className="text-3xl font-black text-amber-600 mt-2">{stats.open_tickets}</div>
              </div>
            </div>
          )}

          {/* Users Tab */}
          {activeTab === 'users' && (
            <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
              <table className="w-full text-left text-xs sm:text-sm">
                <thead className="bg-slate-50 border-b border-slate-200 font-bold uppercase text-slate-500">
                  <tr>
                    <th className="p-4">Name</th>
                    <th className="p-4">Email</th>
                    <th className="p-4">Role</th>
                    <th className="p-4">Registered On</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium">
                  {users.map((u) => (
                    <tr key={u.id} className="hover:bg-slate-50">
                      <td className="p-4 font-bold text-slate-900">{u.full_name}</td>
                      <td className="p-4 text-slate-600">{u.email}</td>
                      <td className="p-4">
                        <span className={`px-2.5 py-1 rounded-full text-[10px] font-extrabold ${u.role === 'ADMIN' ? 'bg-amber-100 text-amber-800' : 'bg-teal-100 text-teal-800'}`}>
                          {u.role}
                        </span>
                      </td>
                      <td className="p-4 text-slate-500">{new Date(u.created_at).toLocaleDateString('en-IN')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Bookings Tab */}
          {activeTab === 'bookings' && (
            <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
              <table className="w-full text-left text-xs sm:text-sm">
                <thead className="bg-slate-50 border-b border-slate-200 font-bold uppercase text-slate-500">
                  <tr>
                    <th className="p-4">PNR</th>
                    <th className="p-4">Route</th>
                    <th className="p-4">Class</th>
                    <th className="p-4">Status</th>
                    <th className="p-4 text-right">Total Fare</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium">
                  {bookings.map((b) => (
                    <tr key={b.id} className="hover:bg-slate-50">
                      <td className="p-4 font-black text-teal-800">{b.pnr}</td>
                      <td className="p-4 text-slate-900 font-bold">{b.origin_code} → {b.destination_code}</td>
                      <td className="p-4 text-slate-600">{b.travel_class.replace('_', ' ')}</td>
                      <td className="p-4"><StatusBadge status={b.status} /></td>
                      <td className="p-4 text-right font-black text-slate-900">₹{b.total_fare.toLocaleString('en-IN')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Support Tab */}
          {activeTab === 'support' && (
            <div className="space-y-3">
              {tickets.map((t) => (
                <div key={t.id} className="bg-white border border-slate-200 rounded-2xl p-4 space-y-2">
                  <div className="flex justify-between items-center text-xs font-bold">
                    <span className="text-teal-800 uppercase bg-teal-50 px-2 py-0.5 rounded">{t.category}</span>
                    <span className="text-slate-500">{new Date(t.created_at).toLocaleDateString('en-IN')}</span>
                  </div>
                  <div className="font-bold text-slate-900 text-sm">{t.subject}</div>
                  <div className="text-xs text-slate-600">{t.message}</div>
                </div>
              ))}
            </div>
          )}

          {/* Feedback Tab */}
          {activeTab === 'feedback' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {feedback.map((f) => (
                <div key={f.id} className="bg-white border border-slate-200 rounded-2xl p-4 space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-slate-900">{f.user_name || 'User'}</span>
                    <span className="text-amber-500 font-bold">{'★'.repeat(f.rating)}</span>
                  </div>
                  <div className="text-xs font-semibold text-teal-800">{f.category}</div>
                  <p className="text-xs text-slate-600">{f.comments}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
