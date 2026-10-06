"""Answer normalisation and salted hashing (design 012 D5; plan 101 B).

Hidden `answer`, `predict` and `expected-output` items ship only `answer_hash` of their canonical
text. Part C's JavaScript port must agree byte for byte; `hash_vectors.json` pins the cases.
"""

import hashlib
import re

_WS = re.compile(r"\s+")  # str regex: every Unicode whitespace, NBSP included


def normalise(text: str, *, case: str) -> str:
    lines = [_WS.sub(" ", line).strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    out = "\n".join(lines)
    return out.casefold() if case == "insensitive" else out


def answer_hash(item_key: str, canonical: str, *, case: str) -> str:
    # The salt is the item's global key: public, per item, so equal answers hash differently (D5).
    payload = f"py4kids-answer-v1\n{item_key}\n{normalise(canonical, case=case)}"
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()
