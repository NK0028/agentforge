import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { AgentDAG } from './components/AgentDAG';
import { ProjectInput } from './components/ProjectInput';
import { LiveLogs } from './components/LiveLogs';
import { CodeViewer } from './components/CodeViewer';
import { TestResultsPanel } from './components/TestResultsPanel';
import { ReviewScoreCard } from './components/ReviewScoreCard';
import { MemoryViewer } from './components/MemoryViewer';
import { HITLApprovalModal } from './components/HITLApprovalModal';
import { fetchHealth, startProjectRun, fetchWorkspaceFiles } from './services/api';
import { SystemStatus, LogEvent, GeneratedFile, TestResults, ReviewReport, ArchitectureSpec } from './types/agent';

export function App() {
  const [status, setStatus]               = useState<SystemStatus | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>('qwen2.5-coder');
  const [isProcessing, setIsProcessing]   = useState<boolean>(false);
  const [currentStep, setCurrentStep]     = useState<string>('idle');
  const [activeAgent, setActiveAgent]     = useState<string>('System');
  const [retryCount, setRetryCount]       = useState<number>(0);
  const [logs, setLogs]                   = useState<LogEvent[]>([]);
  const [generatedFiles, setGeneratedFiles] = useState<GeneratedFile[]>([]);
  const [testResults, setTestResults]     = useState<TestResults | null>(null);
  const [reviewReport, setReviewReport]   = useState<ReviewReport | null>(null);
  const [logSeen, setLogSeen]             = useState<Set<string>>(new Set());
  const [currentProjectId, setCurrentProjectId] = useState<string | null>(null);

  // HITL Approval State
  const [awaitingApproval, setAwaitingApproval] = useState<boolean>(false);
  const [architectureSpec, setArchitectureSpec] = useState<ArchitectureSpec | null>(null);

  useEffect(() => {
    fetchHealth().then(data => {
      setStatus(data);
      if (data.ollama?.available_models?.length) {
        setSelectedModel(data.ollama.available_models[0]);
      }
    });
  }, []);

  const handleStartProject = async (prompt: string) => {
    setIsProcessing(true);
    setCurrentStep('supervisor');
    setActiveAgent('Supervisor');
    setRetryCount(0);
    setTestResults(null);
    setReviewReport(null);
    setGeneratedFiles([]);
    setAwaitingApproval(false);
    setArchitectureSpec(null);
    setLogSeen(new Set());
    setLogs([{
      agent: 'System',
      message: `🚀 Launching AgentForge for: "${prompt.slice(0, 80)}${prompt.length > 80 ? '…' : ''}"`,
      timestamp: 'now'
    }]);

    try {
      const runRes = await startProjectRun(prompt, selectedModel);
      setCurrentProjectId(runRes.project_id);
      listenToStream(runRes.stream_url, runRes.project_id);
    } catch (err: any) {
      setIsProcessing(false);
      setLogs(l => [...l, { agent: 'System', message: `❌ Error: ${err.message}`, timestamp: 'now' }]);
    }
  };

  const listenToStream = (streamUrl: string, projectId: string) => {
    const eventSource = new EventSource(`http://localhost:8000${streamUrl}`);

    eventSource.addEventListener('log', (e: MessageEvent) => {
      const data: LogEvent = JSON.parse(e.data);
      const key = `${data.agent}:${data.message}`;
      setLogSeen(prev => {
        if (prev.has(key)) return prev;
        const next = new Set(prev); next.add(key);
        setLogs(l => [...l, data]);
        return next;
      });
    });

    eventSource.addEventListener('status', (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      if (data.current_step) setCurrentStep(data.current_step);
      if (data.active_agent) setActiveAgent(data.active_agent);
      if (typeof data.retry_count === 'number') setRetryCount(data.retry_count);
      if (data.test_results)  setTestResults(data.test_results);
      if (data.review_report) setReviewReport(data.review_report);
      if (typeof data.awaiting_approval === 'boolean') {
        setAwaitingApproval(data.awaiting_approval);
        if (data.architecture) setArchitectureSpec(data.architecture);
      }
    });

    eventSource.addEventListener('awaiting_approval', (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      setAwaitingApproval(true);
      if (data.architecture) setArchitectureSpec(data.architecture);
    });

    eventSource.addEventListener('file_created', (e: MessageEvent) => {
      const file: GeneratedFile = JSON.parse(e.data);
      setGeneratedFiles(prev => [...prev.filter(f => f.path !== file.path), file]);
    });

    eventSource.addEventListener('file_patched', (e: MessageEvent) => {
      const file: GeneratedFile = JSON.parse(e.data);
      setGeneratedFiles(prev => prev.map(f => f.path === file.path ? file : f));
    });

    eventSource.addEventListener('test_results', (e: MessageEvent) => {
      setTestResults(JSON.parse(e.data));
    });

    eventSource.addEventListener('review_report', (e: MessageEvent) => {
      setReviewReport(JSON.parse(e.data));
    });

    eventSource.addEventListener('complete', () => {
      setIsProcessing(false);
      setAwaitingApproval(false);
      setCurrentStep('completed');
      setActiveAgent('System');
      setLogs(l => [...l, {
        agent: 'System',
        message: '🎉 AgentForge 9-Node Pipeline Completed Successfully!',
        timestamp: 'now'
      }]);
      if (projectId) {
        fetchWorkspaceFiles(projectId).then(files => {
          if (files.length > 0) setGeneratedFiles(files);
        });
      }
      eventSource.close();
    });

    eventSource.onerror = () => {
      setIsProcessing(false);
      eventSource.close();
    };
  };

  const handleHITLApprove = async (modifiedFiles?: Array<{ path: string; purpose: string }>) => {
    if (!currentProjectId) return;
    setAwaitingApproval(false);

    try {
      const res = await fetch(`http://localhost:8000/api/agent/resume/${currentProjectId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved: true, modified_files: modifiedFiles })
      });
      const data = await res.json();
      if (data.status === 'RESUMED') {
        listenToStream(`/api/agent/stream/${currentProjectId}`, currentProjectId);
      }
    } catch (err: any) {
      setLogs(l => [...l, { agent: 'System', message: `❌ Error resuming run: ${err.message}`, timestamp: 'now' }]);
    }
  };

  const handleHITLReject = async () => {
    if (!currentProjectId) return;
    setAwaitingApproval(false);
    setIsProcessing(false);
    await fetch(`http://localhost:8000/api/agent/resume/${currentProjectId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approved: false })
    });
  };

  return (
    <div className="min-h-screen bg-dark-900 text-slate-100 flex flex-col font-sans">
      <Header status={status} selectedModel={selectedModel} onModelChange={setSelectedModel} />

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 space-y-5">

        {/* Prompt Input */}
        <ProjectInput onStart={handleStartProject} isProcessing={isProcessing} />

        {/* Visual 9-Node DAG */}
        <AgentDAG
          currentStep={currentStep}
          activeAgent={activeAgent}
          isProcessing={isProcessing}
          retryCount={retryCount}
          awaitingApproval={awaitingApproval}
        />

        {/* Primary row: Logs + Code Workspace */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <LiveLogs logs={logs} />
          <CodeViewer files={generatedFiles} projectId={currentProjectId} />
        </div>

        {/* Secondary row: Test Results + Review Scorecard */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <TestResultsPanel testResults={testResults} />
          <ReviewScoreCard   report={reviewReport} />
        </div>

        {/* Phase 3: ChromaDB RAG Vector Memory Base Viewer */}
        <MemoryViewer />

      </main>

      {/* Phase 4: Human-In-The-Loop Approval Modal */}
      <HITLApprovalModal
        isOpen={awaitingApproval}
        architecture={architectureSpec}
        onApprove={handleHITLApprove}
        onReject={handleHITLReject}
      />
    </div>
  );
}

export default App;
