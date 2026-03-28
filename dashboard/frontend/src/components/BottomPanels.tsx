import type { PipelineState, TeamRole, ChatMessage } from "../lib/types";
import TeamPanel from "./TeamPanel";
import AgentActivity from "./AgentActivity";

interface BottomPanelsProps {
  team: TeamRole[] | null;
  pipeline: PipelineState | null;
  messages: ChatMessage[];
}

export default function BottomPanels({ team, pipeline, messages }: BottomPanelsProps) {
  return (
    <div className="h-[200px] shrink-0 border-t border-[#1e1e30] flex">
      <div className="flex-1 p-3 border-r border-[#1e1e30] overflow-hidden">
        <TeamPanel
          team={team}
          messages={messages}
          activePhase={pipeline?.active ? pipeline.phase : null}
        />
      </div>
      <div className="flex-1 p-3 overflow-hidden">
        <AgentActivity pipeline={pipeline} messages={messages} />
      </div>
    </div>
  );
}
