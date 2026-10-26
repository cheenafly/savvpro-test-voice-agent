# AI session log

Running notes from building this project with Claude Code (model: Claude Opus 5.5), kept
as raw material for `AI_USAGE.md`. Each phase lists what the AI got wrong or had to fix,
where the work deviated from `PLAN.md`, and anything else worth mentioning.

Token counts are not in this log: the assistant cannot see its own usage. Capture them
with `/cost` or `/usage` at the end of each session (and `npx ccusage` for totals).

## Phase 0 — Setup

- Only Python 3.14 is installed on the dev machine; the plan assumed 3.11. Everything
  installed and ran on 3.14 (including `piper-tts` and `faster-whisper`), so the project
  targets 3.14 (`pyproject.toml`).
- The plan expected `backend/requirements.txt`; the file was at the repo root, so it was
  moved into `backend/` unchanged.
- `requirements.txt` had a typo (`ruff>=0.5.` with a trailing dot). pip accepted it; it was
  fixed during the Phase 0 wrap-up.
- The first `pip install` created a virtualenv at the repo root before the backend
  layout existed; it was later deleted in favour of `backend/.venv`.
- Commit attribution was turned off in `.claude/settings.json`, and commit-message rules
  were added to the (local, untracked) `CLAUDE.md`.
- Personal working files (PLAN.md, CLAUDE.md, `.claude/`) were removed from branch
  history with `git filter-branch`. **Gotcha:** filter-branch's final checkout deleted those
  files from disk too. The assistant had backed them up first and restored them.

## Phase 1 — Database and fake data

- **Deviation:** `appointments.slot_id` uniqueness is a *partial* unique index (only rows
  with `status = 'booked'`), not a plain unique column. A plain unique column would make a
  cancelled slot impossible to book again. The DB still rejects two active bookings for one
  slot.
- Double-booking is prevented by a conditional `UPDATE ... WHERE is_booked = false` plus
  that index; tests cover same-session, two-connection and raw-insert cases.
- **AI mistake (test):** a test meant to check "soonest appointment by phone" picked two
  slots that were both at 09:00 (one per doctor), so neither was sooner. Fixed the test
  setup, not the code.
- Ruff asked for quoted forward references in the models to be unquoted (UP037); that
  works on Python 3.14's deferred annotations, and the tests confirm it.

## Phase 2 — NLU

- **dateparser surprises:** `"next monday"` and `"this friday"` return `None`, and
  `"the 5th"` returns a date that has already passed even with
  `PREFER_DATES_FROM="future"`. Both are worked around in `entities.py` and covered by tests.
- **Classifier accuracy started at 0.70** on the held-out split (25–35 utterances per
  intent). Hyper-parameter tuning (C, n-gram ranges, LinearSVC, SGD) moved it by less
  than 1 point; what helped was data and representation.
- **Deviation — entity placeholders ("delexicalization"):** before classification, entity
  values are replaced by placeholder words ("cardiology on monday" → "somedepartment on
  somedate"). The biggest single gain (inform 0.70 → 0.82 F1). Not in the plan.
- **AI-introduced bug — YAML type coercion:** `03001234567` in `intents.yaml` loaded as
  an *octal integer* (402995575), and `yes`/`no` loaded as booleans. The assistant's own
  script for merging new utterances then wrote them back as the words `true`/`false`, so
  the training data was silently corrupted. Spotted in a list of misclassified utterances;
  fixed by quoting, a loader that rejects non-strings, and a test.
- **AI bug — booking reference regex:** it matched any 6-letter word starting with "sc"
  ("screen", "school", "scared"). Spotted when "my phone screen is broken" became
  "my phone bookingref is broken" in the training features. Fixed with regression tests.
- **AI over-correction:** lowering the doctor-name fuzzy threshold from 85 to 80 (to accept
  "dr saema") also made "with usama" match Dr. Saima. Split into 80 after "dr/doctor" and
  85 after the weaker "with".
- Other regex false positives caught during manual checks: "go to 2 doctors" parsed as the
  time 14:00; "my name is Bilal Aslam" matching the doctor of the same name.
- Data was added in 8 rounds (561 → 1,726 utterances). Some early training labels were
  ambiguous ("is parking free", "do you have a pharmacy") and were removed.
- **Deviations from the plan:** char_wb n-grams 2–4 instead of 3–5 (same accuracy, smaller
  model); LogisticRegression C=10 (the default spread probabilities too thinly to pass the
  0.60 fusion threshold); weights stored as float32 (halves the file, max probability change
  4e-8). The model is 558 KB and is committed.
- **The report prints two views:** the plan's 80/20 split, and 5-fold cross-validation where
  every utterance is predicted once. With only 10–50 test examples per intent the split is
  noisy (one error moves an intent's F1 by 0.03–0.10).
- **Not fully met:** "every intent ≥ 0.85" — final held-out accuracy 0.902 (CV 0.903), but
  `list_departments` is 0.833 on the split and `out_of_scope` 0.845 in CV. Stopped after 8
  rounds as gains had flattened; reported rather than tuned to the number.
- Some fixes to Phase 2a files (YAML quoting, booking-ref regex) landed in the Phase 2b
  commit.

## Phase 3 — Dialogue manager

- **AI bug found in a manual run:** "my number is 0321" was treated as "change the phone
  number" (the word *number* matched a "which field do you want to change" rule), so the
  caller never got the format hint. Field-name clearing now only happens on a
  `change_request` or right after "what would you like to change?".
- **AI wrote a meaningless test** (`test_greeting_time_is_frozen`, asserting constants);
  removed before committing.
- **Weak test tightened:** one edge-case test checked the chosen slot against *all*
  bookings (including the ones the test made for "someone else"); it now checks the
  caller's booking by reference.
- **Mutation check:** temporarily disabling the emergency rule and the "pick an offered
  slot" logic made 7 edge-case tests fail, so the tests do exercise the behaviour.
- **Deviations from the plan:**
  - `app/clinic.py` holds clinic facts (name, invented address, opening hours, 30-day
    booking window) shared by seed data, policies and replies.
  - `ClinicRepository` (in `repository.py`) binds the repository functions to one
    session and clock; it is what the manager gets injected with.
  - `Frame` is a pydantic model rather than a dataclass so it serialises straight into
    API responses in Phase 4.
  - `check_availability` flows into the booking flow: the offered times can be picked
    and booked directly.
  - Entities are merged at any state, but only on slot-carrying intents: otherwise
    "what time do you close on Saturday?" would change the booking date.
  - Extra `Decision.action` values for the UI: `not_understood`, `silence`, `aborted`,
    `slot_unavailable`, `cancel_declined`, `ended_silence`.
  - Rescheduling keeps the same doctor by default.
- **Known limitations:** the "3 nearest" search ignores a requested doctor; "next Monday"
  means the coming Monday; offers list date and doctor, which is long when spoken.
- The emergency reply points callers to 1122 (Pakistan's public Rescue number) on purpose;
  it is the only real-world contact detail in the app.
