import React, { useState, useEffect } from 'react';
import { Database, Search, Sparkles, FileCode, Server } from 'lucide-react';

interface MemoryHit {
  content: string;
  similarity: number;
  metadata: {
    project_id?: string;
    file_path?: string;
    memory_type?: string;
  };
}

export const MemoryViewer: React.FC = () => {
  const [query, setQuery] = useState('');
  const [hits, setHits] = useState<MemoryHit[]>([]);
  const [stats, setStats] = useState<{ total_chunks: number; collection: string } | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/agent/memory/stats');
      const data = await res.json();
      setStats(data);
    } catch {
      setStats({ total_chunks: 0, collection: 'agentforge_knowledge' });
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/agent/memory/search?q=${encodeURIComponent(query)}&n=4`);
      const data = await res.json();
      setHits(data.hits || []);
    } catch {
      setHits([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel rounded-2xl border border-dark-700/80 p-5 mt-6">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
        <div className="flex items-center space-x-2">
          <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
            <Database className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              ChromaDB RAG Memory Base
            </h3>
            <p className="text-xs text-slate-400">Phase 3: Long-Term Episodic & Semantic Code Vector Memory</p>
          </div>
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <div className="bg-dark-900 px-3 py-1.5 rounded-lg border border-dark-700 font-mono text-slate-300">
            <span className="text-slate-500 mr-1.5">Indexed Chunks:</span>
            <span className="font-bold text-indigo-400">{stats?.total_chunks ?? 0}</span>
          </div>
        </div>
      </div>

      {/* RAG Search Bar */}
      <form onSubmit={handleSearch} className="flex gap-2 mb-4">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search vector memory base (e.g. FastAPI database connection, React components)..."
            className="w-full bg-dark-900 text-xs text-slate-200 placeholder-slate-500 pl-9 pr-3 py-2 rounded-xl border border-dark-700 focus:border-indigo-500 focus:outline-none"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold px-4 py-2 rounded-xl flex items-center space-x-1.5 transition"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Vector Search</span>
        </button>
      </form>

      {/* Results view */}
      {hits.length > 0 && (
        <div className="space-y-2 max-h-60 overflow-y-auto">
          {hits.map((hit, idx) => (
            <div key={idx} className="bg-dark-950 p-3 rounded-xl border border-dark-800 text-xs">
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center space-x-1.5 font-mono text-indigo-300 text-[11px]">
                  <FileCode className="w-3.5 h-3.5 text-indigo-400" />
                  <span>{hit.metadata?.file_path || 'Semantic Snippet'}</span>
                  {hit.metadata?.project_id && (
                    <span className="text-slate-500 text-[10px]">[{hit.metadata.project_id}]</span>
                  )}
                </div>
                <span className="text-[10px] bg-indigo-500/10 text-indigo-300 px-2 py-0.5 rounded font-mono font-bold border border-indigo-500/20">
                  {(hit.similarity * 100).toFixed(1)}% Match
                </span>
              </div>
              <pre className="text-[11px] text-slate-300 font-mono whitespace-pre-wrap line-clamp-3 bg-dark-900 p-2 rounded-lg border border-dark-800">
                {hit.content}
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
