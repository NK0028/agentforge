import React, { useRef, useEffect } from 'react';
import { Terminal, ShieldCheck, Compass, Layout, Code, AlertCircle } from 'lucide-react';
import { LogEvent } from '../types/agent';

interface LiveLogsProps {
  logs: LogEvent[];
}

export const LiveLogs: React.FC<LiveLogsProps> = ({ logs }) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const getAgentBadge = (agent: string) => {
    switch (agent.toLowerCase()) {
      case 'supervisor':
        return { icon: ShieldCheck, color: 'bg-amber-500/20 text-amber-300 border-amber-500/30' };
      case 'planner':
        return { icon: Compass, color: 'bg-blue-500/20 text-blue-300 border-blue-500/30' };
      case 'architect':
        return { icon: Layout, color: 'bg-purple-500/20 text-purple-300 border-purple-500/30' };
      case 'coder':
        return { icon: Code, color: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' };
      default:
        return { icon: Terminal, color: 'bg-slate-700/50 text-slate-300 border-slate-600' };
    }
  };

  return (
    <div className="glass-panel rounded-2xl border border-dark-700/80 flex flex-col h-[400px]">
      <div className="px-5 py-3.5 border-b border-dark-700/80 flex items-center justify-between bg-dark-900/60 rounded-t-2xl">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-brand-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">Live Agent Stream Terminal</h3>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-red-500/80"></span>
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80"></span>
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80"></span>
        </div>
      </div>

      <div ref={scrollRef} className="p-4 overflow-y-auto font-mono text-xs space-y-3 flex-1">
        {logs.length === 0 ? (
          <div className="h-full flex items-center justify-center text-slate-500 text-xs italic">
            Waiting for agent execution prompt...
          </div>
        ) : (
          logs.map((log, index) => {
            const badge = getAgentBadge(log.agent);
            const Icon = badge.icon;
            return (
              <div key={index} className="flex items-start space-x-3 leading-relaxed border-b border-dark-800/60 pb-2">
                <span className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-semibold border ${badge.color}`}>
                  <Icon className="w-3 h-3" />
                  <span>{log.agent}</span>
                </span>
                <span className="text-slate-300 flex-1">{log.message}</span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
