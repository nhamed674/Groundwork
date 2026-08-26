import { ChatPanel } from "@/features/chat/ChatPanel";

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col p-6">
      <h1 className="mb-2 text-2xl font-semibold tracking-tight">Groundwork</h1>
      <p className="mb-6 text-sm text-muted-foreground">
        Document Q&amp;A with citations
      </p>
      <ChatPanel />
    </main>
  );
}