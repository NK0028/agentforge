import React from 'react';
import { ClipboardList, ShieldCheck, Star, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';
import { ReviewReport, ReviewFinding } from '../types/agent';

interface ReviewScoreCardProps {
  report: ReviewReport | null;
}

const ScoreBar: React.FC<{ label: string; score: number; icon?: React.ReactNode }> = ({ label, score, icon }) => {
  const color = score >= 8 ? 'bg-emerald-500' : score >= 6 ? 'bg-amber-500' : 'bg-red-500';
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center space-x-1.5">
          {icon}
          <span className="text-[11px] text-slate-300">{label}</span>
        </div>
        <span className={`text-[11px] font-bold ${score >= 8 ? 'text-emerald-400' : score >= 6 ? 'text-amber-400' : 'text-red-400'}`}>
          {score}/10
        </span>
      </div>
      <div className="bg-dark-900 rounded-full h-1.5 overflow-hidden">
        <div className={`h-1.5 rounded-full transition-all duration-700 ${color}`} style={{ width: `${score * 10}%` }} />
      </div>
    </div>
  );
};

const FindingBadge: React.FC<{ finding: ReviewFinding }> = ({ finding }) => {
  const config = {
    info:     { icon: <CheckCircle2 className="w-3 h-3" />,   cls: 'text-blue-300 bg-blue-500/10 border-blue-500/20'   },
    warning:  { icon: <AlertTriangle className="w-3 h-3" />,  cls: 'text-amber-300 bg-amber-500/10 border-amber-500/20' },
    critical: { icon: <XCircle className="w-3 h-3" />,        cls: 'text-red-300 bg-red-500/10 border-red-500/20'       },
  }[finding.severity] ?? { icon: null, cls: '' };

  return (
    <div className={`flex items-start space-x-2 text-[11px] px-2.5 py-1.5 rounded-lg border ${config.cls}`}>
      <span className="mt-0.5 shrink-0">{config.icon}</span>
      <div>
        <span className="font-mono font-semibold">{finding.file}</span>
        <span className="text-slate-400 ml-1">— {finding.message}</span>
      </div>
    </div>
  );
};

export const ReviewScoreCard: React.FC<ReviewScoreCardProps> = ({ report }) => {
  if (!report) {
    return (
      <div className="glass-panel rounded-2xl border border-dark-700/80 p-5 flex items-center justify-center h-40">
        <div className="text-center">
          <ClipboardList className="w-8 h-8 text-slate-600 mx-auto mb-2" />
          <p className="text-xs text-slate-500 italic">Code review report will appear after tests pass</p>
        </div>
      </div>
    );
  }

  const { overall_score, quality_score, security_score, completeness_score,
          best_practices_score, findings, summary, approved } = report;

  return (
    <div className="glass-panel rounded-2xl border border-dark-700/80 overflow-hidden">
      {/* Header */}
      <div className="px-5 py-3.5 border-b border-dark-700/80 flex items-center justify-between bg-dark-900/60">
        <div className="flex items-center space-x-2">
          <ClipboardList className={`w-4 h-4 ${approved ? 'text-emerald-400' : 'text-amber-400'}`} />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">Code Review Scorecard</h3>
        </div>
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1">
            <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
            <span className="text-sm font-bold text-white">{overall_score.toFixed(1)}</span>
            <span className="text-xs text-slate-400">/10</span>
          </div>
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
            approved ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30' : 'bg-amber-500/10 text-amber-300 border-amber-500/30'
          }`}>
            {approved ? '✅ APPROVED' : '⚠️ REVIEW'}
          </span>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Score bars */}
        <div className="space-y-2.5">
          <ScoreBar label="Code Quality"    score={quality_score}        icon={<Star className="w-3 h-3 text-brand-400" />} />
          <ScoreBar label="Security"        score={security_score}       icon={<ShieldCheck className="w-3 h-3 text-emerald-400" />} />
          <ScoreBar label="Completeness"    score={completeness_score}   icon={<CheckCircle2 className="w-3 h-3 text-blue-400" />} />
          <ScoreBar label="Best Practices"  score={best_practices_score} icon={<ClipboardList className="w-3 h-3 text-purple-400" />} />
        </div>

        {/* Summary */}
        {summary && (
          <p className="text-[11px] text-slate-400 italic border-t border-dark-700/60 pt-3">{summary}</p>
        )}

        {/* Findings */}
        {findings.length > 0 && (
          <div className="space-y-1.5 border-t border-dark-700/60 pt-3">
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Findings</p>
            {findings.slice(0, 4).map((f, i) => (
              <FindingBadge key={i} finding={f} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
