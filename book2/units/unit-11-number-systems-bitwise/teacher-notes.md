# Teacher Notes — Unit 11: Number Systems, Bitwise & Number Theory

## Goals

By the end of this unit students can:

- Convert a number between decimal, **binary**, and **hexadecimal** BY HAND (repeated `% / //` for the digits;
  positional value to parse) — no `bin`/`hex`/`int(s, base)` shortcuts.
- Use the **bitwise operators** `&` `|` `^` `~` `<<` `>>`, and test / set / clear bit `i` with
  `x & (1<<i)`, `x | (1<<i)`, `x & ~(1<<i)` — always masking `~` to a stated **finite width** `((1<<w)-1)`.
- Enumerate every subset of a small set with a **bitmask** (`for mask in range(1<<n)`; `mask & (1<<i)`).
- Compute the **GCD** with iterative Euclid and the **LCM** as `a // gcd * b`.
- Build a **sieve of Eratosthenes** (crossing off multiples from `p*p`) to answer prime questions fast.
- Do **modular arithmetic** ("answer mod M") by reducing as you go so intermediate values stay small.

This is a number-theory toolkit unit. Everything is **iterative** (no recursion — that is Unit 9's tool and is
not used here); lists are built with `while`/`append` (never `[0]*n`).

## Pacing

Three 60–90 minute lessons.

**Lesson 1 — Binary & bitwise (≈60–75 min instruction, rest practice).**
Write numbers in binary by repeated division; read them back by positional value. Hexadecimal is introduced as
reading (its digits `A–F` = 10–15) and practiced in Lesson 2. Live-code the bitwise operators and the
test/set/clear-bit idioms, then the **finite-width NOT** rule (`~x & ((1<<w)-1)`) — stress that Python's `~x`
is infinite-width (`~5 == -6`) so a width must always be fixed.
Class works Exercises 1, 3, 4 (decimal→binary; light-panel bit commands; lone XOR code).

**Lesson 2 — Bitmasks & GCD/LCM.**
Work hexadecimal conversion both directions. Introduce the bitmask loop: one integer `mask` per subset, test
membership with `mask & (1<<i)`; connect to the subset searches of Unit 9 (same subsets, different tool).
Then iterative Euclid and the integer-safe `lcm = a // gcd * b` (with the `lcm(0, x) = 0` edge).
Class works Exercises 2, 5, 6 (hex converter; exact-cargo bitmask; GCD/LCM).

**Lesson 3 — Sieve & modular arithmetic.**
Build the sieve with a `while`/`append` boolean list and cross off multiples starting at `p*p`; discuss why
the crossing-off bound is `p*p` and why the sieve is near-linear. Then modular arithmetic: "answer mod M",
reducing after every step so values never explode; note Python's `-3 % 5 == 2` and that outputs are
non-negative.
Class works Exercises 7, 8 (prime count; power mod M). Assign the stretch problems (9, 10) as extension.

## Common mistakes

- **Bit-index off-by-one** — bit `i` is `1 << i`, and bit 0 is the ones place; drawing the bits helps.
- **`[False]*n` / `'0'*n` habit** — list and string repetition are untaught here; build the sieve array and
  any zero-padding with a `while`/`append` loop.
- **Infinite-width `~`** — `~x` alone is a negative number; every complement problem fixes a width `w` and
  masks with `((1<<w)-1)`.
- **Forgetting the final `% M`** — reduce as you go AND reduce the final answer; a missing last `% M` passes
  small samples and fails large ones.
- **Sieve boundary** — cross off from `p*p` and include the bound correctly (`p*p <= n`); an upper bound like
  49 (= 7²) is the case that catches a `<` vs `<=` slip.
- **Hex digits** — values 10–15 print as `A–F`; forgetting the letter digits corrupts conversions.
- **Reaching for recursion** — this unit is iterative; a recursive helper would also be flagged as an
  out-of-unit feature.

## Discussion prompts

- Why does repeated division by 2 produce the binary digits in reverse order, and how do you reassemble them?
- A bitmask gives the same subsets as Unit 9's recursive search. When is the bitmask loop the better tool, and
  what limits it (why must `n` stay small)?
- In "compute a huge power mod M", why does reducing after each multiplication give the same answer as
  reducing only at the end — and why can't you skip the reductions in practice?
- Why does the sieve only need to cross off multiples starting at `p*p`, not `2*p`?

## Differentiation

- **More support:** give the digit-extraction loop skeleton for Exercises 1–2 and the `mask & (1<<i)` test for
  Exercise 5; pre-write the input parsing so students focus on the number logic.
- **More challenge:** the stretch problems (9 Fixed-Width Hex Complement, 10 Nth Prime) combine conversion +
  masking and sizing a sieve bound; ask students to state the Big-O and justify the sieve bound they pick.
- **Extension:** ask fast finishers to explain why repeated-squaring makes a power-mod fast, or to estimate the
  sieve size needed for the nth prime.

### Big-O per exercise

_(reconciled against the shipped reference solutions in Phase C)_

1. Decimal to Binary by Hand — O(log n) (one digit per division).
2. Two-Way Hexadecimal Converter — O(d) for a d-digit value.
3. Light Panel Commands — O(C) over C commands (each bit op O(1)).
4. Lone Signal Code — O(N) (one XOR pass).
5. Exact Cargo Team — O(2ⁿ·n) (one mask per subset of n items).
6. GCD and LCM Reports — O(log min(a,b)) per pair (Euclid).
7. Prime Count Through a Boundary — O(n log log n) (sieve).
8. Astronomical Power Modulo M — O(log e) via repeated squaring, each step reduced mod M.
9. Fixed-Width Hex Complement *(stretch)* — O(d) (mask to width, then convert).
10. Nth Prime *(stretch)* — O(B log log B) for a sieve bound B sized to contain the nth prime.
