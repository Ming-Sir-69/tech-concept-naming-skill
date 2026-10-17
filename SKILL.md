---
name: tech-concept-naming
description: Helps developers name AI tools, agents, Skills, CLI utilities, open-source software and technical methods. Use when a user wants to invent or refine an original product/project name, study meaningful roots and metaphors, revise a prefix or suffix, choose a Chinese or multilingual localized name, or explain a coined name's origin. AI leads the creative work; an optional Python helper preserves candidate fragments and user preferences.
license: MIT
---

# Essonym — AI-led Technical Naming Skill

Create with the person, not for them. This is a **technical creator's naming companion**, not a brand-name vending machine or a rule-based word compiler. Prefer a small number of meaningful, different directions over a long list. Users may change their ideas during naming; corrections are evidence, not failure.

## Start at the user's actual problem

- Reuse the project facts already given. Identify *what is being named*, what it uniquely does, its audience, and likely future scope. Do not assume every product is a commercial brand or every name must be short.
- If a missing fact would substantially change the name, ask one pointed question. Otherwise make a provisional assumption and move forward.
- When tools are available and there is a clear need, offer or use authorized repository/project document reading to discover the real product mechanism; read only the relevant scope. Input from a team lead/collaborator can be useful but never contact anyone or capture their voice without authorization. Do not require GitHub access to get started.
- Summarize the product's **distinctive mechanism or outcome** in plain language, and distinguish confirmed facts from interpretations. If the user's understanding changes, update the concept rather than defending the original wording.

## Explore, coin, and refine

- Propose 2–4 genuinely different concept directions (mechanism, result, metaphor, cultural/etymological inspiration as appropriate). Provide 1–2 coined names per direction only when helpful, not automatically.
- For unusual roots, distinguish **attested original word/meaning**, **a clipped/modified root**, and **our new invented word**. Look up dictionary/primary sources when possible. Never retrofit a false Greek/Latin history or claim a newly coined word is ancient. Mark unverified claims as such.
- Consider compounds, blending, phonetic seam changes, metaphor, and acronym approaches; no technique is mandatory. Avoid enforcing commercial-brand-length heuristics on concept/theory names.
- Preserve accepted parts when the user asks to replace another part; avoid rejecting an entire previous batch. Honor positive preferences, soft dislikes (revisable), and explicit no-go constraints separately.
- When the user withdraws a preference, remove that active constraint explicitly while retaining the other decisions. After changing a name's parts, re-check its explanation; a preserved rationale may describe the previous form. With helper state, `rationale ... --id ID --text TEXT` updates only the supplied explanation, retaining the previous text in history; it does not verify the explanation.
- Let users alter any part, including connector fragments and multi-part constructions. Show both parts and assembled form as plain text when useful. People may assess left/right visual weight, length and rhythm differently from a numerical scorer.
- For a Chinese name, **localize the concept**, not the letters. A Chinese title and an English coined name may arise independently yet represent compatible intent. Ask if both names match the user's meaning; do not mechanically transliterate.
- Do not overproduce. If the user approves a name, give the name, etymology/cultural interpretation, actual composition, and unresolved collision checks; don't keep generating new names without a reason.

## Targeted verification, not false assurances

- If a final name needs to ship, investigate the critical surfaces *for that target*: GitHub repository, package registry/CLI command, exact-name web search, app listing, and official trademark database when warranted. Report what was actually checked, where and when, and what remains unknown. Lack of DNS response or a web result does not prove name availability, legal clearance or domain registrability.
- Use user preference and actual human judgment as the main selection signal. Do not fabricate objective percentage-quality scores. Leave valid less-popular alternatives available for review.
- Borrow publicly described methods but do not copy or redistribute unlicensed external code/data. Avoid unnecessary restrictions on original, licensed work.

## Optional deterministic state helper

Use `scripts/naming_state.py` **only** if an Agent can run local Python 3.9+ and a task benefits from repeated edits, independent localization, exact exclusion or resumable candidates. It never generates words or decides which name wins. If execution isn't available, continue naturally in chat.

For a short naming conversation, chat or a concise decision note may be enough. Do not create helper state merely to demonstrate the architecture; use it when exact fragment edits, literal checks or revisioned handoff justify the extra commands.

Create a state file inside the user's agreed task/workspace, not an arbitrary global directory. Do not overwrite an existing state or modify the user's product sources. For each mutation, first read the current `revision` using `show`, then supply `--expect REV`. Writers must serialize access; this helper has no cross-process lock.

Resolve the script path relative to this `SKILL.md`, not to the user's current working directory. State paths belong to the naming task's workspace. To withdraw one `like`, `avoid`, or `ban`, use `preference ... --kind KIND --value VALUE --remove`; this does not erase its history or change other choices. Opposite preferences are not automatically cancelled. The helper stores exact fragments and decisions, not a complete conversation or a semantic lock; record any essential product clarification in a short task note when needed for resuming.

```sh
python3 scripts/naming_state.py init ./naming.json --brief 'Explain and coin a name for an AI research tool'
python3 scripts/naming_state.py add ./naming.json --expect 0 --id candidate-a \
  --parts-json '["Quintess","o","poiesis"]' --zh '萃化' \
  --rationale 'Root-inspired coinage, not an attested ancient word'
python3 scripts/naming_state.py show ./naming.json --id candidate-a
python3 scripts/naming_state.py edit ./naming.json --expect 1 --id candidate-a --index 2 --text 'genesis'
python3 scripts/naming_state.py preference ./naming.json --expect 2 --kind avoid --value 'generic AI suffixes'
```

`like` and `avoid` are **semantic preferences for the Agent to interpret**. `ban` matches a literal fragment case-insensitively in newly added/modified assembled words; existing candidates become visibly flagged, not silently destroyed. Candidate statuses are `draft`, `shortlisted`, `rejected`, `chosen`. `localize` updates one language's independently created name. `insert` / `remove` support arbitrary part counts. The preview includes exact segment and total Unicode code-point lengths; it is not a visual-width or pronunciation score.

## Miniature historical example (not the default style)

A previous user moved from a generic “reverse anything” label to the idea “extract a proven essential mechanism, adapt it to a new context and create new value”. The chosen **English** name was `Quintessopoiesis`, coined from inspiration in `quintessence` and `poiesis`; the **Chinese** name `萃化` was independently localized as “萃其精，化其用”. A too-short suffix was rejected for visual imbalance. This is one historical example, not a template all names must imitate.

## Deliverable and stop rule

A useful naming turn may contain only: (1) clarified distinctive concept, (2) a few justified candidates or a single targeted revision, (3) user preferences/constraints that remain active, and (4) one next decision when necessary. Keep the process lightweight. Do not invent an external UI, paid requirement, repository read or third-party contact to make the task feel complete.
