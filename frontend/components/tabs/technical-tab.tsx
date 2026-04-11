'use client';

import IndicatorCard from '../indicator-card';
import { AlertCircle } from 'lucide-react';

interface TechnicalTabProps {
  bias: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  indicators?: Array<{
    name: string;
    value: string;
    signal: 'BUY' | 'SELL' | 'NEUTRAL';
    reason: string;
  }>;
  buysignals?: number;
  neutralSignals?: number;
  sellSignals?: number;
}

export default function TechnicalTab({
  bias = 'BULLISH',
  indicators = [
    {
      name: 'RSI (14)',
      value: '62.5',
      signal: 'BUY',
      reason: 'Approaching overbought territory but still in buy zone',
    },
    {
      name: 'MACD',
      value: '0.45',
      signal: 'BUY',
      reason: 'Positive histogram with uptrend crossover signal',
    },
    {
      name: 'Bollinger Bands',
      value: '65%',
      signal: 'BUY',
      reason: 'Price near upper band with strong momentum',
    },
    {
      name: 'EMA Cross (50/200)',
      value: 'Bullish',
      signal: 'BUY',
      reason: '50-day EMA above 200-day EMA confirming uptrend',
    },
    {
      name: 'SMA 200',
      value: '₹1,380',
      signal: 'BUY',
      reason: 'Price trading well above long-term support level',
    },
    {
      name: 'Volume Trend',
      value: 'Increasing',
      signal: 'NEUTRAL',
      reason: 'Volume elevated but needs confirmation on breakout',
    },
  ],
  buysignals = 5,
  neutralSignals = 1,
  sellSignals = 0,
}: TechnicalTabProps) {
  const biasColors = {
    BULLISH: 'bg-green-500/10 border-green-500/30 text-green-400',
    BEARISH: 'bg-red-500/10 border-red-500/30 text-red-400',
    NEUTRAL: 'bg-gray-500/10 border-gray-500/30 text-gray-400',
  };

  return (
    <div className="space-y-8">
      {/* Overall Bias Badge */}
      <div className="flex justify-center">
        <div
          className={`inline-flex items-center rounded-full border px-6 py-3 text-xl font-bold ${biasColors[bias]}`}
        >
          {bias}
        </div>
      </div>

      {/* Indicator Cards Grid */}
      <div>
        <h2 className="mb-6 text-2xl font-bold text-foreground">Technical Indicators</h2>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {indicators.map((indicator, index) => (
            <IndicatorCard
              key={index}
              name={indicator.name}
              value={indicator.value}
              signal={indicator.signal}
              reason={indicator.reason}
            />
          ))}
        </div>
      </div>

      {/* Chart Placeholder */}
      <div className="rounded-lg border border-border bg-card p-12 text-center">
        <div className="mx-auto flex h-80 items-center justify-center rounded-md bg-background/50">
          <div className="flex flex-col items-center gap-2 text-muted-foreground">
            <AlertCircle className="h-12 w-12 opacity-50" />
            <p className="text-lg font-medium">Price Chart with Indicators</p>
            <p className="text-sm">Chart data will be integrated here</p>
          </div>
        </div>
      </div>

      {/* Signals Summary */}
      <div>
        <h2 className="mb-6 text-xl font-bold text-foreground">Signals Summary</h2>
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-lg border border-green-500/30 bg-green-500/10 p-6">
            <p className="text-sm font-medium text-green-400">BUY Signals</p>
            <p className="mt-2 text-4xl font-bold text-green-400">{buysignals}</p>
          </div>
          <div className="rounded-lg border border-gray-500/30 bg-gray-500/10 p-6">
            <p className="text-sm font-medium text-gray-400">NEUTRAL Signals</p>
            <p className="mt-2 text-4xl font-bold text-gray-400">{neutralSignals}</p>
          </div>
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-6">
            <p className="text-sm font-medium text-red-400">SELL Signals</p>
            <p className="mt-2 text-4xl font-bold text-red-400">{sellSignals}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
