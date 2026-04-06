'use client';

import { AlertCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import ScoreGauge from '../score-gauge';

interface OverviewTabProps {
  recommendationType: 'BUY' | 'HOLD' | 'SELL';
  confidence: 'LOW' | 'MEDIUM' | 'HIGH';
  technicalScore: number;
  sentimentScore: number;
  combinedScore: number;
  summaryText: string;
  targetPrice: string;
  stopLoss: string;
  risks: string[];
}

export default function OverviewTab({
  recommendationType,
  confidence,
  technicalScore,
  sentimentScore,
  combinedScore,
  summaryText,
  targetPrice,
  stopLoss,
  risks,
}: OverviewTabProps) {
  const recommendationColors = {
    BUY: 'bg-green-600 text-white hover:bg-green-700',
    HOLD: 'bg-yellow-600 text-white hover:bg-yellow-700',
    SELL: 'bg-red-600 text-white hover:bg-red-700',
  };

  const confidenceColors = {
    LOW: 'bg-red-500/10 text-red-400',
    MEDIUM: 'bg-yellow-500/10 text-yellow-400',
    HIGH: 'bg-green-500/10 text-green-400',
  };

  const normalizedScore = (combinedScore + 1) / 2; // Convert -1 to 1 into 0 to 1

  return (
    <div className="space-y-8 pb-8">
      {/* Recommendation Card */}
      <div className="rounded-xl border-2 border-border bg-gradient-to-br from-card to-secondary p-8">
        <div className="mb-6 text-center">
          <div
            className={`mb-4 inline-block rounded-lg px-6 py-3 ${recommendationColors[recommendationType]}`}
          >
            <span className="text-3xl font-bold">{recommendationType}</span>
          </div>
          <Badge className={`ml-4 ${confidenceColors[confidence]}`}>
            {confidence} CONFIDENCE
          </Badge>
        </div>

        {/* Combined Score Progress Bar */}
        <div className="mb-6">
          <div className="mb-2 flex items-center justify-between">
            <p className="text-sm font-medium text-muted-foreground">
              Combined Score
            </p>
            <p className="text-sm font-semibold text-foreground">
              {combinedScore > 0 ? '+' : ''}{combinedScore.toFixed(2)}
            </p>
          </div>
          <div className="relative h-2 w-full overflow-hidden rounded-full bg-secondary">
            <div
              className="h-full bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 transition-all duration-500"
              style={{ width: `${Math.max(0, normalizedScore * 100)}%` }}
            />
          </div>
          <div className="mt-1 flex justify-between text-xs text-muted-foreground">
            <span>Bearish</span>
            <span>Neutral</span>
            <span>Bullish</span>
          </div>
        </div>

        {/* Summary Text */}
        <p className="text-center text-base leading-relaxed text-foreground">
          {summaryText}
        </p>
      </div>

      {/* Target & Stop Loss */}
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-lg border border-border bg-card p-6">
          <p className="mb-2 text-xs text-muted-foreground">Target Price</p>
          <p className="text-2xl font-bold text-green-500">{targetPrice}</p>
        </div>
        <div className="rounded-lg border border-border bg-card p-6">
          <p className="mb-2 text-xs text-muted-foreground">Stop Loss</p>
          <p className="text-2xl font-bold text-red-500">{stopLoss}</p>
        </div>
      </div>

      {/* Scores Grid */}
      <div className="grid gap-6 sm:grid-cols-2">
        <ScoreGauge label="Technical Score" score={technicalScore} color="blue" />
        <ScoreGauge label="Sentiment Score" score={sentimentScore} color="green" />
      </div>

      {/* Risks Section */}
      <div className="rounded-lg border border-amber-500/20 bg-amber-500/10 p-6">
        <div className="mb-4 flex items-center gap-2">
          <AlertCircle className="h-5 w-5 text-amber-500" />
          <h3 className="text-lg font-semibold text-amber-400">Risk Factors</h3>
        </div>
        <ul className="space-y-2">
          {risks.map((risk, idx) => (
            <li key={idx} className="flex gap-2 text-sm text-amber-200">
              <span className="mt-0.5 h-2 w-2 flex-shrink-0 rounded-full bg-amber-500" />
              <span>{risk}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Disclaimer */}
      <p className="text-center text-xs text-muted-foreground">
        Disclaimer: This analysis is for educational purposes only. Past performance does not
        guarantee future results. Please consult a financial advisor before making investment
        decisions.
      </p>
    </div>
  );
}
