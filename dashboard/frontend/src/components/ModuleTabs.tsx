import { useState, useEffect } from "react";
import type { WorkspaceConfig } from "../lib/types";
import { switchModule, createModule } from "../lib/api";

interface ModuleTabsProps {
  workspaces: WorkspaceConfig | null;
  onModuleChange?: () => void;
}

export default function ModuleTabs({ workspaces, onModuleChange }: ModuleTabsProps) {
  const [adding, setAdding] = useState(false);
  const [newName, setNewName] = useState("");
  const [localActive, setLocalActive] = useState("");

  // Sync from server
  useEffect(() => {
    if (workspaces?.active_module !== undefined) {
      setLocalActive(workspaces.active_module);
    }
  }, [workspaces?.active_module]);

  const allModules: string[] = [];
  if (workspaces?.workspaces) {
    for (const ws of workspaces.workspaces) {
      for (const m of ws.modules) {
        if (!allModules.includes(m)) allModules.push(m);
      }
    }
  }

  const handleSwitch = async (mod: string) => {
    setLocalActive(mod); // Immediate visual feedback
    try {
      await switchModule(mod);
      onModuleChange?.();
    } catch {
      // revert
    }
  };

  const handleAdd = async () => {
    if (!newName.trim()) return;
    const ws = workspaces?.workspaces?.[0];
    if (!ws) return;
    try {
      await createModule(ws.name, newName.trim());
      setNewName("");
      setAdding(false);
      onModuleChange?.();
    } catch {
      // ignore
    }
  };

  return (
    <div className="flex items-center gap-0 px-3 border-b-2 border-[#1e1e30] bg-[#06060c] overflow-x-auto shrink-0">
      <Tab label="# todo" active={localActive === ""} onClick={() => handleSwitch("")} />
      {allModules.map((m) => (
        <Tab key={m} label={m} active={localActive === m} onClick={() => handleSwitch(m)} />
      ))}
      {adding ? (
        <div className="flex items-center gap-1 ml-2">
          <input
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleAdd();
              if (e.key === "Escape") setAdding(false);
            }}
            className="px-2 py-0.5 text-xs bg-[#12121e] border border-[#1e1e30] rounded text-[#e0e0e8] outline-none focus:border-[#6366f1] w-24"
            placeholder="nombre..."
            autoFocus
          />
        </div>
      ) : (
        <button
          onClick={() => setAdding(true)}
          className="ml-2 px-2 py-1 text-xs text-[#7a7a8c] border border-[#1e1e30] rounded hover:text-[#6366f1] hover:border-[#6366f1] transition-colors"
        >
          +
        </button>
      )}
    </div>
  );
}

function Tab({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      style={active ? { borderBottomColor: "#6366f1", color: "#6366f1", background: "rgba(99,102,241,0.12)" } : {}}
      className={`px-4 py-2.5 text-[11px] font-[JetBrains_Mono,monospace] whitespace-nowrap transition-all border-b-2 ${
        active
          ? "border-[#6366f1]"
          : "border-transparent text-[#7a7a8c] hover:text-[#e0e0e8]"
      }`}
    >
      {label}
    </button>
  );
}
