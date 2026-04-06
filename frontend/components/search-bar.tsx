'use client';

import { SearchIcon } from 'lucide-react';
import { useState } from 'react';

export default function SearchBar() {
  const [searchValue, setSearchValue] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Searching for:', searchValue);
  };

  return (
    <form onSubmit={handleSearch} className="w-full max-w-2xl">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <input
            type="text"
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            placeholder="Search stock or company... (e.g. Reliance, TCS, INFY)"
            className="w-full rounded-lg border border-border bg-input px-4 py-3 text-foreground placeholder-muted-foreground focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/30"
          />
        </div>
        <button
          type="submit"
          className="flex items-center gap-2 rounded-lg bg-accent px-6 py-3 font-semibold text-accent-foreground transition-all hover:bg-accent/90"
        >
          <SearchIcon size={18} />
          <span className="hidden sm:inline">Search</span>
        </button>
      </div>
    </form>
  );
}
