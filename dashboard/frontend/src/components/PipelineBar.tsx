import type { PipelineState } from "../lib/types";

const PHASE_COLORS: Record<string, string> = {
  intake: "#a855f7",
  plan: "#14b8a6",
  exec: "#3b82f6",
  verify: "#22c55e",
  fix: "#f97316",
};

interface PipelineBarProps {
  pipeline: PipelineState | null;
}

export default function PipelineBar({ pipeline }: PipelineBarProps) {
  if (!pipeline?.active) return null;

  const color = PHASE_COLORS[pipeline.phase] ?? "#6366f1";

  return (
    <div
      className="flex items-center gap-3 px-4 py-2 border-b border-[#1e1e30]"
      style={{ background: `${color}10` }}
    >
      <span
        className="w-2.5 h-2.5 rounded-full animate-blink shrink-0"
        style={{ backgroundColor: color }}
      />
      <span
        className="text-xs font-semibold uppercase tracking-wider font-[JetBrains_Mono,monospace]"
        style={{ color }}
      >
        {pipeline.phase}
      </span>
      <span className="text-xs text-[#e0e0e8] truncate">
        {pipeline.title}
      </span>
      <span className="text-[10px] text-[#7a7a8c] font-[JetBrains_Mono,monospace]">
        {pipeline.task_id}
      </span>
      {pipeline.module && (
        <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#1e1e30] text-[#7a7a8c]">
          {pipeline.module}
        </span>
      )}
      {pipeline.fix_attempts > 0 && (
        <span className="text-[10px] text-[#f97316]">
          fix #{pipeline.fix_attempts}
        </span>
      )}
    </div>
  );
}
