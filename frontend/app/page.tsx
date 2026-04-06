// app/page.tsx
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { searchTicker } from "@/lib/api";

export default function Home() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    setError("");
    try {
      const result = await searchTicker(searchQuery);
      router.push(`/stock/${encodeURIComponent(result.resolved_ticker)}`);
    } catch (e) {
      setError("Could not find that stock. Try a ticker like RELIANCE.NS");
    } finally {
      setLoading(false);
    }
  };

  const quickPicks = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS",
    "HDFCBANK.NS", "SBIN.NS", "TATAMOTORS.NS"
  ];

  return (
    <main className="min-h-screen bg-[#0f0f0f] text-white flex flex-col items-center justify-center px-4">
      
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold text-emerald-400 mb-2">BharmAstra</h1>
        <p className="text-gray-400 text-lg">AI-Powered Indian Stock Predictor</p>
      </div>

      {/* Search Bar */}
      <div className="w-full max-w-2xl mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch(query)}
            placeholder="Search stock or company... (e.g. Reliance, TCS, INFY)"
            className="flex-1 bg-[#1a1a1a] border border-[#262626] rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500"
          />
          <button
            onClick={() => handleSearch(query)}
            disabled={loading}
            className="bg-emerald-500 hover:bg-emerald-600 text-black font-semibold px-6 py-3 rounded-lg transition-colors disabled:opacity-50"
          >
            {loading ? "..." : "Search"}
          </button>
        </div>
        {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
      </div>

      {/* Quick Picks */}
      <div className="flex flex-wrap gap-2 mb-16 justify-center">
        {quickPicks.map((ticker) => (
          <button
            key={ticker}
            onClick={() => handleSearch(ticker)}
            className="bg-[#1a1a1a] border border-[#262626] hover:border-emerald-500 text-gray-300 hover:text-emerald-400 px-4 py-2 rounded-full text-sm transition-all"
          >
            {ticker}
          </button>
        ))}
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl w-full">
        {[
          {
            icon: "📰",
            title: "Sentiment Analysis",
            desc: "Real-time news sentiment using FinBERT AI"
          },
          {
            icon: "📈",
            title: "Technical Analysis",
            desc: "RSI, MACD, Bollinger Bands & more"
          },
          {
            icon: "🤖",
            title: "AI Recommendation",
            desc: "BUY / HOLD / SELL powered by Gemini AI"
          },
        ].map((card) => (
          <div
            key={card.title}
            className="bg-[#1a1a1a] border border-[#262626] rounded-xl p-6 text-center hover:border-emerald-500/50 transition-all"
          >
            <div className="text-4xl mb-3">{card.icon}</div>
            <h3 className="text-emerald-400 font-semibold text-lg mb-2">{card.title}</h3>
            <p className="text-gray-500 text-sm">{card.desc}</p>
          </div>
        ))}
      </div>

    </main>
  );
}