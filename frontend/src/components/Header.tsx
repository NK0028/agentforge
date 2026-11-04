import React from 'react';
import { Cpu, Server, Activity, ShieldCheck, Github } from 'lucide-react';
import { SystemStatus } from '../types/agent';

interface HeaderProps {
  status: SystemStatus | null;
  selectedModel: string;
  onModelChange: (model: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ status, selectedModel, onModelChange }) => {
  const isOllamaOnline = status?.ollama?.online ?? false;
  const models = status?.ollama?.available_models.length ? status.ollama.available_models : ['qwen2.5-coder', 'deepseek-r1', 'llama3.1'];

  return (
    <header className="glass-panel border-b border-dark-700/80 px-6 py-3.5 flex items-center justify-between sticky top-0 z-50">
      <div className="flex items-center space-x-3">
        <div className="bg-gradient-to-tr from-brand-600 to-indigo-500 p-2.5 rounded-xl shadow-lg shadow-brand-500/20">
          <Cpu className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="font-bold text-lg tracking-tight text-white">AgentForge</h1>
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-400 border border-brand-500/30">
              v0.1.0 MVP
            </span>
          </div>
          <p className="text-xs text-slate-400">Open-Source Local Multi-Agent AI Engineering Engine</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* Model Selector */}
        <div className="flex items-center space-x-2 bg-dark-900/90 px-3 py-1.5 rounded-lg border border-dark-700">
          <Server className="w-4 h-4 text-brand-400" />
          <span className="text-xs text-slate-400 font-medium">Model:</span>
          <select 
            value={selectedModel} 
            onChange={(e) => onModelChange(e.target.value)}
            className="bg-transparent text-xs text-slate-200 font-semibold focus:outline-none cursor-pointer"
          >
            {models.map(m => (
              <option key={m} value={m} className="bg-dark-800 text-slate-200">{m}</option>
            ))}
          </select>
        </div>

        {/* Ollama Status Indicator */}
        <div className="flex items-center space-x-2 bg-dark-900/90 px-3 py-1.5 rounded-lg border border-dark-700">
          <Activity className={`w-3.5 h-3.5 ${isOllamaOnline ? 'text-emerald-400 animate-pulse' : 'text-amber-400'}`} />
          <span className="text-xs text-slate-300 font-medium">
            {isOllamaOnline ? 'Ollama Online' : 'Ollama Standby'}
          </span>
        </div>

        {/* Security badge */}
        <div className="hidden md:flex items-center space-x-1 text-xs text-slate-400 bg-emerald-500/10 px-2.5 py-1.5 rounded-lg border border-emerald-500/20">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-emerald-300 font-medium">100% Local</span>
        </div>
      </div>
    </header>
  );
};
