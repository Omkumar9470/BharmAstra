'use client';

import { ExternalLink } from 'lucide-react';

interface NewsArticleCardProps {
  headline: string;
  source: string;
  publishedDate: string;
  sentiment: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL';
  confidence: number; // 0-100
  url: string;
  isCEOStatement?: boolean;
}

export default function NewsArticleCard({
  headline,
  source,
  publishedDate,
  sentiment,
  confidence,
  url,
  isCEOStatement = false,
}: NewsArticleCardProps) {
  const sentimentConfig = {
    POSITIVE: { bg: 'bg-emerald-600/20', text: 'text-emerald-400', label: 'POSITIVE' },
    NEGATIVE: { bg: 'bg-red-600/20', text: 'text-red-400', label: 'NEGATIVE' },
    NEUTRAL: { bg: 'bg-gray-600/20', text: 'text-gray-400', label: 'NEUTRAL' },
  };

  const config = sentimentConfig[sentiment];

  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="group block rounded-lg border border-border bg-card p-4 transition-all duration-300 hover:border-primary hover:bg-card/80 hover:shadow-lg hover:shadow-primary/20"
    >
      <div className="space-y-3">
        {/* Headline and badges row */}
        <div className="flex items-start justify-between gap-3">
          <h3 className="flex-1 font-semibold leading-snug text-foreground group-hover:text-primary">
            {headline}
            <ExternalLink className="mb-1 ml-2 inline h-4 w-4 opacity-0 transition-opacity group-hover:opacity-100" />
          </h3>
          <div className="flex flex-shrink-0 gap-2">
            {isCEOStatement && (
              <span className="inline-flex items-center rounded-full bg-amber-500/20 px-2.5 py-1 text-xs font-semibold text-amber-300">
                CEO Statement
              </span>
            )}
            <span className={`inline-flex items-center rounded-full ${config.bg} px-2.5 py-1 text-xs font-semibold ${config.text}`}>
              {config.label} ({confidence}%)
            </span>
          </div>
        </div>

        {/* Source and date */}
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span className="font-medium">{source}</span>
          <span>•</span>
          <span>{publishedDate}</span>
        </div>
      </div>
    </a>
  );
}
