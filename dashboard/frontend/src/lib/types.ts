export interface BacklogItem {
  priority: string;
  title: string;
  sp: number;
  blocked?: boolean;
}

export interface SprintItem {
  priority: string;
  title: string;
  sp: number;
  blocked?: boolean;
}

export interface GitHubInfo {
  repo_url: string;
  current_branch: string;
  last_commit: {
    hash: string;
    message: string;
    time_ago: string;
  };
  open_prs: number;
  ci_status: string;
}

export interface SprintHealth {
  goal: string;
  days_remaining: number;
  sp_completed: number;
  sp_planned: number;
  progress: number;
  status: string;
}

export interface TeamRole {
  name: string;
  color: string;
  tag: string;
  status: string;
  team: string;
}

export interface WorkspaceModule {
  name: string;
  path: string;
  modules: string[];
}

export interface WorkspaceConfig {
  workspaces: WorkspaceModule[];
  active: string;
  active_module: string;
}

export interface ProjectState {
  backlog: {
    active: BacklogItem[];
    completed: BacklogItem[];
  };
  sprint: {
    goal: string;
    in_progress: SprintItem[];
    done: SprintItem[];
    wip_limit: number;
    sprint_start: string;
    sprint_end: string;
    total_sp_planned: number;
    total_sp_done: number;
  };
  github: GitHubInfo;
  sprint_health: SprintHealth;
  team: TeamRole[];
  summary: {
    backlog_count: number;
    in_progress_count: number;
    done_count: number;
    wip_limit: number;
  };
  methodology: string;
  project_name: string;
  workspaces: WorkspaceConfig;
}

export interface PipelinePhaseEntry {
  phase: string;
  timestamp: string;
  reason: string;
}

export interface PipelineState {
  active: boolean;
  module: string;
  phase: string;
  task_id: string;
  title: string;
  fix_attempts: number;
  status_line: string;
  phase_history: PipelinePhaseEntry[];
}

export interface ChatMessage {
  id: string;
  sender: string;
  role: string;
  text: string;
  module: string;
  timestamp: string;
  time: string;
}
