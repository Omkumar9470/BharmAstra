// frontend/lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ── Types ──────────────────────────────────────────────

export interface StockInfo {
  ticker: string;
  name: string;
  sector: string;
  industry: string;
  market_cap: number;
  current_price: number;
  "52w_high": number;
  "52w_low": number;
  pe_ratio: number;
  currency: string;
}

export interface Signal {
  indicator: string;
  signal: "BUY" | "SELL" | "NEUTRAL";
  reason: string;
  weight: number;
}

export interface TechnicalData {
  ticker: string;
  date: string;
  close: number;
  technical_score: number;
  bias: "BULLISH" | "BEARISH" | "NEUTRAL";
  signals: Signal[];
  latest_indicators: {
    rsi: number | null;
    macd_diff: number | null;
    bb_pct: number | null;
    ema_20: number | null;
    ema_50: number | null;
    sma_200: number | null;
  };
}

export interface Article {
  title: string;
  source: string;
  url: string;
  published_at: string;
  is_ceo_statement: boolean;
  sentiment: "positive" | "negative" | "neutral";
  confidence: number;
  positive: number;
  negative: number;
  neutral: number;
  weight: number;
}

export interface SentimentData {
  company: string;
  ticker: string;
  sentiment_score: number;
  label: "positive" | "negative" | "neutral";
  article_count: number;
  articles: Article[];
}

export interface Recommendation {
  ticker: string;
  company: string;
  recommendation: "BUY" | "HOLD" | "SELL";
  confidence: "HIGH" | "MEDIUM" | "LOW";
  target_price: string | null;
  stop_loss: string | null;
  summary: string;
  risks: string;
  disclaimer: string;
  engine: string;
}

export interface FullRecommendation {
  ticker: string;
  company: string;
  combined_score: number;
  technical_score: number;
  sentiment_score: number;
  technical_bias: string;
  sentiment_label: string;
  recommendation: Recommendation;
}

// ── API calls ──────────────────────────────────────────

export async function getStockInfo(ticker: string): Promise<StockInfo> {
  const res = await fetch(`${API_URL}/api/stock/${ticker}/info`);
  if (!res.ok) throw new Error("Failed to fetch stock info");
  return res.json();
}

export async function getTechnicalSignals(ticker: string): Promise<TechnicalData> {
  const res = await fetch(`${API_URL}/api/stock/${ticker}/signals`);
  if (!res.ok) throw new Error("Failed to fetch technical signals");
  return res.json();
}

export async function getSentiment(ticker: string): Promise<SentimentData> {
  const res = await fetch(`${API_URL}/api/stock/${ticker}/sentiment`);
  if (!res.ok) throw new Error("Failed to fetch sentiment");
  return res.json();
}

export async function getRecommendation(ticker: string): Promise<FullRecommendation> {
  const res = await fetch(`${API_URL}/api/stock/${ticker}/recommend`);
  if (!res.ok) throw new Error("Failed to fetch recommendation");
  return res.json();
}

export async function searchTicker(query: string): Promise<{ resolved_ticker: string }> {
  const res = await fetch(
    `${API_URL}/api/stock/search?q=${encodeURIComponent(query)}`
  );
  if (!res.ok) throw new Error("Failed to search ticker");
  return res.json();
}