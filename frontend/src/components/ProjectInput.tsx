import React, { useState } from 'react';
import { Sparkles, Play, Loader2 } from 'lucide-react';

interface ProjectInputProps {
  onStart: (prompt: string) => void;
  isProcessing: boolean;
}

export const ProjectInput: React.FC<ProjectInputProps> = ({ onStart, isProcessing }) => {
  const [prompt, setPrompt] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim() && !isProcessing) {
      onStart(prompt.trim());
    }
  };

  const samplePrompts = [
    "Build a real-time weather dashboard with interactive charts and search.",
    "Build a RESTful FastAPI URL shortener with analytics and SQLite persistence.",
    "Create a markdown blog engine with dark mode theme and tag filtering."
  ];

  return (
    <div className="glass-panel rounded-2xl p-5 border border-dark-700/80 mb-6 shadow-2xl">
      <form onSubmit={handleSubmit}>
        <div className="flex items-center justify-between mb-3">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-200 flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-brand-400" />
            <span>Describe Your Target Application</span>
          </label>
          <span className="text-[11px] text-slate-400">AgentForge autonomous multi-agent pipeline will take over</span>
        </div>

        <div className="relative">
          <textarea
            rows={3}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isProcessing}
            placeholder="e.g. Build a lightweight task manager API with FastAPI, Pydantic schemas, SQLite storage, and a clean HTML dashboard..."
            className="w-full bg-dark-900/90 text-slate-100 placeholder-slate-500 rounded-xl p-4 text-sm border border-dark-700 focus:border-brand-500 focus:ring-1 focus:ring-brand-500 focus:outline-none transition resize-none font-sans"
          />

          <div className="mt-3 flex items-center justify-between">
            <div className="flex flex-wrap gap-2">
              <span className="text-[11px] text-slate-400 self-center">Try:</span>
              {samplePrompts.map((sp, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setPrompt(sp)}
                  disabled={isProcessing}
                  className="text-[11px] bg-dark-800 hover:bg-dark-700 text-slate-300 px-2.5 py-1 rounded-lg border border-dark-700 transition"
                >
                  {sp.slice(0, 35)}...
                </button>
              ))}
            </div>

            <button
              type="submit"
              disabled={!prompt.trim() || isProcessing}
              className="flex items-center space-x-2 bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 disabled:opacity-50 text-white font-semibold text-xs px-5 py-2.5 rounded-xl shadow-lg shadow-brand-500/25 transition duration-200 shrink-0"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Generating Project...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-white" />
                  <span>Launch AgentForge</span>
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};
