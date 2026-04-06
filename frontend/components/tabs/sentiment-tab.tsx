'use client';

import NewsArticleCard from '@/components/news-article-card';
import SentimentMeter from '@/components/sentiment-meter';

interface SentimentTabProps {
  score?: number; // -1.0 to +1.0
  articleCount?: number;
}

export default function SentimentTab({ score = -0.23, articleCount = 12 }: SentimentTabProps) {
  // Determine sentiment label
  const getSentimentLabel = (s: number) => {
    if (s > 0.2) return 'POSITIVE';
    if (s < -0.2) return 'NEGATIVE';
    return 'NEUTRAL';
  };

  const getSentimentColor = (s: number) => {
    if (s > 0.2) return 'text-emerald-400';
    if (s < -0.2) return 'text-red-400';
    return 'text-gray-400';
  };

  const getSentimentBadgeColor = (s: number) => {
    if (s > 0.2) return 'bg-emerald-600/20 text-emerald-400';
    if (s < -0.2) return 'bg-red-600/20 text-red-400';
    return 'bg-gray-600/20 text-gray-400';
  };

  const sentimentLabel = getSentimentLabel(score);
  const sentimentColor = getSentimentColor(score);
  const badgeColor = getSentimentBadgeColor(score);

  // Sample news articles
  const articles = [
    {
      headline: 'Reliance Industries Q4 Results Beat Expectations, Strong Petrochemical Demand',
      source: 'Economic Times',
      publishedDate: '2 hours ago',
      sentiment: 'POSITIVE' as const,
      confidence: 85,
      url: 'https://economictimes.indiatimes.com',
      isCEOStatement: false,
    },
    {
      headline: 'CEO Mukesh Ambani Announces Strategic Expansion into Renewable Energy',
      source: 'Business Today',
      publishedDate: '5 hours ago',
      sentiment: 'POSITIVE' as const,
      confidence: 92,
      url: 'https://www.businesstoday.com',
      isCEOStatement: true,
    },
    {
      headline: 'Concerns Over Oil Price Volatility Impact Profit Margins',
      source: 'Moneycontrol',
      publishedDate: '8 hours ago',
      sentiment: 'NEGATIVE' as const,
      confidence: 72,
      url: 'https://www.moneycontrol.com',
      isCEOStatement: false,
    },
    {
      headline: 'RIL Maintains Market Leadership Position Despite Global Headwinds',
      source: 'LiveMint',
      publishedDate: '12 hours ago',
      sentiment: 'NEUTRAL' as const,
      confidence: 65,
      url: 'https://www.livemint.com',
      isCEOStatement: false,
    },
  ];

  return (
    <div className="space-y-8">
      {/* Overall Sentiment Score Card */}
      <div className="rounded-lg border border-border bg-card p-8">
        <div className="space-y-4">
          <div className="flex items-end justify-between">
            <div className="space-y-2">
              <p className="text-sm font-medium text-muted-foreground">Sentiment Score</p>
              <p className={`text-5xl font-bold ${sentimentColor}`}>
                {score > 0 ? '+' : ''}{score.toFixed(2)}
              </p>
            </div>
            <div className="text-right">
              <span className={`mb-2 inline-flex items-center rounded-full ${badgeColor} px-4 py-2 text-sm font-semibold`}>
                {sentimentLabel}
              </span>
              <p className="mt-3 text-sm text-muted-foreground">{articleCount} articles analyzed</p>
            </div>
          </div>
        </div>
      </div>

      {/* Sentiment Meter */}
      <div className="rounded-lg border border-border bg-card p-6">
        <h3 className="mb-6 text-lg font-semibold text-foreground">Market Sentiment Distribution</h3>
        <SentimentMeter score={score} />
      </div>

      {/* News Articles Section */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-foreground">Recent News & Sentiment</h3>
        <div className="max-h-[800px] space-y-3 overflow-y-auto pr-2">
          {articles.map((article, index) => (
            <NewsArticleCard
              key={index}
              headline={article.headline}
              source={article.source}
              publishedDate={article.publishedDate}
              sentiment={article.sentiment}
              confidence={article.confidence}
              url={article.url}
              isCEOStatement={article.isCEOStatement}
            />
          ))}
        </div>
      </div>

      {/* Disclaimer */}
      <div className="rounded-lg border border-border/50 bg-secondary/30 p-4">
        <p className="text-xs text-muted-foreground">
          * Sentiment analysis is generated using FinBERT AI model on news articles and financial reports. Scores range from -1.0 (very bearish)
          to +1.0 (very bullish). Past sentiment does not guarantee future results. Always conduct your own research before investing.
        </p>
      </div>
    </div>
  );
}
