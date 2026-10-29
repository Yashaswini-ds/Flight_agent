import React from 'react';
import { BookingStatus } from '../types';

interface StatusBadgeProps {
  status: BookingStatus | string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  let badgeStyle = 'bg-slate-100 text-slate-700 border-slate-300';

  switch (status) {
    case 'CONFIRMED':
    case 'BOOKED':
    case 'COMPLETED':
      badgeStyle = 'bg-emerald-50 text-emerald-800 border-emerald-200';
      break;
    case 'PAYMENT_PENDING':
    case 'REFUND_PENDING':
      badgeStyle = 'bg-amber-50 text-amber-800 border-amber-200';
      break;
    case 'CANCELLED':
    case 'REFUNDED':
    case 'FAILED':
      badgeStyle = 'bg-red-50 text-red-800 border-red-200';
      break;
  }

  return (
    <span className={`text-xs font-bold px-2.5 py-1 rounded-full border ${badgeStyle} uppercase tracking-wider`}>
      {status.replace('_', ' ')}
    </span>
  );
};
