import { useState, useEffect } from "react";
import type { BacklogItem } from "../lib/types";
import TaskCard from "./TaskCard";

interface SprintGroupProps {
  sprintTag: string;
  items: BacklogItem[];
  column: "backlog" | "progress" | "done";
  onTaskClick: (item: BacklogItem) => void;
}

function getStorageKey(tag: string): string {
  return `sprint-collapse-${tag}`;
}

export default function SprintGroup({
  sprintTag,
  items,
  column,
  onTaskClick,
}: SprintGroupProps) {
  const [collapsed, setCollapsed] = useState(() => {
    try {
      return localStorage.getItem(getStorageKey(sprintTag)) === "true";
    } catch {
      return false;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(getStorageKey(sprintTag), String(collapsed));
    } catch {
      // ignore
    }
  }, [collapsed, sprintTag]);

  const totalSp = items.reduce((s, i) => s + (i.sp || 0), 0);

  return (
    <div className="space-y-1.5">
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center gap-2 w-full text-left px-2 py-1 rounded hover:bg-[#1e1e30]/50 transition-colors"
      >
        <span
          className="text-[10px] text-[#7a7a8c] transition-transform"
          style={{ transform: collapsed ? "rotate(-90deg)" : "rotate(0deg)" }}
        >
          ▼
        </span>
        <span className="text-xs font-semibold text-[#6366f1] font-[JetBrains_Mono,monospace]">
          {sprintTag}
        </span>
        <span className="text-[10px] text-[#7a7a8c]">
          {items.length} tareas
        </span>
        {totalSp > 0 && (
          <span className="text-[10px] text-[#7a7a8c] font-[JetBrains_Mono,monospace]">
            {totalSp} SP
          </span>
        )}
      </button>
      {!collapsed && (
        <div className="space-y-1.5 pl-1">
          {items.map((item, idx) => (
            <TaskCard
              key={`${sprintTag}-${idx}`}
              item={item}
              column={column}
              onClick={() => onTaskClick(item)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
