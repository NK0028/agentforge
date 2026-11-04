import React, { useState } from 'react';
import { ShieldAlert, CheckCircle, Edit3, ArrowRight, X } from 'lucide-react';
import { ArchitectureSpec } from '../types/agent';

interface HITLApprovalModalProps {
  isOpen: boolean;
  architecture: ArchitectureSpec | null;
  onApprove: (modifiedFiles?: Array<{ path: string; purpose: string }>) => void;
  onReject: () => void;
}

export const HITLApprovalModal: React.FC<HITLApprovalModalProps> = ({
  isOpen, architecture, onApprove, onReject
}) => {
  if (!isOpen || !architecture) return null;

  const [files, setFiles] = useState(architecture.files || []);

  const handleFileChange = (index: number, key: 'path' | 'purpose', value: string) => {
    const next = [...files];
    next[index][key] = value;
    setFiles(next);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="glass-panel w-full max-w-2xl rounded-2xl border border-brand-500/40 p-6 shadow-2xl space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-dark-700 pb-3">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-amber-500/20 text-amber-400">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Human-In-The-Loop Checkpoint</h3>
              <p className="text-xs text-slate-400">Review & Approve Software Architecture Before Coding</p>
            </div>
          </div>
          <button onClick={onReject} className="text-slate-400 hover:text-white p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Target Files Spec Table */}
        <div className="space-y-2">
          <p className="text-xs font-semibold text-slate-300 flex items-center space-x-1.5">
            <Edit3 className="w-3.5 h-3.5 text-brand-400" />
            <span>Proposed Architecture Files (Edit paths or purposes as needed):</span>
          </p>

          <div className="max-h-60 overflow-y-auto space-y-2 pr-1">
            {files.map((file, idx) => (
              <div key={idx} className="bg-dark-900/90 p-3 rounded-xl border border-dark-700 flex flex-col gap-1.5 text-xs">
                <input
                  type="text"
                  value={file.path}
                  onChange={(e) => handleFileChange(idx, 'path', e.target.value)}
                  className="font-mono text-brand-300 font-semibold bg-dark-950 px-2.5 py-1 rounded border border-dark-700 focus:border-brand-500 focus:outline-none"
                  placeholder="Target File Path"
                />
                <input
                  type="text"
                  value={file.purpose}
                  onChange={(e) => handleFileChange(idx, 'purpose', e.target.value)}
                  className="text-slate-300 bg-transparent px-1 focus:outline-none text-[11px]"
                  placeholder="File Purpose / Responsibilities"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end space-x-3 pt-2 border-t border-dark-700/60">
          <button
            onClick={onReject}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:bg-dark-800 hover:text-white transition"
          >
            Reject / Cancel Run
          </button>

          <button
            onClick={() => onApprove(files)}
            className="px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 shadow-lg shadow-brand-500/25 flex items-center space-x-2 transition"
          >
            <CheckCircle className="w-4 h-4" />
            <span>Approve & Start Coding</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
