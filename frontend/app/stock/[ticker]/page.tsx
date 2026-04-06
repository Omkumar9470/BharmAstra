"use client";
import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import {
  getStockInfo, getTechnicalSignals,
  getSentiment, getRecommendation,
  StockInfo, TechnicalData, SentimentData, FullRecommendation
} from "@/lib/api";

export default function StockAnalysisPage({
  params,
}: {
  params: Promise<{ ticker: string }>;
}) {
  const { ticker } = use(params);
  const decoded = decodeURIComponent(ticker);
  const router  = useRouter();

  const [info,           setInfo]           = useState<StockInfo | null>(null);
  const [technical,      setTechnical]      = useState<TechnicalData | null>(null);
  const [sentiment,      setSentiment]      = useState<SentimentData | null>(null);
  const [recommendation, setRecommendation] = useState<FullRecommendation | null>(null);
  const [loading,        setLoading]        = useState(true);
  const [error,          setError]          = useState("");
  const [activeTab,      setActiveTab]      = useState<"overview" | "technical" | "sentiment">("overview");

  useEffect(() => {
    if (!decoded) return;
    loadAll();
  }, [decoded]);

  const loadAll = async () => {
    setLoading(true);
    setError("");
    try {
      const [infoData, techData] = await Promise.all([
        getStockInfo(decoded),
        getTechnicalSignals(decoded),
      ]);
      setInfo(infoData);
      setTechnical(techData);

      const [sentData, recData] = await Promise.all([
        getSentiment(decoded),
        getRecommendation(decoded),
      ]);
      setSentiment(sentData);
      setRecommendation(recData);
    } catch (e) {
      setError("Failed to load stock data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const rec = recommendation?.recommendation;
  const recColor = rec?.recommendation === "BUY"
    ? "text-emerald-400 border-emerald-400"
    : rec?.recommendation === "SELL"
    ? "text-red-400 border-red-400"
    : "text-yellow-400 border-yellow-400";

  const biasColor = technical?.bias === "BULLISH"
    ? "bg-emerald-500/20 text-emerald-400"
    : technical?.bias === "BEARISH"
    ? "bg-red-500/20 text-red-400"
    : "bg-gray-500/20 text-gray-400";

  return (
    <main className="min-h-screen bg-[#0f0f0f] text-white">

      {/* Header */}
      <div className="border-b border-[#262626] px-6 py-4 flex items-center gap-4">
        <button
          onClick={() => router.push("/")}
          className="text-gray-400 hover:text-white transition-colors text-sm"
        >
          ← Back
        </button>
        <span className="text-emerald-400 font-bold text-lg">BharmAstra</span>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8">

        {/* Loading */}
        {loading && (
          <div className="text-center py-20">
            <div className="text-emerald-400 text-xl mb-2">Analyzing {decoded}...</div>
            <p className="text-gray-500 text-sm">Fetching data, running FinBERT and indicators</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400">
            {error}
          </div>
        )}

        {/* Stock Header */}
        {!loading && info && (
          <>
            <div className="mb-8">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-bold">{info.name}</h1>
                <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-3 py-1 rounded-full text-sm font-mono">
                  {decoded}
                </span>
              </div>
              <div className="text-4xl font-bold text-emerald-400 mb-4">
                ₹{info.current_price?.toLocaleString("en-IN")}
              </div>
              <div className="flex gap-3 flex-wrap">
                {[
                  { label: "52W High",  value: `₹${info["52w_high"]}` },
                  { label: "52W Low",   value: `₹${info["52w_low"]}` },
                  { label: "P/E Ratio", value: info.pe_ratio?.toFixed(1) ?? "N/A" },
                  { label: "Sector",    value: info.sector },
                ].map((s) => (
                  <div key={s.label} className="bg-[#1a1a1a] border border-[#262626] rounded-lg px-4 py-2">
                    <div className="text-gray-500 text-xs">{s.label}</div>
                    <div className="text-white text-sm font-semibold">{s.value}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-1 mb-8 border-b border-[#262626]">
              {(["overview", "technical", "sentiment"] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-5 py-3 capitalize text-sm font-medium transition-colors border-b-2 -mb-px ${
                    activeTab === tab
                      ? "border-emerald-400 text-emerald-400"
                      : "border-transparent text-gray-500 hover:text-white"
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>

            {/* OVERVIEW TAB */}
            {activeTab === "overview" && recommendation && (
              <div className="space-y-6">
                <div className="bg-[#1a1a1a] border border-[#262626] rounded-xl p-8 text-center">
                  <div className={`inline-block text-5xl font-black border-2 rounded-2xl px-10 py-4 mb-4 ${recColor}`}>
                    {rec?.recommendation}
                  </div>
                  <div className="text-gray-400 mb-6">
                    {rec?.confidence} CONFIDENCE
                    <span className="mx-2">·</span>
                    powered by {rec?.engine === "gemini" ? "Gemini AI" : "Rule Engine"}
                  </div>

                  {/* Score Bar */}
                  <div className="mb-6">
                    <div className="flex justify-between text-sm text-gray-500 mb-1">
                      <span>Bearish</span>
                      <span>Combined Score: <strong className="text-white">{recommendation.combined_score.toFixed(2)}</strong></span>
                      <span>Bullish</span>
                    </div>
                    <div className="h-3 bg-[#262626] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-red-500 via-yellow-400 to-emerald-500 rounded-full"
                        style={{ width: `${((recommendation.combined_score + 1) / 2) * 100}%` }}
                      />
                    </div>
                  </div>

                  <p className="text-gray-300 text-sm leading-relaxed max-w-2xl mx-auto mb-6">
                    {rec?.summary}
                  </p>

                  {/* Scores */}
                  <div className="grid grid-cols-2 gap-4 max-w-sm mx-auto mb-6">
                    <div className="bg-[#111] rounded-lg p-4">
                      <div className="text-gray-500 text-xs mb-1">Technical Score</div>
                      <div className="text-2xl font-bold text-blue-400">{recommendation.technical_score.toFixed(2)}</div>
                      <div className="text-xs text-gray-600">{recommendation.technical_bias}</div>
                    </div>
                    <div className="bg-[#111] rounded-lg p-4">
                      <div className="text-gray-500 text-xs mb-1">Sentiment Score</div>
                      <div className="text-2xl font-bold text-purple-400">{recommendation.sentiment_score.toFixed(2)}</div>
                      <div className="text-xs text-gray-600">{recommendation.sentiment_label?.toUpperCase()}</div>
                    </div>
                  </div>

                  {/* Target and Stop Loss */}
                  {(rec?.target_price || rec?.stop_loss) && (
                    <div className="flex gap-4 justify-center mb-6">
                      {rec?.target_price && (
                        <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-lg px-6 py-3">
                          <div className="text-gray-500 text-xs">Target Price</div>
                          <div className="text-emerald-400 font-bold">{rec.target_price}</div>
                        </div>
                      )}
                      {rec?.stop_loss && (
                        <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-6 py-3">
                          <div className="text-gray-500 text-xs">Stop Loss</div>
                          <div className="text-red-400 font-bold">{rec.stop_loss}</div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Risks */}
                  {rec?.risks && (
                    <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4 text-left">
                      <div className="text-yellow-400 text-sm font-semibold mb-1">Risks</div>
                      <div className="text-gray-400 text-sm">{rec.risks}</div>
                    </div>
                  )}
                </div>
                <p className="text-gray-600 text-xs text-center">{rec?.disclaimer}</p>
              </div>
            )}

            {/* TECHNICAL TAB */}
            {activeTab === "technical" && technical && (
              <div className="space-y-6">
                <div className={`inline-block px-4 py-2 rounded-full text-sm font-semibold ${biasColor}`}>
                  {technical.bias}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {technical.signals.map((signal) => (
                    <div key={signal.indicator} className="bg-[#1a1a1a] border border-[#262626] rounded-xl p-5">
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-semibold">{signal.indicator}</span>
                        <span className={`text-xs px-2 py-1 rounded-full font-bold ${
                          signal.signal === "BUY"
                            ? "bg-emerald-500/20 text-emerald-400"
                            : signal.signal === "SELL"
                            ? "bg-red-500/20 text-red-400"
                            : "bg-gray-500/20 text-gray-400"
                        }`}>
                          {signal.signal}
                        </span>
                      </div>
                      <p className="text-gray-500 text-sm">{signal.reason}</p>
                    </div>
                  ))}
                </div>

                <div className="bg-[#1a1a1a] border border-[#262626] rounded-xl p-6">
                  <h3 className="font-semibold mb-4 text-gray-300">Latest Indicator Values</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {Object.entries(technical.latest_indicators).map(([key, val]) => (
                      <div key={key} className="bg-[#111] rounded-lg p-3">
                        <div className="text-gray-500 text-xs uppercase mb-1">{key.replace("_", " ")}</div>
                        <div className="text-white font-mono">{val ?? "N/A"}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* SENTIMENT TAB */}
            {activeTab === "sentiment" && sentiment && (
              <div className="space-y-6">
                <div className="bg-[#1a1a1a] border border-[#262626] rounded-xl p-6 text-center">
                  <div
                    className="text-6xl font-black mb-2"
                    style={{
                      color: sentiment.label === "positive" ? "#10b981"
                           : sentiment.label === "negative" ? "#ef4444"
                           : "#9ca3af"
                    }}
                  >
                    {sentiment.sentiment_score.toFixed(2)}
                  </div>
                  <div className="text-gray-400 mb-1">{sentiment.label.toUpperCase()}</div>
                  <div className="text-gray-600 text-sm">{sentiment.article_count} articles analyzed</div>
                  <div className="mt-4 max-w-md mx-auto">
                    <div className="h-3 bg-[#262626] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-red-500 via-yellow-400 to-emerald-500 rounded-full"
                        style={{ width: `${((sentiment.sentiment_score + 1) / 2) * 100}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-gray-600 mt-1">
                      <span>-1.0</span>
                      <span>0</span>
                      <span>+1.0</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  {sentiment.articles.map((article, i) => (
                    <a
                      key={i}
                      href={article.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block bg-[#1a1a1a] border border-[#262626] hover:border-emerald-500/50 rounded-xl p-5 transition-all"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <p className="font-medium text-sm mb-2">{article.title}</p>
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-gray-600 text-xs">{article.source}</span>
                            <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                              article.sentiment === "positive"
                                ? "bg-emerald-500/20 text-emerald-400"
                                : article.sentiment === "negative"
                                ? "bg-red-500/20 text-red-400"
                                : "bg-gray-500/20 text-gray-400"
                            }`}>
                              {article.sentiment.toUpperCase()} {(article.confidence * 100).toFixed(0)}%
                            </span>
                            {article.is_ceo_statement && (
                              <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-500/20 text-yellow-400 font-semibold">
                                CEO Statement
                              </span>
                            )}
                          </div>
                        </div>
                        <span className="text-gray-600 text-xs">↗</span>
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}