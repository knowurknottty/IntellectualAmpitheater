type ProviderWarningsProps = {
  warnings: string[];
  hardIncompatibilities: string[];
  acknowledged: boolean;
  onAcknowledgedChange: (value: boolean) => void;
};

export function ProviderWarnings({ warnings, hardIncompatibilities, acknowledged, onAcknowledgedChange }: ProviderWarningsProps) {
  if (warnings.length === 0 && hardIncompatibilities.length === 0) return null;
  return (
    <section className="provider-warnings" aria-label="Capability status">
      {hardIncompatibilities.length > 0 && (
        <div className="provider-warnings__hard">
          <strong>Dispatch blocked</strong>
          <ul>{hardIncompatibilities.map((issue) => <li key={issue}>{issue}</li>)}</ul>
        </div>
      )}
      {warnings.length > 0 && (
        <div className="provider-warnings__optional">
          <strong>Capability loss</strong>
          <ul>{warnings.map((issue) => <li key={issue}>{issue}</li>)}</ul>
          <label>
            <input type="checkbox" checked={acknowledged} onChange={(event) => onAcknowledgedChange(event.target.checked)} />
            Acknowledge capability loss
          </label>
        </div>
      )}
    </section>
  );
}
