import type { GitHubInfo, SprintHealth } from "../lib/types";

interface InfoBarProps {
  github: GitHubInfo | null;
  sprintHealth: SprintHealth | null;
  backlogCount: number;
  inProgressCount: number;
  wipLimit: number;
  doneCount: number;
}

export default function InfoBar({
  github,
  sprintHealth,
  backlogCount,
  inProgressCount,
  wipLimit,
  doneCount,
}: InfoBarProps) {
  const progress = sprintHealth?.progress ?? 0;
  const progressColor =
    (sprintHealth?.status === "behind") ? "bg-red-500" :
    (sprintHealth?.status === "at_risk") ? "bg-yellow-500" : "bg-green-500";

  return (
    <div className="flex flex-col border-b border-[#1e1e30]">
      {/* GitHub Bar */}
      {github && (
        <div className="flex items-center gap-3 px-5 py-1.5 text-[11px] border-b border-[#1e1e30]/50">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor" className="text-[#7a7a8c] shrink-0">
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
          </svg>
          {github.repo_url && (
            <a href={github.repo_url} target="_blank" rel="noreferrer"
              className="font-[JetBrains_Mono,monospace] text-[#6366f1] hover:underline text-[11px]">
              {github.repo_url.replace("https://github.com/", "")}
            </a>
          )}
          <div className="w-px h-4 bg-[#1e1e30]" />
          <div className="flex items-center gap-1 text-[#7a7a8c]">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M6 3v12M18 9a3 3 0 100-6 3 3 0 000 6zM6 21a3 3 0 100-6 3 3 0 000 6zM18 9a9 9 0 01-9 9"/>
            </svg>
            <span className="text-[#e0e0e8] font-[JetBrains_Mono,monospace]">{github.current_branch}</span>
          </div>
          <div className="w-px h-4 bg-[#1e1e30]" />
          {github.last_commit && (
            <div className="flex items-center gap-1.5">
              <span className="font-[JetBrains_Mono,monospace] text-[#eab308]">{github.last_commit.hash?.slice(0, 7)}</span>
              <span className="text-[#e0e0e8] max-w-[200px] truncate">{github.last_commit.message}</span>
              <span className="text-[#7a7a8c]">{github.last_commit.time_ago}</span>
            </div>
          )}
          <div className="w-px h-4 bg-[#1e1e30]" />
          <span className="text-[#7a7a8c]">PRs: <span className="text-[#3b82f6] font-[JetBrains_Mono,monospace]">{github.open_prs ?? 0}</span></span>
          <span className="flex items-center gap-1 text-[#7a7a8c]">
            CI:
            <span className={
              github.ci_status === "success" ? "text-green-400" :
              github.ci_status === "failure" ? "text-red-400" : "text-yellow-400"
            }>
              {github.ci_status === "success" ? "✅" : github.ci_status === "failure" ? "❌" : github.ci_status === "running" ? "⏳" : "--"}
            </span>
          </span>
        </div>
      )}

      {/* Sprint Health Bar */}
      <div className="flex items-center gap-3 px-5 py-1.5 text-[11px]">
        <span className="text-[10px] uppercase tracking-wider text-[#7a7a8c] shrink-0">Meta:</span>
        <span className="text-[12px] font-semibold text-[#e0e0e8] truncate flex-1">
          {sprintHealth?.goal || "Sin meta definida"}
        </span>

        <div className="flex items-center gap-3">
          <Metric label="Dias rest." value={sprintHealth?.days_remaining ?? "--"} />
          <div className="w-px h-5 bg-[#1e1e30]" />
          <Metric label="Backlog" value={backlogCount} />
          <div className="w-px h-5 bg-[#1e1e30]" />
          <Metric label="WIP" value={`${inProgressCount}/${wipLimit}`} />
          <div className="w-px h-5 bg-[#1e1e30]" />
          <Metric label="Done" value={doneCount} />
          <div className="w-px h-5 bg-[#1e1e30]" />
          <Metric label="SP" value={`${sprintHealth?.sp_completed ?? 0}/${sprintHealth?.sp_planned ?? 0}`} />
        </div>

        <div className="flex items-center gap-1.5 ml-2">
          <div className="w-28 h-[5px] rounded-full bg-[#1e1e30]/80 overflow-hidden">
            <div
              className={`h-full rounded-full ${progressColor} transition-all duration-500`}
              style={{ width: `${Math.min(100, progress)}%` }}
            />
          </div>
          <span className="font-[JetBrains_Mono,monospace] text-[10px] text-[#7a7a8c] w-8 text-right">
            {Math.round(progress)}%
          </span>
        </div>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex flex-col items-center gap-px">
      <span className="font-[JetBrains_Mono,monospace] text-[14px] font-bold text-white">{value}</span>
      <span className="text-[9px] uppercase tracking-wider text-[#7a7a8c]">{label}</span>
    </div>
  );
}
