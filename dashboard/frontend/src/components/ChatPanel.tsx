import { useState, useRef, useEffect } from "react";
import type { ChatMessage } from "../lib/types";
import { sendChatMessage } from "../lib/api";

interface ChatPanelProps {
  messages: ChatMessage[];
  activeModule: string;
}

const ROLE_META: Record<string, { color: string; name: string; emoji: string }> = {
  SM:      { color: "#a855f7", name: "Scrum Master",     emoji: "SM" },
  TL:      { color: "#14b8a6", name: "Tech Lead",        emoji: "TL" },
  DEV:     { color: "#3b82f6", name: "Developer",        emoji: "DV" },
  QA:      { color: "#22c55e", name: "QA Engineer",      emoji: "QA" },
  ARCH:    { color: "#f97316", name: "Cloud Architect",   emoji: "AR" },
  DEVOPS:  { color: "#eab308", name: "DevOps",           emoji: "DO" },
  DBA:     { color: "#a16207", name: "DBA",              emoji: "DB" },
  OBS:     { color: "#06b6d4", name: "Observability",    emoji: "OB" },
  SEC:     { color: "#ef4444", name: "Security",         emoji: "SE" },
  PENTEST: { color: "#b91c1c", name: "Pen Tester",       emoji: "PT" },
  UX:      { color: "#ec4899", name: "UX Designer",      emoji: "UX" },
  DATA:    { color: "#6366f1", name: "Data Engineer",     emoji: "DA" },
};

function formatText(text: string): (string | React.ReactNode)[] {
  const parts: (string | React.ReactNode)[] = [];
  const regex = /(\*\*(.+?)\*\*|`([^`]+)`|\[PIPELINE:[^\]]+\])/g;
  let last = 0;
  let match: RegExpExecArray | null;
  while ((match = regex.exec(text)) !== null) {
    if (match.index > last) parts.push(text.slice(last, match.index));
    if (match[2]) {
      parts.push(<strong key={match.index} className="font-semibold text-white">{match[2]}</strong>);
    } else if (match[3]) {
      parts.push(
        <code key={match.index} className="px-1 py-0.5 rounded bg-[#1e1e30] text-[#6366f1] font-[JetBrains_Mono,monospace] text-[10px]">{match[3]}</code>
      );
    } else if (match[0].startsWith("[PIPELINE:")) {
      parts.push(
        <span key={match.index} className="inline-block px-1.5 py-0.5 rounded bg-[#6366f1]/20 text-[#6366f1] font-[JetBrains_Mono,monospace] text-[9px] font-bold">{match[0]}</span>
      );
    }
    last = match.index + match[0].length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}

export default function ChatPanel({ messages, activeModule }: ChatPanelProps) {
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const prevCountRef = useRef(0);

  useEffect(() => {
    if (messages.length > prevCountRef.current) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
    prevCountRef.current = messages.length;
  }, [messages.length]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || sending) return;
    setSending(true);
    setInput("");
    try { await sendChatMessage(text); } catch {} finally { setSending(false); }
  };

  return (
    <div className="w-[340px] shrink-0 border-l border-[#1e1e30] bg-[#0c0c16] flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-2.5 border-b border-[#1e1e30] flex items-center justify-between">
        <div>
          <div className="text-xs font-semibold text-[#e0e0e8]">Team Chat</div>
          <div className="text-[10px] text-[#7a7a8c] font-[JetBrains_Mono,monospace]">
            #{activeModule || "general"}
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-2 space-y-0.5">
        {messages.map((msg) => {
          const isUser = msg.sender === "user";
          const isSystemOnly = msg.sender === "system" && !msg.role;
          const roleMeta = msg.role ? ROLE_META[msg.role] : null;

          // System messages (no role) — compact gray
          if (isSystemOnly) {
            return (
              <div key={msg.id} className="px-3 py-1">
                <span className="text-[10px] text-[#7a7a8c]/60 italic">{msg.text}</span>
              </div>
            );
          }

          // User (Product Owner) message
          if (isUser) {
            return (
              <div key={msg.id} className="flex gap-2 px-2 py-2 rounded-md bg-[#e0e0e8]/[0.03]">
                <div className="w-7 h-7 rounded-md shrink-0 flex items-center justify-center text-[9px] font-bold bg-[#e0e0e8] text-[#0a0a12]">
                  PO
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-[11px] font-bold text-[#e0e0e8]">Product Owner</span>
                    <span className="text-[9px] text-[#7a7a8c]">{msg.time}</span>
                  </div>
                  <div className="text-[11px] text-[#e0e0e8] leading-relaxed whitespace-pre-wrap break-words">
                    {formatText(msg.text)}
                  </div>
                </div>
              </div>
            );
          }

          // Role message (SM, TL, DEV, QA, etc.)
          if (roleMeta) {
            const c = roleMeta.color;
            return (
              <div
                key={msg.id}
                className="flex gap-2 px-2 py-2 rounded-md border-l-[3px]"
                style={{ borderLeftColor: c, backgroundColor: `${c}08` }}
              >
                <div
                  className="w-7 h-7 rounded-md shrink-0 flex items-center justify-center text-[9px] font-bold text-white"
                  style={{ backgroundColor: c }}
                >
                  {roleMeta.emoji}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-[11px] font-bold" style={{ color: c }}>
                      {roleMeta.name}
                    </span>
                    <span
                      className="text-[8px] px-1.5 py-0.5 rounded font-[JetBrains_Mono,monospace] font-bold"
                      style={{ color: c, backgroundColor: `${c}20`, border: `1px solid ${c}30` }}
                    >
                      {msg.role}
                    </span>
                    <span className="text-[9px] text-[#7a7a8c]">{msg.time}</span>
                  </div>
                  <div className="text-[11px] text-[#e0e0e8]/80 leading-relaxed whitespace-pre-wrap break-words">
                    {formatText(msg.text)}
                  </div>
                </div>
              </div>
            );
          }

          // Generic assistant message
          return (
            <div key={msg.id} className="flex gap-2 px-2 py-2 rounded-md bg-[#6366f1]/[0.04]">
              <div className="w-7 h-7 rounded-md shrink-0 flex items-center justify-center text-[9px] font-bold bg-[#6366f1] text-white">
                AI
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="text-[11px] font-bold text-[#6366f1]">Assistant</span>
                  <span className="text-[9px] text-[#7a7a8c]">{msg.time}</span>
                </div>
                <div className="text-[11px] text-[#e0e0e8]/80 leading-relaxed whitespace-pre-wrap break-words">
                  {formatText(msg.text)}
                </div>
              </div>
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-3 border-t border-[#1e1e30]">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }}}
            placeholder="Escribe un mensaje..."
            rows={2}
            className="flex-1 px-3 py-2 text-xs bg-[#12121e] border border-[#1e1e30] rounded-lg text-[#e0e0e8] placeholder-[#7a7a8c] outline-none focus:border-[#6366f1] resize-none"
          />
          <button
            onClick={handleSend}
            disabled={sending || !input.trim()}
            className="px-3 py-2 text-xs font-medium rounded-lg bg-[#6366f1] text-white hover:bg-[#6366f1]/80 disabled:opacity-40 transition-colors self-end"
          >
            Enviar
          </button>
        </div>
      </div>
    </div>
  );
}
