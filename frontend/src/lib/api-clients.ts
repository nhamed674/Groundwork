import { env } from "./env";
import type { components } from "./api-types";

export type ChatRequest = components["schemas"]["ChatRequest"];
export type AgentResponse = components["schemas"]["AgentResponse"];

export async function chat(question: string) :  Promise<AgentResponse> {
    const body : ChatRequest = {question};
    const res = await fetch(`${env.NEXT_PUBLIC_API_URL}/chat`,{
        method: "POST",
        headers: {"content-type":"application/json", Accept:"application/json"},
        body:JSON.stringify(body)
    }
    );

    if(!res.ok) {
        const text = await res.text();
        throw new Error(`Chat failed (${res.status}): ${text}`);
    }
    return res.json() as Promise<AgentResponse>
}