import React, { useState } from 'react';
import { FolderTree, FileCode, Copy, Check, Download } from 'lucide-react';
import { GeneratedFile } from '../types/agent';

interface CodeViewerProps {
  files: GeneratedFile[];
  projectId?: string | null;
}

export const CodeViewer: React.FC<CodeViewerProps> = ({ files, projectId }) => {
  const [selectedFilePath, setSelectedFilePath] = useState<string>(files[0]?.path || '');
  const [copied, setCopied] = useState(false);

  const currentFile = files.find(f => f.path === selectedFilePath) || files[0];

  const handleCopy = () => {
    if (currentFile) {
      navigator.clipboard.writeText(currentFile.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownloadZip = () => {
    if (projectId) {
      window.location.href = `http://localhost:8000/api/agent/export/${projectId}`;
    }
  };

  return (
    <div className="glass-panel rounded-2xl border border-dark-700/80 flex flex-col h-[420px]">
      <div className="px-5 py-3.5 border-b border-dark-700/80 flex items-center justify-between bg-dark-900/60 rounded-t-2xl">
        <div className="flex items-center space-x-2">
          <FolderTree className="w-4 h-4 text-brand-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">Generated Project Workspace</h3>
        </div>
        <div className="flex items-center space-x-2">
          {projectId && files.length > 0 && (
            <button
              onClick={handleDownloadZip}
              className="flex items-center space-x-1.5 text-xs text-white bg-brand-600 hover:bg-brand-500 px-3 py-1 rounded-md border border-brand-500 shadow-md font-semibold transition"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download ZIP</span>
            </button>
          )}

          {currentFile && (
            <button
              onClick={handleCopy}
              className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white bg-dark-800 px-2.5 py-1 rounded-md border border-dark-700 transition"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy Code'}</span>
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 flex-1 overflow-hidden">
        {/* File Tree Sidebar */}
        <div className="border-r border-dark-700/80 bg-dark-900/40 p-3 overflow-y-auto space-y-1">
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2 mb-2">Files ({files.length})</p>
          {files.length === 0 ? (
            <p className="text-xs text-slate-500 italic px-2 py-4">No generated files yet...</p>
          ) : (
            files.map((file) => (
              <button
                key={file.path}
                onClick={() => setSelectedFilePath(file.path)}
                className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-mono flex items-center space-x-2 transition ${
                  (selectedFilePath || files[0]?.path) === file.path
                    ? 'bg-brand-600/20 text-brand-300 font-semibold border border-brand-500/30'
                    : 'text-slate-400 hover:bg-dark-800 hover:text-slate-200'
                }`}
              >
                <FileCode className="w-3.5 h-3.5 text-brand-400 shrink-0" />
                <span className="truncate">{file.path}</span>
              </button>
            ))
          )}
        </div>

        {/* Code Editor Preview Pane */}
        <div className="md:col-span-2 p-4 bg-dark-950 overflow-y-auto font-mono text-xs text-slate-200">
          {currentFile ? (
            <pre className="whitespace-pre-wrap leading-relaxed">{currentFile.content}</pre>
          ) : (
            <div className="h-full flex items-center justify-center text-slate-500 italic">
              Select a generated file to preview code
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
