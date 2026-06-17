# Functional Design Plan — Unit 1: Data Layer

## Plan Checkboxes

- [x] Answer open questions below
- [x] Generate domain-entities.md
- [x] Generate business-rules.md
- [x] Generate business-logic-model.md
- [x] Validate design completeness

---

## Context (pre-settled from INCEPTION)

Already decided — no questions needed on these:
- Todo fields (required + optional), subtask model, Status/Priority enums — see requirements.md
- Separate `subtasks` table with FK + CASCADE — Application Design Q4
- Soft-delete via `deleted_at` column — requirements FR-04
- One-level subtask depth only — requirements FR-01
- Filtering/sorting/pagination params — requirements FR-03
- Standard validation (required fields, enum values, UUID format, max-length) — requirements FR-05

---

## Open Questions

Please fill in the letter choice after each `[Answer]:` tag, then let me know when done.

---

### Question 1
When paginating `list_todos`, if the requested `page` number exceeds `total_pages`, should the server:

A) Return an empty `items` list (no error — out-of-range page silently returns nothing)
B) Return a structured MCP error with code `PAGE_OUT_OF_RANGE`
X) Other (please describe after [Answer]: tag below)

[Answer]: option B

---

### Question 2
For the `tags` field on a Todo, should tag values be **case-sensitive** or **case-insensitive** when filtering?

A) Case-sensitive — `@Computer` and `@computer` are different tags
B) Case-insensitive — tags are normalised to lowercase on write; filter matches are lowercase too
X) Other (please describe after [Answer]: tag below)

[Answer]: option A

---

### Question 3
When `update_todo` is called and the caller passes a `subtasks` list, should it **replace** the existing subtasks entirely, or **merge** (add new ones, update existing by id, leave unmentioned ones in place)?

A) Replace — the provided list becomes the new complete set of subtasks (simpler, predictable)
B) Merge — provided subtasks are upserted by id; subtasks not in the list remain unchanged
X) Other (please describe after [Answer]: tag below)

[Answer]: option B
