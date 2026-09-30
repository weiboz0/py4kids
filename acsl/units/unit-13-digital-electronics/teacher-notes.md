# Teacher Notes — Unit 13: Digital Electronics

## Goals

Students learn the Contest 4 Digital Electronics category, which every programming division takes.
By the end they can:

- name the eight gates (BUFFER, NOT, AND, NAND, OR, NOR, XOR, XNOR) and give each one's truth table;
- read a circuit as a netlist (`INPUTS A B C`, then one gate per line, with the last gate the output) and as an ASCII sketch, as a drawn circuit on a real paper would show it;
- turn a circuit into a Boolean expression in unit 08's notation, and find its output for given inputs;
- list the tuples that make a circuit TRUE or FALSE, count them, and remember that an input no gate uses still doubles the rows;
- simplify a circuit to its unique minimal sum of products;
- (Intermediate and above) handle four inputs and XNOR chains; (Senior) recognise NAND-only and NOR-only circuits that equal a given function;
- write a Python circuit simulator with a dict of signal values.

The hook is "The Greenhouse Alarm": `p = NOR(A, B)`, `q = NOT(C)`, `r = NAND(p, q)`, `alarm = BUFFER(r)`. It is silent only at `(0,0,0)`, and simplifies to `A + B + C`.

## Pacing

Budget: three lessons of 60–90 minutes in the Contest 4 window.

- **Lesson 1, Junior and above.**
  - The eight gates, their truth tables and their symbols described in words.
  - Circuits as netlists and ASCII sketches; from a circuit to an expression.
  - Outputs, tuples and counts, including an unused input; the wiki's first sample (`(1,1,0)` is the only FALSE triple).
- **Lesson 2.**
  - Simplifying circuits (the hook, and the wiki's sample that is always `0`) and equivalent circuits.
  - Intermediate: four inputs and XNOR chains. With 3 inputs a chain is TRUE when an odd number of inputs are 1; with 4 inputs, when an even number are.
  - Senior: NAND and NOR are universal (answered by option choice).
- **Lesson 3.**
  - A circuit simulator in Python: a `gate()` function, a word parser, a dict of signal values, and the full truth table with its TRUE count.
- **Exercises:** 22 items. Exercises 1–12 are Junior (programs 10–12); 13–18 are Intermediate (program 18); 19–22 are Senior (21–22 are Challenges; 22 is a program).

**60-minute cut:** keep the gates, netlists and truth tables; set simplification and the simulator as reading plus Exercises 7 and 12.

## Common mistakes

- Mixing up NAND with NOR, or XOR with XNOR.
- Treating a NAND as "NOT A AND NOT B"; it is `~(A * B)`, which by De Morgan is `~A + ~B`.
- Leaving out a column for an input no gate uses: it still doubles the rows (and the count).
- Evaluating gates out of order; a gate can use only inputs or gates above it.
- Writing a simplification in a different order from the book's canonical sum of products.
- In an XNOR chain, guessing the pattern instead of checking the parity rule on one row.

## Discussion prompts

- Why is NAND called universal? Build NOT, AND and OR from NAND gates alone.
- How does a circuit's truth table tell you which gates you could remove?
- Where are logic gates in the devices around you?
- Two different circuits have the same truth table. Are they the same circuit?

## Differentiation

- **Junior:** Lessons 1–3 without the Intermediate and Senior sections; Exercises 1–12.
- **Intermediate:** everything except the Senior section; Exercises 1–18.
- **Senior:** the whole unit, including Exercises 19–22.
- **Classroom:** Classroom's Contest 4 includes Digital Electronics, so do the short-answer items at Junior and Intermediate level.
- **Elementary:** not part of the Elementary path.
- **Support:** a printed card with the eight truth tables, and a blank truth-table sheet with one column per gate.
- **Extension:** build XOR from four NAND gates, then check it with the Lesson 3 simulator.

## Answer forms

- Tuples and counts follow unit 08, with columns in the `INPUTS` order. Simplified expressions use unit 08's canonical sum of products.
- The Senior NAND/NOR items are option choices, decided by truth table.
