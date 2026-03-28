interface HeaderProps {
  methodology: string;
  projectName: string;
}

export default function Header({ methodology, projectName }: HeaderProps) {
  return (
    <header className="flex items-center justify-between px-4 py-2 border-b border-[#1e1e30] bg-[#0a0a12]">
      <div className="flex items-center gap-3">
        <button className="px-2 py-1 text-xs rounded border border-[#1e1e30] text-[#7a7a8c] hover:text-[#e0e0e8] hover:border-[#6366f1] transition-colors">
          Hub
        </button>
        <span className="text-sm font-semibold tracking-wide text-[#e0e0e8]">
          CLAUDE-AGILE{" "}
          <span className="text-[#7a7a8c] font-normal">dashboard</span>
        </span>
        {methodology && (
          <span className="px-2 py-0.5 text-[10px] uppercase tracking-wider rounded bg-[#6366f1]/20 text-[#6366f1] font-medium font-[JetBrains_Mono,monospace]">
            {methodology}
          </span>
        )}
      </div>
      <div className="flex items-center gap-3">
        <span className="flex items-center gap-1.5 text-xs text-green-400">
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          Live
        </span>
        {projectName && (
          <span className="text-xs text-[#7a7a8c] font-[JetBrains_Mono,monospace]">
            {projectName}
          </span>
        )}
      </div>
    </header>
  );
}
