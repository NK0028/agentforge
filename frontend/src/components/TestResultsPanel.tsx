import React from 'react';
import { FlaskConical, CheckCircle2, XCircle, FileCode2 } from 'lucide-react';
import { TestResults } from '../types/agent';

interface TestResultsPanelProps {
  testResults: TestResults | null;
}

export const TestResultsPanel: React.FC<TestResultsPanelProps> = ({ testResults }) => {
  if (!testResults) {
    return (
      <div className="glass-panel rounded-2xl border border-dark-700/80 p-5 flex items-center justify-center h-40">
        <div className="text-center">
          <FlaskConical className="w-8 h-8 text-slate-600 mx-auto mb-2" />
          <p className="text-xs text-slate-500 italic">Test results will appear after code generation</p>
        </div>
      </div>
    );
  }

  const { overall_passed, passed, failed, total_files, file_results } = testResults;

  return (
    <div className="glass-panel rounded-2xl border border-dark-700/80 overflow-hidden">
      {/* Header */}
      <div className="px-5 py-3.5 border-b border-dark-700/80 flex items-center justify-between bg-dark-900/60">
        <div className="flex items-center space-x-2">
          <FlaskConical className={`w-4 h-4 ${overall_passed ? 'text-emerald-400' : 'text-red-400'}`} />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Test Suite Results
          </h3>
        </div>
        <div className={`flex items-center space-x-1.5 text-xs font-bold px-3 py-1 rounded-full border ${
          overall_passed
            ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
            : 'bg-red-500/10 text-red-300 border-red-500/30'
        }`}>
          {overall_passed ? <CheckCircle2 className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
          <span>{overall_passed ? 'ALL PASSED' : `${failed} FAILED`}</span>
        </div>
      </div>

      {/* Score bar */}
      <div className="px-5 py-3 border-b border-dark-800/60 flex items-center gap-4">
        <div className="flex-1 bg-dark-900 rounded-full h-2 overflow-hidden">
          <div
            className={`h-2 rounded-full transition-all duration-700 ${overall_passed ? 'bg-emerald-500' : 'bg-amber-500'}`}
            style={{ width: total_files ? `${(passed / total_files) * 100}%` : '0%' }}
          />
        </div>
        <span className="text-xs font-mono text-slate-300 shrink-0">
          {passed}/{total_files} files
        </span>
      </div>

      {/* Per-file results */}
      <div className="p-3 space-y-1.5 max-h-52 overflow-y-auto">
        {file_results.map((fr, i) => (
          <div key={i} className={`flex items-start space-x-2.5 px-3 py-2 rounded-lg text-xs ${
            fr.passed ? 'bg-emerald-500/5 border border-emerald-500/10' : 'bg-red-500/5 border border-red-500/20'
          }`}>
            {fr.passed
              ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
              : <XCircle     className="w-3.5 h-3.5 text-red-400 mt-0.5 shrink-0" />
            }
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="font-mono text-slate-200 truncate">{fr.path}</span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded font-semibold ml-2 shrink-0 ${
                  fr.passed ? 'bg-emerald-500/20 text-emerald-300' : 'bg-red-500/20 text-red-300'
                }`}>
                  {fr.language}
                </span>
              </div>
              {!fr.passed && fr.stderr && (
                <p className="text-red-400 font-mono text-[10px] mt-1 truncate">{fr.stderr}</p>
              )}
              {fr.note && (
                <p className="text-slate-500 text-[10px] mt-0.5 italic">{fr.note}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
