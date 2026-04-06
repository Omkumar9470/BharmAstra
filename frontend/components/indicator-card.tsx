'use client';

import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface IndicatorCardProps {
  name: string;
  value: string;
  signal: 'BUY' | 'SELL' | 'NEUTRAL';
  reason: string;
}

export default function IndicatorCard({
  name,
  value,
  signal,
  reason,
}: IndicatorCardProps) {
  const signalColors = {
    BUY: 'bg-green-500/10 border-green-500/30 text-green-400',
    SELL: 'bg-red-500/10 border-red-500/30 text-red-400',
    NEUTRAL: 'bg-gray-500/10 border-gray-500/30 text-gray-400',
  };

  const signalIcons = {
    BUY: <TrendingUp className="h-4 w-4" />,
    SELL: <TrendingDown className="h-4 w-4" />,
    NEUTRAL: <Minus className="h-4 w-4" />,
  };

  return (
    <div className="rounded-lg border border-border bg-card p-6">
      <div className="mb-4 flex items-start justify-between">
        <h3 className="text-lg font-semibold text-foreground">{name}</h3>
        <div className={`flex items-center gap-2 rounded-md border px-3 py-1 ${signalColors[signal]}`}>
          {signalIcons[signal]}
          <span className="text-sm font-medium">{signal}</span>
        </div>
      </div>

      <p className="mb-3 text-3xl font-bold text-accent">{value}</p>

      <p className="text-sm text-muted-foreground">{reason}</p>
    </div>
  );
}
