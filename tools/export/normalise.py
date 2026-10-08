"""Answer normalisation and salted hashing (design 012 D5; plan 101 B; plan 102 Phase 0).

Hidden `answer`, `predict` and `expected-output` items ship only `answer_hash` of their canonical
text. Part C's JavaScript port must agree byte for byte; `hash_vectors.json` pins the cases.

The steps, in order (an item's `answer_format` picks `case`, `whitespace` and `aliases`):

1. **Lines.** CRLF and lone CR become LF.
2. **Whitespace.** `collapse` (the default) turns every run of Unicode whitespace in a line into one
   space and strips each line. `exact` only strips trailing whitespace from each line, keeping tabs,
   leading indentation and inner runs. Both then drop leading and trailing blank lines.
3. **Case.** `insensitive` casefolds the text.
4. **Aliases.** Each `{typed: canonical}` pair replaces the typed form with the canonical one, in
   one left-to-right pass that tries the longest key first (a replacement is never re-scanned).
   Under `insensitive` the keys and values are casefolded too, so they match the folded text.
"""

import hashlib
import re

_WS = re.compile(r"\s+")  # str regex: every Unicode whitespace, NBSP included
WHITESPACE_MODES = ("collapse", "exact")


def _apply_aliases(text: str, aliases: dict[str, str], fold: bool) -> str:
    table = {(k.casefold() if fold else k): (v.casefold() if fold else v)
             for k, v in aliases.items() if k}
    if not table:
        return text
    pattern = re.compile("|".join(re.escape(k) for k in sorted(table, key=lambda k: (-len(k), k))))
    return pattern.sub(lambda match: table[match[0]], text)


def normalise(text: str, *, case: str, whitespace: str = "collapse",
              aliases: dict[str, str] | None = None) -> str:
    if whitespace not in WHITESPACE_MODES:
        raise ValueError(f"unknown whitespace mode {whitespace!r}")
    raw = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if whitespace == "collapse":
        lines = [_WS.sub(" ", line).strip() for line in raw]
    else:
        lines = [line.rstrip() for line in raw]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    out = "\n".join(lines)
    fold = case == "insensitive"
    if fold:
        out = out.casefold()
    return _apply_aliases(out, aliases or {}, fold)


def answer_hash(item_key: str, canonical: str, *, case: str, whitespace: str = "collapse",
                aliases: dict[str, str] | None = None) -> str:
    # The salt is the item's global key: public, per item, so equal answers hash differently (D5).
    text = normalise(canonical, case=case, whitespace=whitespace, aliases=aliases)
    payload = f"py4kids-answer-v1\n{item_key}\n{text}"
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()
