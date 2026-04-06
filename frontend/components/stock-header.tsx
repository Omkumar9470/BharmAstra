'use client';

import { Badge } from '@/components/ui/badge';

interface StockHeaderProps {
  companyName: string;
  ticker: string;
  currentPrice: string;
  priceChange: number;
  stats: {
    high52w: string;
    low52w: string;
    peRatio: string;
    sector: string;
  };
}

export default function StockHeader({
  companyName,
  ticker,
  currentPrice,
  priceChange,
  stats,
}: StockHeaderProps) {
  return (
    <div className="border-b border-border bg-background py-8">
      <div className="mx-auto max-w-7xl px-4">
        {/* Company Name and Ticker */}
        <div className="mb-4 flex items-center gap-4">
          <h1 className="text-4xl font-bold text-foreground">{companyName}</h1>
          <Badge className="bg-accent text-accent-foreground text-base px-3 py-1">
            {ticker}
          </Badge>
        </div>

        {/* Current Price */}
        <div className="mb-6 flex items-baseline gap-3">
          <span className="text-5xl font-bold text-primary">{currentPrice}</span>
          <span
            className={`text-lg font-semibold ${
              priceChange >= 0 ? 'text-green-500' : 'text-red-500'
            }`}
          >
            {priceChange >= 0 ? '+' : ''}{priceChange}%
          </span>
        </div>

        {/* Stats Chips */}
        <div className="flex flex-wrap gap-3">
          <div className="rounded-lg bg-secondary px-4 py-2">
            <p className="text-xs text-muted-foreground">52W High</p>
            <p className="text-sm font-semibold text-foreground">{stats.high52w}</p>
          </div>
          <div className="rounded-lg bg-secondary px-4 py-2">
            <p className="text-xs text-muted-foreground">52W Low</p>
            <p className="text-sm font-semibold text-foreground">{stats.low52w}</p>
          </div>
          <div className="rounded-lg bg-secondary px-4 py-2">
            <p className="text-xs text-muted-foreground">P/E Ratio</p>
            <p className="text-sm font-semibold text-foreground">{stats.peRatio}</p>
          </div>
          <div className="rounded-lg bg-secondary px-4 py-2">
            <p className="text-xs text-muted-foreground">Sector</p>
            <p className="text-sm font-semibold text-foreground">{stats.sector}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
