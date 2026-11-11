# System patterns

See `docs/architecture.md` for the full picture. In short:

- Apps own their models; rules are functions in `services/` or `reports.py`.
- `Transaction` → `rebuild_holding` (signals for single edits, one rebuild per
  asset after bulk imports) → `Holding`.
- Extension by settings: `PRICE_PROVIDERS`, `IMPORT_PARSERS`.
- Parsers are pure (rows in, `ParsedRow` out); the import service does all
  database work in one atomic block.
- Inconsistent ledgers are flagged on the holding, not raised.
