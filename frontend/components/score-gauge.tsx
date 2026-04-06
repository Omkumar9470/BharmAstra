'use client';

interface ScoreGaugeProps {
  label: string;
  score: number; // 0-100
  color?: 'green' | 'blue' | 'amber';
}

export default function ScoreGauge({
  label,
  score,
  color = 'green',
}: ScoreGaugeProps) {
  const colorClasses = {
    green: 'from-green-500 to-primary',
    blue: 'from-blue-500 to-cyan-500',
    amber: 'from-amber-500 to-orange-500',
  };

  const gaugeColor = {
    green: 'bg-green-500',
    blue: 'bg-blue-500',
    amber: 'bg-amber-500',
  };

  return (
    <div className="rounded-lg border border-border bg-card p-6">
      <p className="mb-4 text-center text-sm font-medium text-muted-foreground">
        {label}
      </p>

      {/* Gauge Visualization */}
      <div className="mb-4 flex flex-col items-center">
        <div className="relative h-24 w-24">
          {/* Outer circle */}
          <svg className="h-full w-full" viewBox="0 0 100 100">
            {/* Background arc */}
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="#374151"
              strokeWidth="8"
              opacity="0.3"
            />
            {/* Progress arc */}
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="currentColor"
              strokeWidth="8"
              strokeDasharray={`${(score / 100) * 251.2} 251.2`}
              strokeLinecap="round"
              className={gaugeColor[color]}
              style={{
                transform: 'rotate(-90deg)',
                transformOrigin: '50px 50px',
                transition: 'stroke-dasharray 0.5s ease',
              }}
            />
          </svg>
          {/* Center text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-3xl font-bold ${gaugeColor[color]}`}>
              {score}
            </span>
            <span className="text-xs text-muted-foreground">/100</span>
          </div>
        </div>
      </div>

      {/* Score label */}
      <p className="text-center text-xs text-muted-foreground">
        {score >= 70 ? 'Strong' : score >= 50 ? 'Moderate' : 'Weak'}
      </p>
    </div>
  );
}
