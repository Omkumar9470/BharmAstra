'use client';

import { useState } from 'react';

const stocks = [
  'RELIANCE.NS',
  'TCS.NS',
  'INFY.NS',
  'HDFCBANK.NS',
  'SBIN.NS',
  'TATAMOTORS.NS',
];

export default function QuickPicks() {
  const [selected, setSelected] = useState<string | null>(null);

  const handleClick = (stock: string) => {
    setSelected(stock);
    console.log('Selected stock:', stock);
  };

  return (
    <div className="flex flex-wrap gap-3">
      {stocks.map((stock) => (
        <button
          key={stock}
          onClick={() => handleClick(stock)}
          className={`rounded-full px-4 py-2 text-sm font-medium transition-all ${
            selected === stock
              ? 'bg-accent text-accent-foreground shadow-lg shadow-accent/30'
              : 'border border-border bg-card text-foreground hover:border-accent hover:bg-card/80'
          }`}
        >
          {stock}
        </button>
      ))}
    </div>
  );
}
