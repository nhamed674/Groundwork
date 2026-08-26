import type { components } from "@/lib/api-types";
import { Separator } from "@/components/ui/separator";

type Citation = components["schemas"]["Citation"];

type CitationListProps = {
  citations: Citation[];
};

export function CitationList({ citations }: CitationListProps) {
  if (citations.length === 0) {
    return null;
  }

  return (
    <div className="mt-3 space-y-3">
      <p className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
        Sources
      </p>
      <ul className="space-y-3">
        {citations.map((citation, index) => (
          <li key={`${citation.source_path}-${index}`} className="space-y-1">
            {index > 0 ? <Separator className="mb-3" /> : null}
            <p className="text-sm font-medium">
              {citation.source}
              {citation.page_number != null ? (
                <span className="font-normal text-muted-foreground">
                  {" "}
                  · p. {citation.page_number}
                </span>
              ) : null}
            </p>
            <p className="text-sm leading-relaxed text-muted-foreground">
              {citation.snippet}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}