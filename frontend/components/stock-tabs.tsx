'use client';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import OverviewTab from './tabs/overview-tab';
import TechnicalTab from './tabs/technical-tab';
import SentimentTab from './tabs/sentiment-tab';

interface StockTabsProps {
  recommendationType: 'BUY' | 'HOLD' | 'SELL';
  confidence: 'LOW' | 'MEDIUM' | 'HIGH';
  technicalScore: number; // 0-100
  sentimentScore: number; // 0-100
  combinedScore: number; // -1 to 1
  summaryText: string;
  targetPrice: string;
  stopLoss: string;
  risks: string[];
}

export default function StockTabs({
  recommendationType,
  confidence,
  technicalScore,
  sentimentScore,
  combinedScore,
  summaryText,
  targetPrice,
  stopLoss,
  risks,
}: StockTabsProps) {
  return (
    <Tabs defaultValue="overview" className="mx-auto max-w-7xl">
      <TabsList className="mb-8 border-b border-border bg-transparent p-0">
        <TabsTrigger
          value="overview"
          className="border-b-2 border-transparent px-4 py-3 text-base font-medium text-muted-foreground hover:text-foreground data-[state=active]:border-b-accent data-[state=active]:text-foreground"
        >
          Overview
        </TabsTrigger>
        <TabsTrigger
          value="technical"
          className="border-b-2 border-transparent px-4 py-3 text-base font-medium text-muted-foreground hover:text-foreground data-[state=active]:border-b-accent data-[state=active]:text-foreground"
        >
          Technical
        </TabsTrigger>
        <TabsTrigger
          value="sentiment"
          className="border-b-2 border-transparent px-4 py-3 text-base font-medium text-muted-foreground hover:text-foreground data-[state=active]:border-b-accent data-[state=active]:text-foreground"
        >
          Sentiment
        </TabsTrigger>
      </TabsList>

      <TabsContent value="overview" className="mt-8">
        <OverviewTab
          recommendationType={recommendationType}
          confidence={confidence}
          technicalScore={technicalScore}
          sentimentScore={sentimentScore}
          combinedScore={combinedScore}
          summaryText={summaryText}
          targetPrice={targetPrice}
          stopLoss={stopLoss}
          risks={risks}
        />
      </TabsContent>

      <TabsContent value="technical" className="mt-8">
        <TechnicalTab bias="BULLISH" />
      </TabsContent>

      <TabsContent value="sentiment" className="mt-8">
        <SentimentTab score={-0.23} articleCount={12} />
      </TabsContent>
    </Tabs>
  );
}
