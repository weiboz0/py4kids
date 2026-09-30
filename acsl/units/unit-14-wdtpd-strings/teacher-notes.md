# Teacher Notes — Unit 14: What Does This Program Do? – Strings

## Goals

Students learn Junior's third Contest 4 category: tracing programs that work on strings, and writing their exact one-line output.
By the end they can:

- read ACSL string positions, which start at 0, with `len(S)` and `S[j]`;
- apply ACSL's three substring forms, which are **not** Python slices: `S[:n]` is the first n characters, `S[n:]` the **last** n characters, and `S[a:b]` positions a **through** b;
- translate each form to Python, and predict the length of a piece before tracing;
- trace loops over characters that count, build, reverse, and compare with `+` and `==`;
- check palindromes, compare letters by alphabetical order, and shrink a string in a `WHILE` loop.

The hook is "The Password Machine": `S = "ELEPHANT"`, and the password is `S[3:] + S[1:3] + S[:2]`. Read by ACSL's rules it prints `ANTLEPEL 8`; read with Python's slices it prints `PHANTLEEL 9`. The whole unit turns on that difference.

## Pacing

Budget: three lessons of 60–90 minutes in the Contest 4 window.

- **Lesson 1.**
  - Positions, `len` and `S[j]`.
  - The three ACSL substring forms beside their Python translations, and the Python-slice trap.
  - Piece lengths, `+` and `==`.
- **Lesson 2.**
  - Loops over characters: counting, vowels with `||`, building a new string, reversing, palindromes.
- **Lesson 3.**
  - A moving two-letter piece `S[j:j + 1]` and endings `S[k:]`.
  - Comparing capital letters, ordering pairs, and shrinking a string with `WHILE`.
- **Exercises:** 19 items, all Junior (16 short answers; 3 predict-then-verify programs: 8, 13 and 17); 18–19 are Challenges. 14 of the 19 are in ACSL pseudocode. Exercises 2 and 3 are a pair: the same program under Python's rules and under ACSL's.

**60-minute cut:** keep Lesson 1 in full (it holds the trap) and Lesson 2's loops; set Lesson 3 as reading plus Exercises 10–11.

## Common mistakes

- Reading `S[n:]` as Python does ("from position n to the end") instead of ACSL's "the last n characters".
- Reading `S[a:b]` as stopping before b; ACSL includes position b.
- Starting positions at 1; ACSL strings start at 0.
- Forgetting that `len` changes when a loop shrinks or builds the string.
- Stopping a `FOR` loop one pass early; ACSL includes the end value.
- Comparing letters by position in the word instead of alphabetical order.

## Discussion prompts

- Why does ACSL's `S[n:]` mean "the last n", and when is that handier than Python's form?
- How can you know a piece's length before you trace it?
- How would you check a palindrome with only `S[j]` and a loop?
- In the hook, which piece changed the answer most when read with Python's slices?

## Differentiation

- **Junior:** the whole unit; this is Junior's Contest 4 WDTPD category.
- **Intermediate and Senior:** extra string drill only. Their Contest 4 has Assembly Language instead, and they met strings in Contest 1's WDTPD unit.
- **Classroom:** optional practice (Classroom's Contest 4 categories are Graph Theory, Digital Electronics and Assembly Language).
- **Elementary:** not part of the Elementary path.
- **Support:** printed strips of numbered boxes (from 0) for each string, and a card with the three ACSL substring forms and their Python translations.
- **Extension:** write a three-line program whose output changes when read with Python's slices, and trade it with a partner.
