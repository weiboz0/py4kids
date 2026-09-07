# Teacher Notes — Project 01: Arcade Night

## Goals

Students combine everything from Term 2 — functions that return values, loops, conditionals,
and randomness — into a working mini-arcade they designed. This is the payoff of unit 05:
functions stop being an exercise and become the tool that makes a real program possible.
Success looks like: every student demos a playable arcade with at least two scoring games,
and the class plays each other's on showcase day.

## Pacing

Budget: two lessons of 60–90 minutes, run as design → build → showcase.

The brief's milestones run M1 menu → M2 game one → M3 game two → M4 running total, so the
two lessons split along that order:

- **Lesson 1 — design + Milestones 1–2 (the minimum bar).**
  10 min: the hook — the teacher plays a finished arcade; the class lists what makes it fun.
  10 min: design on paper — pick two games, name each game's function and what it returns.
  40 min: BUILD Milestones 1–2 — the menu loop (M1) and the FIRST game as a function that
  returns points, called from the menu and showing that game's points (M2). Every student
  reaches a playable one-game arcade by end of lesson 1 — nobody leaves without something
  that runs.
- **Lesson 2 — Milestones 3–4, extensions, showcase.**
  25 min: the SECOND game function (M3) and the running total across both games (M4).
  20 min: `## Make it yours` — a third game, a high-score line, or a difficulty parameter.
  15 min: SHOWCASE — pairs swap seats and play each other's arcades; each author notes one
  thing they'd add next.

Differentiation: strugglers ship the one-game minimum bar as a complete, celebrated result;
the second game and extensions are where faster students spend lesson 2.

## Common mistakes

- A game function that PRINTS the points instead of RETURNING them, so the total can't add
  them up (the return-vs-print gap from unit 05 — the single most common project bug).
- The score variable reset inside the menu loop, so it never accumulates.
- The menu loop with no `break`/quit path — an arcade you can't leave.
- Comparing a typed menu choice as a number without `int()`, or vice versa.
- `random.randint(a, b)` bounds confusion (both ends inclusive).

## Discussion prompts

- Why is each game a FUNCTION instead of just code in the menu? (Reuse, a clean score,
  swapping games in and out.)
- What makes an arcade fun to a player vs. easy to build? Where do those pull apart?
- How would you add a two-player mode with what you know now?

## Differentiation

- Strugglers: provide a menu + one-game skeleton with the game function's `def` line and
  `return` stubbed; they fill the body. The one-game arcade is a full, valid submission.
- Middle tier: the second game and a high-score message.
- Fast finishers: a difficulty toggle passed as a parameter, or a third game — all inside
  the taught concept set (no lists needed; a third `elif` branch handles a third game).

## Rubric

Assess each student's OWN arcade against these criteria — there is no fixed answer key; the
games differ by design. Judge the BUILD, not a match to a reference.

**Meets the brief (full credit — the spec is TWO games):**
- TWO games, each implemented as a function that RETURNS points (not prints them).
- A menu the player navigates and can QUIT (a `while` loop with a `break`/quit path).
- A running total `score` that accumulates across both games, shown with an f-string.
- The program RUNS without crashing on normal play.

**Developing (a valid, celebrated result for strugglers — below the two-game spec):**
- ONE working game function that returns points, wired into a menu with a running total
  and a quit path. This is the end-of-lesson-1 minimum bar; a student who ships exactly
  this has a real, playable arcade — mark it complete-for-them and note the second game as
  the next step, don't fail it.

**Milestone-by-milestone "what done looks like":**
1. **Menu loop:** loops until the player quits; each choice routes to a game or exits.
2. **Game one (function returning points):** takes the player's input, returns an integer
   score for that round — the return is the point.
3. **Game two (function returning points):** a genuinely different game, same return contract.
4. **Running total:** score starts at 0 outside the loop, grows by each game's return,
   displays a scoreboard.

**Stretch (beyond the bar — recognize, don't require):**
- A third game, a high-score/personal-best message, a difficulty toggle via a parameter,
  a rounds-played counter, thematic polish.

**Re-teach signal:** if a third of the class or more ships a game that PRINTS points instead
of returning them, the return-vs-print idea from unit 05 needs one more focused example
before the next project — it is the concept the whole build hinges on.
