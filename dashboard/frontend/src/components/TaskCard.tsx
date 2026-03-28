import type { BacklogItem } from "../lib/types";

const PRIORITY_COLORS: Record<string, string> = {
  P0: "bg-red-500",
  P1: "bg-orange-500",
  P2: "bg-yellow-500",
  P3: "bg-blue-500",
};

interface TaskCardProps {
  item: BacklogItem;
  column: "backlog" | "progress" | "done";
  onClick: () => void;
}

/** Strip [S1], [S2] etc. tags from title for display */
function cleanTitle(title: string): string {
  return title.replace(/\[S\d+\]\s*/g, "").trim();
}

export default function TaskCard({ item, column, onClick }: TaskCardProps) {
  const prioColor = PRIORITY_COLORS[item.priority] ?? "bg-gray-500";

  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-3 rounded-lg bg-[#12121e] border border-[#1e1e30] hover:border-[#6366f1]/40 transition-colors cursor-pointer ${
        item.blocked ? "border-l-2 border-l-red-500" : ""
      }`}
    >
      <div className="flex items-start gap-2">
        {column === "progress" && (
          <span className="w-2 h-2 rounded-full bg-blue-500 animate-blink mt-1.5 shrink-0" />
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span
              className={`text-[10px] px-1.5 py-0.5 rounded font-semibold text-white ${prioColor}`}
            >
              {item.priority}
            </span>
            {item.sp > 0 && (
              <span className="text-[10px] text-[#7a7a8c] font-[JetBrains_Mono,monospace]">
                {item.sp} SP
              </span>
            )}
            {item.blocked && (
              <span className="text-[10px] text-red-400 font-semibold">
                BLOQUEADO
              </span>
            )}
          </div>
          <p className="text-xs text-[#e0e0e8] leading-relaxed truncate">
            {cleanTitle(item.title)}
          </p>
        </div>
      </div>
    </button>
  );
}
