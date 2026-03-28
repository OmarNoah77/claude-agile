import { useState, useEffect } from "react";
import type { TeamRole, ChatMessage } from "../lib/types";

const DEFAULT_TEAM: TeamRole[] = [
  { name: "Scrum Master", color: "#a855f7", tag: "SM", status: "standby", team: "core" },
  { name: "Tech Lead", color: "#14b8a6", tag: "TL", status: "standby", team: "core" },
  { name: "Developer", color: "#3b82f6", tag: "DEV", status: "standby", team: "core" },
  { name: "QA", color: "#22c55e", tag: "QA", status: "standby", team: "core" },
  { name: "Cloud Architect", color: "#f97316", tag: "ARCH", status: "standby", team: "infra" },
  { name: "DevOps", color: "#eab308", tag: "DEVOPS", status: "standby", team: "infra" },
  { name: "DBA", color: "#a16207", tag: "DBA", status: "standby", team: "infra" },
  { name: "Observability", color: "#06b6d4", tag: "OBS", status: "standby", team: "infra" },
  { name: "Security", color: "#ef4444", tag: "SEC", status: "standby", team: "security" },
  { name: "Pen Tester", color: "#b91c1c", tag: "PENTEST", status: "standby", team: "security" },
  { name: "UX Designer", color: "#ec4899", tag: "UX", status: "standby", team: "product" },
  { name: "Data Engineer", color: "#6366f1", tag: "DATA", status: "standby", team: "product" },
];

interface TeamPanelProps {
  team: TeamRole[] | null;
  messages: ChatMessage[];
  activePhase: string | null;
}

interface RoleStats {
  messages: number;
  chars: number;
}

// Phase to role mapping
const PHASE_TO_ROLE: Record<string, string> = {
  intake: "SM", plan: "TL", exec: "DEV", verify: "QA", fix: "DEV",
};

export default function TeamPanel({ team, messages, activePhase }: TeamPanelProps) {
  const [stats, setStats] = useState<Record<string, RoleStats>>({});
  const roles = team && team.length > 0 ? team : DEFAULT_TEAM;

  // Compute stats from chat messages
  useEffect(() => {
    const s: Record<string, RoleStats> = {};
    for (const m of messages) {
      const role = m.role;
      if (!role) continue;
      if (!s[role]) s[role] = { messages: 0, chars: 0 };
      s[role].messages += 1;
      s[role].chars += (m.text || "").length;
    }
    setStats(s);
  }, [messages]);

  const activeRole = activePhase ? PHASE_TO_ROLE[activePhase] : null;

  return (
    <div className="flex-1 min-w-0 overflow-y-auto">
      <h3 className="text-[10px] uppercase tracking-wider text-[#7a7a8c] font-semibold mb-2 px-1">
        Equipo
      </h3>
      <div className="grid gap-1.5" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(130px, 1fr))" }}>
        {roles.map((role) => {
          const isActive = role.tag === activeRole;
          const roleStat = stats[role.tag];
          const hasActivity = !!roleStat;

          return (
            <div
              key={role.tag}
              className={`flex items-center gap-2 px-2.5 py-2 rounded-md border transition-all ${
                isActive
                  ? "bg-[#12121e] border-[#3b3b5c] opacity-100"
                  : hasActivity
                    ? "bg-[#0c0c16] border-[#1e1e30] opacity-80"
                    : "bg-[#0c0c16] border-[#1e1e30] opacity-35"
              }`}
            >
              <span
                className={`w-2.5 h-2.5 rounded-full shrink-0 ${isActive ? "animate-blink" : ""}`}
                style={{ backgroundColor: role.color }}
              />
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-1">
                  <span className="text-[10px] text-[#e0e0e8] truncate font-medium">
                    {role.name}
                  </span>
                  <span
                    className="text-[8px] font-[JetBrains_Mono,monospace] ml-auto shrink-0"
                    style={{ color: role.color }}
                  >
                    {role.tag}
                  </span>
                </div>
                {hasActivity ? (
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-[8px] font-[JetBrains_Mono,monospace] text-[#7a7a8c]">
                      {roleStat.messages} msgs
                    </span>
                    <span className="text-[8px] font-[JetBrains_Mono,monospace] text-[#7a7a8c]">
                      {roleStat.chars > 1000 ? `${(roleStat.chars / 1000).toFixed(1)}k` : roleStat.chars} chars
                    </span>
                  </div>
                ) : (
                  <div className="text-[8px] text-[#7a7a8c]/50 mt-0.5">standby</div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
