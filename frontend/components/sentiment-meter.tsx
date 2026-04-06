'use client';

interface SentimentMeterProps {
  score: number; // -1.0 to +1.0
}

export default function SentimentMeter({ score }: SentimentMeterProps) {
  // Convert score (-1 to 1) to percentage (0 to 100)
  const percentage = ((score + 1) / 2) * 100;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span className="font-medium">-1.0</span>
        <span className="font-medium">Bearish ←→ Bullish</span>
        <span className="font-medium">+1.0</span>
      </div>

      <div className="relative h-3 w-full overflow-hidden rounded-full bg-secondary">
        {/* Background gradient */}
        <div className="absolute inset-0 flex">
          <div className="flex-1 bg-red-600/30"></div>
          <div className="flex-1 bg-gray-500/30"></div>
          <div className="flex-1 bg-emerald-600/30"></div>
        </div>

        {/* Progress indicator */}
        <div
          className="absolute h-full w-1 bg-foreground transition-all duration-500"
          style={{
            left: `${percentage}%`,
            transform: 'translateX(-50%)',
          }}
        >
          <div className="absolute -top-2 left-1/2 h-7 w-7 -translate-x-1/2 rounded-full border-2 border-foreground bg-secondary shadow-lg"></div>
        </div>
      </div>

      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>Very Bearish</span>
        <span>Neutral</span>
        <span>Very Bullish</span>
      </div>
    </div>
  );
}
