import type { CreateMapRequest } from "@/types";

// Stub: replaced by GridPainter in Task 7.
interface Props {
  onCancel: () => void;
  onSave: (body: CreateMapRequest) => Promise<void>;
}

export function MapEditor({ onCancel }: Props) {
  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">Editor legado removido.</p>
      <button onClick={onCancel}>Cancelar</button>
    </div>
  );
}
