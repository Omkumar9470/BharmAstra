import {
  BarChart3,
  Brain,
  Newspaper,
} from 'lucide-react';

const features = [
  {
    title: 'Sentiment Analysis',
    description: 'Real-time news sentiment using FinBERT AI',
    icon: Newspaper,
  },
  {
    title: 'Technical Analysis',
    description: 'RSI, MACD, Bollinger Bands & more',
    icon: BarChart3,
  },
  {
    title: 'AI Recommendation',
    description: 'BUY / HOLD / SELL powered by Gemini AI',
    icon: Brain,
  },
];

export default function FeatureCards() {
  return (
    <div className="grid gap-6 md:grid-cols-3">
      {features.map((feature) => {
        const IconComponent = feature.icon;
        return (
          <div
            key={feature.title}
            className="rounded-lg border border-border bg-card p-6 transition-all hover:border-accent hover:shadow-lg hover:shadow-accent/10"
          >
            <div className="mb-4 inline-flex rounded-lg bg-accent/10 p-3">
              <IconComponent className="text-accent" size={28} />
            </div>
            <h3 className="mb-2 text-lg font-semibold text-foreground">
              {feature.title}
            </h3>
            <p className="text-sm text-muted-foreground">{feature.description}</p>
          </div>
        );
      })}
    </div>
  );
}
