import { useCallback } from "react";
import { usePolling } from "./hooks/usePolling";
import {
  fetchState,
  fetchPipeline,
  fetchChatHistory,
} from "./lib/api";
import type { ProjectState, PipelineState, ChatMessage } from "./lib/types";
import Header from "./components/Header";
import ModuleTabs from "./components/ModuleTabs";
import PipelineBar from "./components/PipelineBar";
import InfoBar from "./components/InfoBar";
import KanbanBoard from "./components/KanbanBoard";
import BottomPanels from "./components/BottomPanels";
import ChatPanel from "./components/ChatPanel";

function App() {
  const {
    data: state,
    refetch: refetchState,
  } = usePolling<ProjectState>(fetchState, 3000);

  const { data: pipeline } = usePolling<PipelineState>(fetchPipeline, 3000);

  const chatFetcher = useCallback(() => fetchChatHistory(40), []);
  const { data: chatData } = usePolling<{ messages: ChatMessage[] }>(
    chatFetcher,
    2000
  );

  const messages = chatData?.messages ?? [];
  const activeModule = state?.workspaces?.active_module ?? "";

  return (
    <div className="h-screen flex flex-col bg-[#0a0a12] text-[#e0e0e8] overflow-hidden">
      {/* Module Tabs */}
      <ModuleTabs
        workspaces={state?.workspaces ?? null}
        onModuleChange={refetchState}
      />

      {/* Header */}
      <Header
        methodology={state?.methodology ?? ""}
        projectName={state?.project_name ?? ""}
      />

      {/* Main content area */}
      <div className="flex-1 flex min-h-0 overflow-hidden">
        {/* Left: main content */}
        <div className="flex-1 flex flex-col min-h-0 overflow-hidden border-r border-[#1e1e30]">
          {/* Pipeline bar */}
          <PipelineBar pipeline={pipeline ?? null} />

          {/* Info bar */}
          <InfoBar
            github={state?.github ?? null}
            sprintHealth={state?.sprint_health ?? null}
            backlogCount={state?.summary?.backlog_count ?? 0}
            inProgressCount={state?.summary?.in_progress_count ?? 0}
            wipLimit={state?.summary?.wip_limit ?? 2}
            doneCount={state?.summary?.done_count ?? 0}
          />

          {/* Kanban board (scrollable) */}
          <KanbanBoard state={state ?? null} />

          {/* Bottom panels (fixed at bottom) */}
          <BottomPanels
            team={state?.team ?? null}
            pipeline={pipeline ?? null}
            messages={messages}
          />
        </div>

        {/* Right: chat panel */}
        <ChatPanel messages={messages} activeModule={activeModule} />
      </div>
    </div>
  );
}

export default App;
