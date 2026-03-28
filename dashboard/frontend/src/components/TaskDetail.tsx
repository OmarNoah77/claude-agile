import type { BacklogItem } from "../lib/types";
import { sendChatMessage } from "../lib/api";

interface TaskDetailProps {
  item: BacklogItem;
  column: string;
  onClose: () => void;
}

const PRIORITY_COLORS: Record<string, string> = {
  P0: "bg-red-500",
  P1: "bg-orange-500",
  P2: "bg-yellow-500",
  P3: "bg-blue-500",
};

/** Extract sprint tag from title */
function extractSprint(title: string): string | null {
  const m = title.match(/\[(S\d+)\]/);
  return m ? m[1] : null;
}

function cleanTitle(title: string): string {
  return title.replace(/\[S\d+\]\s*/g, "").trim();
}

export default function TaskDetail({ item, column, onClose }: TaskDetailProps) {
  const prioColor = PRIORITY_COLORS[item.priority] ?? "bg-gray-500";
  const sprint = extractSprint(item.title);

  const handleSendToChat = async () => {
    try {
      await sendChatMessage(item.title);
    } catch {
      // ignore
    }
  };

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black/40 z-40"
        onClick={onClose}
      />
      {/* Drawer */}
      <div className="fixed top-0 right-0 bottom-0 w-[400px] bg-[#12121e] border-l border-[#1e1e30] z-50 flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[#1e1e30]">
          <span className="text-sm font-semibold text-[#e0e0e8]">
            Detalle de tarea
          </span>
          <button
            onClick={onClose}
            className="text-[#7a7a8c] hover:text-[#e0e0e8] text-lg leading-none"
          >
            &times;
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <h2 className="text-base font-semibold text-[#e0e0e8] leading-snug">
            {cleanTitle(item.title)}
          </h2>

          <div className="flex flex-wrap gap-2">
            <span
              className={`text-xs px-2 py-0.5 rounded font-semibold text-white ${prioColor}`}
            >
              {item.priority}
            </span>
            {item.sp > 0 && (
              <span className="text-xs px-2 py-0.5 rounded bg-[#1e1e30] text-[#7a7a8c] font-[JetBrains_Mono,monospace]">
                {item.sp} SP
              </span>
            )}
            {sprint && (
              <span className="text-xs px-2 py-0.5 rounded bg-[#6366f1]/20 text-[#6366f1] font-[JetBrains_Mono,monospace]">
                {sprint}
              </span>
            )}
            <span className="text-xs px-2 py-0.5 rounded bg-[#1e1e30] text-[#7a7a8c] capitalize">
              {column}
            </span>
            {item.blocked && (
              <span className="text-xs px-2 py-0.5 rounded bg-red-500/20 text-red-400 font-semibold">
                BLOQUEADO
              </span>
            )}
          </div>

          <div className="text-xs text-[#7a7a8c] leading-relaxed whitespace-pre-wrap">
            {item.title}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[#1e1e30]">
          <button
            onClick={handleSendToChat}
            className="w-full py-2 text-xs font-medium rounded bg-[#6366f1] text-white hover:bg-[#6366f1]/80 transition-colors"
          >
            Enviar al chat
          </button>
        </div>
      </div>
    </>
  );
}
