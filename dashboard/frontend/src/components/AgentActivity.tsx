import type { PipelineState, ChatMessage } from "../lib/types";

const PHASE_COLORS: Record<string, string> = {
  intake: "#a855f7",
  plan: "#14b8a6",
  exec: "#3b82f6",
  verify: "#22c55e",
  fix: "#f97316",
};

interface AgentActivityProps {
  pipeline: PipelineState | null;
  messages: ChatMessage[];
}

export default function AgentActivity({ pipeline, messages }: AgentActivityProps) {
  // Last 4 system/assistant messages
  const activityLog = messages
    .filter((m) => m.role === "system" || m.role === "assistant")
    .slice(-4);

  return (
    <div className="flex-1 min-w-0 overflow-y-auto">
      <h3 className="text-[10px] uppercase tracking-wider text-[#7a7a8c] font-semibold mb-2 px-1">
        Actividad del agente
      </h3>
      {pipeline?.active ? (
        <div className="space-y-2">
          <div className="flex items-center gap-2 px-2 py-1.5 rounded bg-[#0c0c16] border border-[#1e1e30]">
            <span
              className="w-2.5 h-2.5 rounded-full animate-blink shrink-0"
              style={{
                backgroundColor: PHASE_COLORS[pipeline.phase] ?? "#6366f1",
              }}
            />
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span
                  className="text-xs font-semibold font-[JetBrains_Mono,monospace]"
                  style={{
                    color: PHASE_COLORS[pipeline.phase] ?? "#6366f1",
                  }}
                >
                  {pipeline.phase.toUpperCase()}
                </span>
                {pipeline.module && (
                  <span className="text-[10px] px-1 py-0.5 rounded bg-[#1e1e30] text-[#7a7a8c]">
                    {pipeline.module}
                  </span>
                )}
              </div>
              <p className="text-[10px] text-[#e0e0e8] truncate">
                {pipeline.title}
              </p>
            </div>
          </div>

          {/* Log */}
          <div className="space-y-1">
            {activityLog.map((msg) => (
              <div
                key={msg.id}
                className="px-2 py-1 text-[10px] text-[#7a7a8c] truncate"
              >
                <span className="text-[#e0e0e8]">{msg.sender}</span>{" "}
                {msg.text.slice(0, 80)}
                {msg.text.length > 80 ? "..." : ""}
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-center h-16 text-xs text-[#7a7a8c]">
          Sin agente activo
        </div>
      )}
    </div>
  );
}
