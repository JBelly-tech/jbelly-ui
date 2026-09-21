# Recorded runs

One file per run, written by `evals/run.py` from what the agent CLI reported. These are the
numbers `COST.md` quotes. Re-run any of them with
`python evals/run.py --brief evals/briefs/<brief>.md --skill jbelly-ui`; a run spends real
subscription usage and will not reproduce exactly, because an agent is not deterministic.

| Brief | Context tokens | Billed | Minutes | Tool calls | Isolated | Record |
|---|---|---|---|---|---|---|
| 01-dashboard | 831,640 | 97,004 | 2.07 | 10 | yes | [`01-dashboard-jbelly-ui-20260919-162651.json`](01-dashboard-jbelly-ui-20260919-162651.json) |
| 02-landing | 1,321,657 | 132,137 | 7.21 | 13 | yes | [`02-landing-jbelly-ui-20260919-164728.json`](02-landing-jbelly-ui-20260919-164728.json) |
| 03-pricing | 4,906,916 | 182,638 | 9.28 | 41 | yes | [`03-pricing-jbelly-ui-20260919-170349.json`](03-pricing-jbelly-ui-20260919-170349.json) |
