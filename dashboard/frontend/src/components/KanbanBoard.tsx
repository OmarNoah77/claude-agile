import { useState, useMemo } from "react";
import type { ProjectState, BacklogItem } from "../lib/types";
import TaskCard from "./TaskCard";
import TaskDetail from "./TaskDetail";
import SprintGroup from "./SprintGroup";

interface KanbanBoardProps {
  state: ProjectState | null;
}

interface SelectedTask {
  item: BacklogItem;
  column: string;
}

/** Extract sprint tag like [S1] from title */
function getSprintTag(title: string): string | null {
  const m = title.match(/\[(S\d+)\]/);
  return m ? m[1] : null;
}

/** Group items by sprint tag. Returns [grouped, ungrouped] */
function groupBySprint(
  items: BacklogItem[]
): { groups: Map<string, BacklogItem[]>; ungrouped: BacklogItem[] } {
  const groups = new Map<string, BacklogItem[]>();
  const ungrouped: BacklogItem[] = [];

  for (const item of items) {
    const tag = getSprintTag(item.title);
    if (tag) {
      const list = groups.get(tag) ?? [];
      list.push(item);
      groups.set(tag, list);
    } else {
      ungrouped.push(item);
    }
  }

  return { groups, ungrouped };
}

function ColumnContent({
  items,
  column,
  onTaskClick,
}: {
  items: BacklogItem[];
  column: "backlog" | "progress" | "done";
  onTaskClick: (item: BacklogItem) => void;
}) {
  const { groups, ungrouped } = useMemo(() => groupBySprint(items), [items]);

  return (
    <div className="space-y-1.5">
      {ungrouped.map((item, i) => (
        <TaskCard
          key={`ug-${i}`}
          item={item}
          column={column}
          onClick={() => onTaskClick(item)}
        />
      ))}
      {Array.from(groups.entries()).map(([tag, groupItems]) => (
        <SprintGroup
          key={tag}
          sprintTag={tag}
          items={groupItems}
          column={column}
          onTaskClick={onTaskClick}
        />
      ))}
    </div>
  );
}

export default function KanbanBoard({ state }: KanbanBoardProps) {
  const [selected, setSelected] = useState<SelectedTask | null>(null);

  const backlog = state?.backlog?.active ?? [];
  const inProgress = state?.sprint?.in_progress ?? [];
  const done = [
    ...(state?.sprint?.done ?? []),
    ...(state?.backlog?.completed ?? []),
  ];

  const columns: {
    key: "backlog" | "progress" | "done";
    label: string;
    items: BacklogItem[];
    color: string;
  }[] = [
    {
      key: "backlog",
      label: "Backlog",
      items: backlog,
      color: "#7a7a8c",
    },
    {
      key: "progress",
      label: "En Progreso",
      items: inProgress,
      color: "#3b82f6",
    },
    {
      key: "done",
      label: "Completado",
      items: done,
      color: "#22c55e",
    },
  ];

  return (
    <>
      <div className="grid grid-cols-3 gap-3 px-4 py-3 flex-1 min-h-0 overflow-hidden">
        {columns.map((col) => (
          <div
            key={col.key}
            className="flex flex-col min-h-0 rounded-lg bg-[#0c0c16] border border-[#1e1e30]"
          >
            {/* Column header */}
            <div className="flex items-center gap-2 px-3 py-2 border-b border-[#1e1e30]">
              <span
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: col.color }}
              />
              <span className="text-xs font-semibold text-[#e0e0e8]">
                {col.label}
              </span>
              <span className="text-[10px] text-[#7a7a8c] font-[JetBrains_Mono,monospace]">
                {col.items.length}
              </span>
            </div>
            {/* Scrollable cards */}
            <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
              <ColumnContent
                items={col.items}
                column={col.key}
                onTaskClick={(item) =>
                  setSelected({ item, column: col.label })
                }
              />
            </div>
          </div>
        ))}
      </div>

      {selected && (
        <TaskDetail
          item={selected.item}
          column={selected.column}
          onClose={() => setSelected(null)}
        />
      )}
    </>
  );
}
