export interface LogEvent {
  agent: string;
  message: string;
  timestamp: string;
}

export interface GeneratedFile {
  path: string;
  content: string;
}

export interface ProjectPlan {
  project_name: string;
  summary: string;
  tech_stack: {
    frontend?: string;
    backend?: string;
    database?: string;
  };
  milestones: Array<{
    step: number;
    title: string;
    description: string;
  }>;
}

export interface ArchitectureSpec {
  folder_structure: string;
  files: Array<{
    path: string;
    purpose: string;
  }>;
}

export interface FileTestResult {
  path: string;
  language: string;
  passed: boolean;
  stdout: string;
  stderr: string;
  exit_code: number;
  note?: string;
}

export interface TestResults {
  overall_passed: boolean;
  total_files: number;
  passed: number;
  failed: number;
  file_results: FileTestResult[];
  errors: Array<{ file_path: string; stderr: string; exit_code: number }>;
}

export interface ReviewFinding {
  severity: 'info' | 'warning' | 'critical';
  file: string;
  message: string;
}

export interface ReviewReport {
  overall_score: number;
  quality_score: number;
  security_score: number;
  completeness_score: number;
  best_practices_score: number;
  findings: ReviewFinding[];
  summary: string;
  approved: boolean;
}

export interface SystemStatus {
  status: string;
  service: string;
  version: string;
  ollama: {
    online: boolean;
    base_url: string;
    available_models: string[];
  };
}
