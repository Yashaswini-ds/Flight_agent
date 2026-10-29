import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, X, Sparkles, User, Plane, ArrowRight, CreditCard, ShieldCheck, CheckCircle, Minimize2, Maximize2, MoveLeft, MoveRight, Minus, Square } from 'lucide-react';
import api from '../services/api';
import { AgentResponse, Flight, PaymentIntent, PaymentResult } from '../types';

interface AIAssistantWidgetProps {
  onSelectFlightFromAgent?: (flight: Flight) => void;
  onSearchFlightsFromAgent?: (flights: Flight[]) => void;
}


interface Message {
  sender: 'user' | 'bot';
  text: string;
  flights?: Flight[];
  suggestedAction?: string;
  paymentIntent?: PaymentIntent;
  draftBooking?: any;
}

export const AIAssistantWidget: React.FC<AIAssistantWidgetProps> = ({ onSelectFlightFromAgent, onSearchFlightsFromAgent }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isCompact, setIsCompact] = useState(false);
  const [positionLeft, setPositionLeft] = useState(false);

  const [messages, setMessages] = useState<Message[]>([
    {
      sender: 'bot',
      text: 'Hello! I am your AI Travel Assistant. I am backed by two separate AI agents: an Intent Agent (to understand your request) and a Booking Agent (to find flights and assist bookings). How can I help you today?'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);

  // Demo Payment State
  const [activePaymentIntent, setActivePaymentIntent] = useState<PaymentIntent | null>(null);
  const [paymentMethod, setPaymentMethod] = useState<'UPI' | 'CARD' | 'QR'>('UPI');
  const [demoAuthPin, setDemoAuthPin] = useState('1234');
  const [demoIdentifier, setDemoIdentifier] = useState('user@upi');
  const [isExecutingPayment, setIsExecutingPayment] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen && !isMinimized) {
      scrollToBottom();
    }
  }, [messages, isOpen, isMinimized]);

  const sendQuery = async (msgText: string) => {
    if (!msgText.trim() || isLoading) return;

    setMessages((prev) => [...prev, { sender: 'user', text: msgText }]);
    setIsLoading(true);

    try {
      const res = await api.post<AgentResponse>('/assistant/chat', {
        message: msgText,
        conversation_id: conversationId
      });

      setConversationId(res.data.conversation_id);
      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: res.data.reply,
          flights: res.data.flights_found || undefined,
          suggestedAction: res.data.action_suggested || undefined,
          paymentIntent: res.data.payment_intent || undefined,
          draftBooking: res.data.draft_booking || undefined
        }
      ]);

      if (res.data.flights_found && res.data.flights_found.length > 0) {
        onSearchFlightsFromAgent?.(res.data.flights_found);
      }

      if (res.data.action_suggested === 'LAUNCH_PAYMENT' && res.data.payment_intent) {
        setActivePaymentIntent(res.data.payment_intent);
      }
    } catch (err) {

      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: 'Sorry, I encountered an issue connecting to the AI Agents. Please ensure you are signed in and try again.'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    const txt = input.trim();
    setInput('');
    sendQuery(txt);
  };

  // Direct Frontend Payment Execution (Strict Payment Credential Isolation)
  const handleExecuteDemoPayment = async () => {
    if (!activePaymentIntent || isExecutingPayment) return;
    setIsExecutingPayment(true);

    try {
      const res = await api.post<PaymentResult>('/payments/execute', {
        payment_intent_id: activePaymentIntent.payment_intent_id,
        payment_method: paymentMethod,
        demo_pin_or_auth: demoAuthPin,
        demo_identifier: demoIdentifier
      });

      setActivePaymentIntent(null);
      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: `🎉 **Booking Confirmed!**\n\n🎟️ **PNR Code**: \`${res.data.pnr}\`\n🔖 **Booking Reference**: \`${res.data.booking_reference}\`\n💰 **Amount Paid**: ₹${res.data.amount.toLocaleString()}\n🔒 **Payment Status**: PAID\n✅ **Booking Status**: CONFIRMED\n\nYour E-Ticket is ready in 'My Trips'. Have a great journey!`
        }
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: `❌ Payment failed: ${err?.response?.data?.detail || 'Simulated payment authorization error'}. Please try again.`
        }
      ]);
    } finally {
      setIsExecutingPayment(false);
    }
  };

  return (
    <div className={`fixed bottom-3 sm:bottom-5 z-40 transition-all duration-300 ${positionLeft ? 'left-3 sm:left-5' : 'right-3 sm:right-5'} max-h-[calc(100vh-1.5rem)]`}>
      {/* Floating Closed Launcher Button */}
      {!isOpen && (
        <button
          type="button"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setIsOpen(true);
            setIsMinimized(false);
          }}
          className="bg-teal-700 hover:bg-teal-800 text-white p-4 rounded-full shadow-2xl transition-all transform hover:scale-105 flex items-center gap-2 group border border-teal-500/30"
          title="Open Dual-Agent AI Travel Assistant"
        >
          <div className="relative">
            <Bot className="w-6 h-6" />
            <span className="w-2.5 h-2.5 bg-emerald-400 rounded-full absolute -top-1 -right-1 ring-2 ring-teal-800 animate-pulse"></span>
          </div>
          <span className="text-sm font-bold pr-1 hidden sm:inline">AI Travel Assistant</span>
        </button>
      )}

      {/* Minimized Pill */}
      {isOpen && isMinimized && (
        <button
          type="button"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setIsMinimized(false);
          }}
          className="bg-slate-900/95 backdrop-blur-md text-white px-4 py-2.5 rounded-2xl shadow-2xl border border-slate-700 hover:bg-slate-800 transition-all flex items-center gap-3 animate-in fade-in slide-in-from-bottom-2"
        >
          <div className="relative flex items-center justify-center">
            <Bot className="w-5 h-5 text-teal-400" />
            <span className="w-2 h-2 bg-emerald-400 rounded-full absolute -top-0.5 -right-0.5 animate-pulse"></span>
          </div>
          <span className="text-xs font-bold">AI Assistant Active (Click to Expand)</span>
          <Maximize2 className="w-3.5 h-3.5 text-slate-400 hover:text-white" />
        </button>
      )}

      {/* Chat Panel */}
      {isOpen && !isMinimized && (
        <div className={`bg-white/95 backdrop-blur-md rounded-3xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-300 transition-all max-h-[calc(100vh-2rem)] ${
          isCompact ? 'w-[90vw] sm:w-[360px] h-[440px]' : 'w-[92vw] sm:w-[420px] h-[520px] sm:h-[560px]'
        }`}>

          {/* Header */}
          <div className="bg-slate-900 text-white p-3 sm:p-3.5 flex items-center justify-between border-b border-slate-800 gap-2 shrink-0">
            <div className="flex items-center gap-2 min-w-0">
              <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-xl bg-teal-600 flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
              </div>
              <div className="min-w-0">
                <h3 className="font-bold text-xs sm:text-sm truncate flex items-center gap-1.5">
                  AI Travel Assistant
                </h3>
                <p className="text-[10px] text-slate-400 truncate">Dual Agent Engine</p>
              </div>
            </div>

            {/* Header Controls */}
            <div className="flex items-center gap-1 sm:gap-1.5 shrink-0">
              <button
                type="button"
                onClick={(e) => { e.preventDefault(); setPositionLeft(!positionLeft); }}
                className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
                title={positionLeft ? "Move chatbot to right side" : "Move chatbot to left side"}
              >
                {positionLeft ? <MoveRight className="w-4 h-4" /> : <MoveLeft className="w-4 h-4" />}
              </button>

              <button
                type="button"
                onClick={(e) => { e.preventDefault(); setIsMinimized(true); }}
                className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
                title="Minimize chatbot window"
              >
                <Minus className="w-4 h-4" />
              </button>

              <button
                type="button"
                onClick={(e) => { e.preventDefault(); setIsCompact(!isCompact); }}
                className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
                title={isCompact ? "Maximize / Expand chatbot window" : "Compact chatbot window"}
              >
                {isCompact ? <Maximize2 className="w-4 h-4" /> : <Square className="w-3.5 h-3.5" />}
              </button>

              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setIsOpen(false);
                  setIsMinimized(false);
                }}
                className="bg-red-600 hover:bg-red-700 text-white font-bold px-3 py-1.5 rounded-xl text-xs flex items-center gap-1 shadow-md transition-transform active:scale-95 shrink-0 border border-red-500"
                title="Close Chatbot"
              >
                <X className="w-4 h-4" />
                <span>Close</span>
              </button>
            </div>
          </div>





          {/* Messages */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4 custom-scrollbar bg-slate-50">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex gap-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {m.sender === 'bot' && (
                  <div className="w-7 h-7 rounded-lg bg-teal-700 text-white flex items-center justify-center shrink-0 mt-1">
                    <Bot className="w-4 h-4" />
                  </div>
                )}
                <div
                  className={`max-w-[85%] rounded-2xl p-3.5 text-xs sm:text-sm font-medium leading-relaxed whitespace-pre-wrap ${
                    m.sender === 'user'
                      ? 'bg-teal-700 text-white rounded-br-none'
                      : 'bg-white text-slate-800 border border-slate-200 shadow-sm rounded-bl-none'
                  }`}
                >
                  {m.text}

                  {/* Flight Options Buttons */}
                  {m.suggestedAction === 'SELECT_FLIGHT' && m.flights && m.flights.length > 0 && (
                    <div className="mt-3 space-y-2 pt-2 border-t border-slate-100">
                      {m.flights.slice(0, 3).map((f) => (
                        <button
                          type="button"
                          key={f.id}
                          onClick={() => sendQuery(`Select flight ${f.flight_number}`)}
                          className="w-full text-left bg-slate-50 hover:bg-teal-50 p-2.5 rounded-xl border border-slate-200 transition-colors flex justify-between items-center text-xs group"
                        >
                          <div>
                            <div className="font-bold text-slate-900 group-hover:text-teal-800">{f.airline_name} ({f.flight_number})</div>
                            <div className="text-[10px] text-slate-500">{f.origin_code} → {f.destination_code}</div>
                          </div>
                          <span className="bg-teal-700 text-white text-[11px] font-bold px-2.5 py-1 rounded-lg flex items-center gap-1">
                            Select <ArrowRight className="w-3 h-3" />
                          </span>
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Class Selection Buttons */}
                  {m.suggestedAction === 'SELECT_CLASS' && (
                    <div className="mt-3 flex gap-2 pt-2 border-t border-slate-100">
                      <button
                        type="button"
                        onClick={() => sendQuery('Economy')}
                        className="bg-slate-100 hover:bg-teal-50 hover:text-teal-800 text-slate-800 px-3 py-1.5 rounded-lg text-xs font-bold border border-slate-200"
                      >
                        Economy
                      </button>
                      <button
                        type="button"
                        onClick={() => sendQuery('Premium Economy')}
                        className="bg-slate-100 hover:bg-teal-50 hover:text-teal-800 text-slate-800 px-3 py-1.5 rounded-lg text-xs font-bold border border-slate-200"
                      >
                        Premium Eco
                      </button>
                      <button
                        type="button"
                        onClick={() => sendQuery('Business')}
                        className="bg-slate-100 hover:bg-teal-50 hover:text-teal-800 text-slate-800 px-3 py-1.5 rounded-lg text-xs font-bold border border-slate-200"
                      >
                        Business
                      </button>
                    </div>
                  )}

                  {/* Review Summary Buttons */}
                  {m.suggestedAction === 'REVIEW_SUMMARY' && (
                    <div className="mt-3 flex gap-2 pt-2 border-t border-slate-100">
                      <button
                        type="button"
                        onClick={() => sendQuery('Proceed to payment')}
                        className="bg-teal-700 hover:bg-teal-800 text-white px-3 py-1.5 rounded-lg text-xs font-bold shadow-sm"
                      >
                        Proceed to Payment
                      </button>
                      <button
                        type="button"
                        onClick={() => sendQuery('Modify')}
                        className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-lg text-xs font-medium"
                      >
                        Modify
                      </button>
                      <button
                        type="button"
                        onClick={() => sendQuery('Cancel')}
                        className="bg-slate-100 hover:bg-red-50 text-red-600 px-3 py-1.5 rounded-lg text-xs font-medium"
                      >
                        Cancel
                      </button>
                    </div>
                  )}

                  {/* Modification Menu Buttons */}
                  {m.suggestedAction === 'MODIFICATION_MENU' && (
                    <div className="mt-3 flex flex-wrap gap-2 pt-2 border-t border-slate-100">
                      <button
                        type="button"
                        onClick={() => sendQuery('Change flight')}
                        className="bg-slate-100 hover:bg-teal-50 hover:text-teal-800 text-slate-800 px-3 py-1.5 rounded-lg text-xs font-bold border border-slate-200"
                      >
                        Flight
                      </button>
                      <button
                        type="button"
                        onClick={() => sendQuery('Change travel class')}
                        className="bg-slate-100 hover:bg-teal-50 hover:text-teal-800 text-slate-800 px-3 py-1.5 rounded-lg text-xs font-bold border border-slate-200"
                      >
                        Travel Class
                      </button>
                      <button
                        type="button"
                        onClick={() => sendQuery('Change seat')}
                        className="bg-slate-100 hover:bg-teal-50 hover:text-teal-800 text-slate-800 px-3 py-1.5 rounded-lg text-xs font-bold border border-slate-200"
                      >
                        Seat
                      </button>
                      <button
                        type="button"
                        onClick={() => sendQuery('Change passenger details')}
                        className="bg-slate-100 hover:bg-teal-50 hover:text-teal-800 text-slate-800 px-3 py-1.5 rounded-lg text-xs font-bold border border-slate-200"
                      >
                        Passenger Details
                      </button>
                      <button
                        type="button"
                        onClick={() => sendQuery('Cancel modification')}
                        className="bg-slate-100 hover:bg-red-50 hover:text-red-700 text-slate-600 px-3 py-1.5 rounded-lg text-xs font-medium border border-slate-200"
                      >
                        Cancel Modification
                      </button>
                    </div>
                  )}



                  {/* Cancellation Review Buttons */}
                  {m.suggestedAction === 'CANCELLATION_REVIEW_SUMMARY' && (
                    <div className="mt-3 flex gap-2 pt-2 border-t border-slate-100">
                      <button
                        type="button"
                        onClick={() => sendQuery('Confirm cancellation')}
                        className="bg-red-600 hover:bg-red-700 text-white px-3 py-1.5 rounded-lg text-xs font-bold shadow-sm"
                      >
                        Confirm Cancellation
                      </button>
                      <button
                        type="button"
                        onClick={() => sendQuery('Keep ticket')}
                        className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-lg text-xs font-medium"
                      >
                        Keep Ticket
                      </button>
                    </div>
                  )}

                </div>
              </div>
            ))}

            {/* Interactive Demo Payment Launcher Widget */}
            {activePaymentIntent && (
              <div className="bg-gradient-to-br from-slate-900 to-slate-800 text-white rounded-2xl p-4 shadow-xl border border-slate-700 space-y-3 animate-in fade-in duration-300">
                <div className="flex items-center justify-between border-b border-slate-700 pb-2">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="w-5 h-5 text-emerald-400" />
                    <span className="font-bold text-xs">Simulated Demo Payment</span>
                  </div>
                  <span className="text-[10px] bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded-full font-bold">
                    No Money Charged
                  </span>
                </div>

                <div className="text-xs space-y-1">
                  <div className="text-slate-300">Total Amount: <span className="text-emerald-400 font-bold text-sm">₹{activePaymentIntent.amount.toLocaleString()}</span></div>
                  <div className="text-[11px] text-slate-400">Payment Intent: {activePaymentIntent.payment_intent_id}</div>
                </div>

                <div className="space-y-2">
                  <label className="text-[11px] font-bold text-slate-300 block">Payment Method:</label>
                  <div className="flex gap-2">
                    {(['UPI', 'CARD', 'QR'] as const).map((method) => (
                      <button
                        type="button"
                        key={method}
                        onClick={() => setPaymentMethod(method)}
                        className={`flex-1 py-1.5 rounded-lg text-xs font-bold border transition-colors ${
                          paymentMethod === method
                            ? 'bg-teal-600 border-teal-400 text-white'
                            : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-white'
                        }`}
                      >
                        {method}
                      </button>
                    ))}
                  </div>

                  {paymentMethod === 'UPI' && (
                    <div>
                      <input
                        type="text"
                        value={demoIdentifier}
                        onChange={(e) => setDemoIdentifier(e.target.value)}
                        placeholder="UPI ID (e.g. user@upi)"
                        className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-teal-500"
                      />
                    </div>
                  )}

                  {paymentMethod === 'CARD' && (
                    <div>
                      <input
                        type="text"
                        value={demoIdentifier}
                        onChange={(e) => setDemoIdentifier(e.target.value)}
                        placeholder="Card Number (4111-2222-3333-4444)"
                        className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-teal-500"
                      />
                    </div>
                  )}

                  <div>
                    <input
                      type="password"
                      value={demoAuthPin}
                      onChange={(e) => setDemoAuthPin(e.target.value)}
                      placeholder="Demo PIN / Auth Token (e.g. 1234)"
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-teal-500"
                    />
                  </div>

                  <button
                    type="button"
                    onClick={handleExecuteDemoPayment}
                    disabled={isExecutingPayment}
                    className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2 rounded-xl text-xs flex items-center justify-center gap-1.5 shadow-lg transition-colors disabled:opacity-50"
                  >
                    {isExecutingPayment ? (
                      'Executing Payment...'
                    ) : (
                      <>
                        <CheckCircle className="w-4 h-4" /> Authorize & Pay ₹{activePaymentIntent.amount.toLocaleString()}
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}

            {isLoading && (
              <div className="flex gap-2 justify-start items-center text-xs text-slate-500 font-medium">
                <Bot className="w-4 h-4 text-teal-700 animate-spin" />
                Dual Agents processing request...
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Prompts */}
          <div className="px-3 py-2 bg-white border-t border-slate-100 flex gap-1.5 overflow-x-auto custom-scrollbar text-[11px]">
            <button
              type="button"
              onClick={() => sendQuery('Book a flight from Bangalore to Hyderabad')}
              className="bg-slate-100 hover:bg-teal-50 text-slate-700 hover:text-teal-800 px-2.5 py-1 rounded-lg shrink-0 border border-slate-200 font-medium"
            >
              ✈️ Book BLR → HYD
            </button>
            <button
              type="button"
              onClick={() => sendQuery('Book 2 tickets from Bangalore to Hyderabad')}
              className="bg-slate-100 hover:bg-teal-50 text-slate-700 hover:text-teal-800 px-2.5 py-1 rounded-lg shrink-0 border border-slate-200 font-medium"
            >
              👥 2 Tickets BLR → HYD
            </button>
            <button
              type="button"
              onClick={() => sendQuery('Cancel ticket')}
              className="bg-slate-100 hover:bg-red-50 text-slate-700 hover:text-red-800 px-2.5 py-1 rounded-lg shrink-0 border border-slate-200 font-medium"
            >
              ❌ Cancel Ticket
            </button>
          </div>




          {/* Input Bar */}
          <form onSubmit={handleSend} className="p-3 bg-white border-t border-slate-200 flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything (e.g. Book BLR to HYD)..."
              className="flex-1 bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-xs sm:text-sm font-medium focus:ring-2 focus:ring-teal-600 focus:outline-none"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="bg-teal-700 hover:bg-teal-800 text-white p-2.5 rounded-xl transition-colors disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

