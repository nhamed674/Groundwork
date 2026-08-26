import { Badge } from "@/components/ui/badge";

type RouteBadgeProps = {
  routeTaken?: string | null;
};

export function RouteBadge({ routeTaken }: RouteBadgeProps) {
  return (
    <Badge variant="secondary" className="font-mono text-xs">
      route: {routeTaken ?? "—"}
    </Badge>
  );
}