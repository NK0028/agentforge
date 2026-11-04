import React from 'react';
import {
  Compass, Layout, Code, ShieldCheck, CheckCircle2,
  Loader2, ArrowRight, FlaskConical, Bug, ClipboardList,
  FileText, Box, ShieldAlert
} from 'lucide-react';

interface AgentDAGProps {
  currentStep: string;
  activeAgent: string;
  isProcessing: boolean;
  retryCount?: number;
  awaitingApproval?: boolean;
}

const nodes = [
  { id: 'supervisor', label: 'Supervisor',  icon: ShieldCheck,    role: 'Orchestrator'  },
  { id: 'planner',    label: 'Planner',     icon: Compass,         role: 'Requirements'  },
  { id: 'architect',  label: 'Architect',   icon: Layout,          role: 'System Spec'   },
  { id: 'hitl',       label: 'HITL',        icon: ShieldAlert,     role: 'Approval'      },
  { id: 'coder',      label: 'Coder',       icon: Code,            role: 'Code Gen'      },
  { id: 'tester',     label: 'Tester',      icon: FlaskConical,    role: 'Syntax Check'  },
  { id: 'debugger',   label: 'Debugger',    icon: Bug,             role: 'Self-Heal'     },
  { id: 'reviewer',   label: 'Reviewer',    icon: ClipboardList,   role: 'Code Audit'    },
  { id: 'docgen',     label: 'DocGen',      icon: FileText,        role: 'Docs Gen'      },
  { id: 'deployer',   label: 'Deployer',    icon: Box,             role: 'DevOps'        },
];

export const AgentDAG: React.FC<AgentDAGProps> = ({
  currentStep, activeAgent, isProcessing, retryCount = 0, awaitingApproval = false
}) => {
  const getStatus = (nodeId: string) => {
    const active = activeAgent.toLowerCase();
    if (!isProcessing && currentStep === 'completed') return 'completed';
    if (awaitingApproval && nodeId === 'hitl') return 'active';
    if (active === nodeId || currentStep === nodeId) return 'active';

    const order = ['supervisor', 'planner', 'architect', 'hitl', 'coder', 'tester', 'debugger', 'reviewer', 'docgen', 'deployer'];
    const currentIdx = order.indexOf(active !== 'system' ? active : currentStep);
    const nodeIdx = order.indexOf(nodeId);
    if (currentIdx > nodeIdx) return 'completed';
    return 'idle';
  };

  const nodeColor = {
    active:    'bg-brand-600/20 border-brand-500 shadow-lg shadow-brand-500/20 ring-1 ring-brand-500',
    completed: 'bg-emerald-500/10 border-emerald-500/30',
    idle:      'bg-dark-900/60 border-dark-700/60 opacity-50',
  };

  const iconColor = {
    active:    'bg-brand-500 text-white',
    completed: 'bg-emerald-500/20 text-emerald-400',
    idle:      'bg-dark-800 text-slate-500',
  };

  return (
    <div className="glass-panel rounded-2xl p-5 border border-dark-700/80 mb-6">
      <div className="flex flex-wrap items-center justify-between mb-4 gap-2">
        <div>
          <h3 className="text-sm font-semibold text-white tracking-wide uppercase">
            Complete 9-Node Agent Pipeline
          </h3>
          <p className="text-xs text-slate-400">
            Autonomous Software Engineering Engine with HITL & DevOps Automation
          </p>
        </div>
        <div className="flex items-center gap-2">
          {awaitingApproval && (
            <div className="text-xs bg-amber-500/20 text-amber-300 border border-amber-500/40 px-3 py-1 rounded-full font-bold animate-bounce">
              ⚠️ Awaiting Architecture Approval
            </div>
          )}
          {retryCount > 0 && (
            <div className="text-xs bg-amber-500/10 text-amber-400 border border-amber-500/20 px-3 py-1 rounded-full font-semibold">
              🔁 Debug Retry #{retryCount}
            </div>
          )}
          {isProcessing && !awaitingApproval && (
            <div className="flex items-center space-x-2 bg-brand-500/10 text-brand-400 text-xs px-3 py-1 rounded-full border border-brand-500/20 animate-pulse">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span className="font-semibold">Running: {activeAgent}</span>
            </div>
          )}
        </div>
      </div>

      {/* DAG grid */}
      <div className="grid grid-cols-2 sm:grid-cols-5 lg:grid-cols-10 gap-2">
        {nodes.map((node, index) => {
          const status = getStatus(node.id) as 'active' | 'completed' | 'idle';
          const Icon = node.icon;
          return (
            <div key={node.id} className="relative">
              <div className={`p-2.5 rounded-xl border transition-all duration-300 ${nodeColor[status]}`}>
                <div className="flex items-center justify-between mb-1.5">
                  <div className={`p-1.5 rounded-lg ${iconColor[status]}`}>
                    <Icon className="w-3.5 h-3.5" />
                  </div>
                  {status === 'completed' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                  {status === 'active'    && <Loader2 className="w-3.5 h-3.5 text-brand-400 animate-spin" />}
                </div>
                <h4 className="text-[11px] font-bold text-white tracking-wide">{node.label}</h4>
                <p  className="text-[9px] text-slate-400 truncate">{node.role}</p>
                <div className="mt-1 text-[9px] font-mono">
                  {status === 'active'    && <span className="text-brand-400 font-semibold">● Active</span>}
                  {status === 'completed' && <span className="text-emerald-400 font-semibold">✓ Done</span>}
                  {status === 'idle'      && <span className="text-slate-600">Standby</span>}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
