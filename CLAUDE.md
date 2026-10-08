# train-delay-analyze

## Agent skills

### Issue tracker

Issues live in GitHub Issues (smuda/train-delay-analyze) via the
`gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`,
`ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` and `docs/adr/` at the repo root.
See `docs/agents/domain.md`.

## Folder structure

- `data/trains.csv`: the service's train numbers, one row per
  number with its valid date range
  (`train_number,valid_from,valid_to`). Edited by hand.
- `data/raw/YYYY-MM-DD.json`: the raw archive, one file per trip
  date, holding the API response unmodified. Written by `fetch`,
  never edited.
