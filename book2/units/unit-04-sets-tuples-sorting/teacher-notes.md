# Teacher Notes — Unit 04: Sets, Tuples & Sorting

## Goals

By the end of this unit students can:

- Build a set from a `{…}` literal or `set()` and test membership with `in` in O(1) average time.
- Remove duplicates by adding items into a set, and count distinct values.
- Compute union, intersection, and difference of two collections — using a loop with `.add`
  (and `-` for difference), *without* reaching for the `&`/`|` operators they have not met.
- Pack related fields into a tuple `(name, score)`, unpack with `for name, score in rows:`,
  and use a tuple as a composite record.
- Sort with `sorted(seq, key=by_field)` using a **named** key function, sort descending,
  and break ties with a compound key that returns a tuple `(-score, name)`.

These are the everyday tools of contest problems: fast lookup, dedup, and "sort then read off the answer."

## Pacing

Two 60–90 minute lessons.

**Lesson 1 — Sets: membership, dedup, and set math.**
Open with the project hook: two club rosters — how many distinct students in total, and who is in
*both*?
Live-code the distinct count (add every name into a set, then `len`).
Introduce membership: `name in members` is instant, unlike scanning a list.
Build intersection and difference by hand with a loop + `.add` (and show `a - b` for difference),
stressing *why* we avoid the `&`/`|` symbols for now (they mean something else the language uses
elsewhere — we meet that in Unit 11).
Class works Exercises 1–4 and 7 (distinct count, in-both, only-on-first, first repeat, allowed codes).
Watch for the decisive value hiding in the last position of Exercise 4.

**Lesson 2 — Tuples and custom sorting.**
Motivate tuples as little records: a player is `(name, score)`, not two loose variables.
Unpack them in a loop; use them as sort keys.
Teach `sorted(rows, key=by_score)` with a named function, then descending, then the compound
`(-score, name)` key that sorts by score high-to-low and breaks ties by name A-to-Z.
Class works Exercises 5, 6, 8, 9 (leaderboard, top-K boundary, partner groups, allowed finalists).

## Common mistakes

- Reaching for `&`, `|`, or `-`… as *operators on lists* — sets support the math, lists do not;
  we build the results with an explicit loop and `.add` so the logic is visible.
- Mutating a set while looping over it (add to a *new* set instead).
- Assuming `sorted` reorders in place — it returns a new list; the original is unchanged.
- Forgetting the tie-breaker: sorting by score alone leaves equal scores in an unpredictable order;
  the compound key fixes the order the problem asks for.
- Stopping a membership/dedup scan one element early and missing a decisive final value
  (Exercise 4 is built to catch this).

## Discussion prompts

- Why is `x in a_set` so much faster than `x in a_list` for large collections? Where does the speed
  come from, and what do we give up (order)?
- Exercise 5 asks for score descending but name ascending. Why can't a single number as the key do
  both? How does returning a tuple solve it?
- When is a tuple the right container and when would a list be better? What can you do to a list that
  you cannot do to a tuple?
- Intersection can be written many ways. Which is clearest, and does clarity cost us any speed here?

## Differentiation

- **More support:** start Exercises 1 and 3 together as a class; give a filled-in `by_score` key
  function for Exercise 5 so the focus is on calling `sorted` with a key.
- **More challenge:** the stretch problems (8 Partner Groups, 9 Allowed Finalists) combine dedup,
  tuple keys, and sorting; ask students to state each solution's Big-O and justify why the constraints
  (up to 10⁵ items) rule out an all-pairs O(n²) approach.
- **Extension:** have fast finishers re-solve Exercise 2 with the roles reversed (who is in *either*
  club) and compare the union code to their intersection code.

### Big-O per exercise

1. Distinct Badge Count — O(n) (set dedup + `len`).
2. Students in Both Clubs — O(n) (build one set, scan the other for membership).
3. Only on the First Roster — O(n) (membership difference).
4. First Repeated Ticket — O(n) (single scan with a "seen" set).
5. Final Leaderboard — O(n log n) (compound-key sort).
6. Last Player in the Top K — O(n log n) (sort, then read index K−1).
7. Unique Allowed Codes — O(n) (dedup then remove the banned set).
8. Partner Groups *(stretch)* — O(n) (dedup tuple records into a set, `len`).
9. Allowed Finalists *(stretch)* — O(n log n) (membership filter, then compound-key sort).
