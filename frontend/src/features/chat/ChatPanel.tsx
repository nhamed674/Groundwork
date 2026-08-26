"use client";

import { useState } from "react";
import { chat, type AgentResponse } from "@/lib/api-clients";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { CitationList } from "@/features/chat/CitationList";
import { RouteBadge } from "@/features/chat/RouteBadge";

type UiMessage =
  | { id: string; role: "user"; content: string }
  | {
      id: string;
      role: "assistant";
      content: string;
      citations: NonNullable<AgentResponse["citations"]>;
      citation_warning: AgentResponse["citation_warning"];
      route_taken: AgentResponse["route_taken"];
    };

function newId() {
  return crypto.randomUUID();
}

export function ChatPanel() {
  const [messages, setMessages] = useState<UiMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const question = input.trim();
    if (!question || loading) return;

    setError(null);
    setInput("");
    setMessages((prev) => [
      ...prev,
      { id: newId(), role: "user", content: question },
    ]);
    setLoading(true);

    try {
      const response = await chat(question);
      setMessages((prev) => [
        ...prev,
        {
          id: newId(),
          role: "assistant",
          content: response.answer,
          citations: response.citations ?? [],
          citation_warning: response.citation_warning,
          route_taken: response.route_taken,
        },
      ]);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Something went wrong";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-[70vh] flex-col gap-4">
      <ScrollArea className="flex-1 rounded-md border p-4">
        <div className="space-y-6 pr-3">
          {messages.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Ask a question about your documents.
            </p>
          ) : null}

          {messages.map((message) => (
            <div key={message.id} className="space-y-2">
              <p className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
                {message.role === "user" ? "You" : "Groundwork"}
              </p>
              <p className="whitespace-pre-wrap text-sm leading-relaxed">
                {message.content}
              </p>

              {message.role === "assistant" ? (
                <>
                  <RouteBadge routeTaken={message.route_taken} />
                  {message.citation_warning ? (
                    <Alert variant="destructive" className="mt-2">
                      <AlertTitle>Citation warning</AlertTitle>
                      <AlertDescription>
                        {message.citation_warning}
                      </AlertDescription>
                    </Alert>
                  ) : null}
                  <CitationList citations={message.citations} />
                </>
              ) : null}
            </div>
          ))}

          {loading ? (
            <p className="text-sm text-muted-foreground">Thinking…</p>
          ) : null}
        </div>
      </ScrollArea>

      {error ? (
        <Alert variant="destructive">
          <AlertTitle>Request failed</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : null}

      <form onSubmit={onSubmit} className="flex flex-col gap-2">
        <Textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask about your documents…"
          disabled={loading}
          rows={3}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              event.currentTarget.form?.requestSubmit();
            }
          }}
        />
        <Button type="submit" disabled={loading || !input.trim()}>
          {loading ? "Sending…" : "Send"}
        </Button>
      </form>
    </div>
  );
}