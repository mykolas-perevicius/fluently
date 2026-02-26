import { useState, useCallback } from "react";
import { detectPII, redactPII } from "../services/api";
import type { PIIEntity, RedactionStrategy } from "../types";

export interface PIIDetectionState {
  isEnabled: boolean;
  setIsEnabled: (v: boolean) => void;
  isDetecting: boolean;
  entities: PIIEntity[];
  selectedEntities: PIIEntity[];
  toggleEntity: (index: number) => void;
  selectAll: () => void;
  deselectAll: () => void;
  strategy: RedactionStrategy;
  setStrategy: (s: RedactionStrategy) => void;
  redactedText: string | null;
  detect: (text: string) => Promise<void>;
  redact: (text: string) => Promise<string>;
  reset: () => void;
}

export function usePIIDetection(): PIIDetectionState {
  const [isEnabled, setIsEnabled] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [entities, setEntities] = useState<PIIEntity[]>([]);
  const [selectedIndices, setSelectedIndices] = useState<Set<number>>(new Set());
  const [strategy, setStrategy] = useState<RedactionStrategy>("mask");
  const [redactedText, setRedactedText] = useState<string | null>(null);

  const selectedEntities = entities.filter((_, i) => selectedIndices.has(i));

  const toggleEntity = useCallback(
    (index: number) => {
      setSelectedIndices((prev) => {
        const next = new Set(prev);
        if (next.has(index)) {
          next.delete(index);
        } else {
          next.add(index);
        }
        return next;
      });
    },
    [],
  );

  const selectAll = useCallback(() => {
    setSelectedIndices(new Set(entities.map((_, i) => i)));
  }, [entities]);

  const deselectAll = useCallback(() => {
    setSelectedIndices(new Set());
  }, []);

  const detect = useCallback(async (text: string) => {
    setIsDetecting(true);
    setEntities([]);
    setSelectedIndices(new Set());
    setRedactedText(null);
    try {
      const result = await detectPII(text);
      setEntities(result.entities as PIIEntity[]);
      // Auto-select all entities by default
      setSelectedIndices(new Set(result.entities.map((_, i) => i)));
    } catch {
      // Detection is best-effort; don't block the workflow
      setEntities([]);
    } finally {
      setIsDetecting(false);
    }
  }, []);

  const redact = useCallback(
    async (text: string): Promise<string> => {
      if (selectedEntities.length === 0) return text;

      const result = await redactPII(text, selectedEntities, strategy);
      setRedactedText(result.redacted_text);
      return result.redacted_text;
    },
    [selectedEntities, strategy],
  );

  const reset = useCallback(() => {
    setEntities([]);
    setSelectedIndices(new Set());
    setRedactedText(null);
    setIsDetecting(false);
  }, []);

  return {
    isEnabled,
    setIsEnabled,
    isDetecting,
    entities,
    selectedEntities,
    toggleEntity,
    selectAll,
    deselectAll,
    strategy,
    setStrategy,
    redactedText,
    detect,
    redact,
    reset,
  };
}
