"""Committed topic vocabulary for the synthetic keyword text (design 011 §6, plan recsys-004).

The catalog has no real prose, so lexical retrieval (U3 BM25) and the later GloVe content
embeddings (U7) have nothing to index. This module is the **committed source of truth** for the
slice vocabulary: a curated list of common, real-English words (so a future GloVe subset has
near-total coverage) partitioned into topics.

Topics are ordered to match the keyword generator's per-book feature vector
(``gen_catalog.generate_keywords``):

    [ latent_pos_0 .. latent_pos_{dim-1},  latent_neg_0 .. latent_neg_{dim-1},  genre_0 .. genre_{g-1} ]

- the ``2 * latent_dim`` **latent-pole topics** carry the finer-than-genre structure a book's
  latent factors encode (each latent dimension has a positive and a negative pole with disjoint
  words, so latent-opposite books do not share tokens);
- the ``n_genres`` **genre topics** are thematic word banks, so a fantasy book's bag reads like
  ``dragon wizard quest magic`` — content that genre cosine and keyword BM25 can both exploit.

No network, no randomness here: the word lists are literals and :func:`build_topics` is a pure
deterministic partition. The keyword generator owns the only RNG (token sampling).
"""

from __future__ import annotations

# Thematic genre word banks, keyed by the catalog's genre name (``gen_catalog.GENRE_NAMES``
# order). Real, common English words so the GloVe subset derived later covers them.
GENRE_WORDBANKS: dict[str, tuple[str, ...]] = {
    "fantasy": (
        "dragon", "wizard", "magic", "quest", "kingdom", "sword", "spell", "elf",
        "sorcerer", "castle", "prophecy", "enchanted", "realm", "knight", "legend", "crown",
    ),
    "sci-fi": (
        "galaxy", "robot", "spaceship", "planet", "future", "alien", "laser", "orbit",
        "android", "starship", "colony", "quantum", "cyborg", "nebula", "warp", "reactor",
    ),
    "mystery": (
        "detective", "clue", "murder", "suspect", "alibi", "witness", "crime", "motive",
        "investigate", "evidence", "shadow", "secret", "puzzle", "hidden", "stolen", "trail",
    ),
    "romance": (
        "love", "heart", "kiss", "wedding", "passion", "lover", "letter", "dance",
        "promise", "embrace", "longing", "tender", "devotion", "affection", "courtship", "vow",
    ),
    "history": (
        "empire", "battle", "ancient", "revolution", "treaty", "dynasty", "conquest", "throne",
        "soldier", "siege", "era", "monument", "chronicle", "rebellion", "ruler", "campaign",
    ),
    "biography": (
        "life", "career", "memoir", "childhood", "journey", "legacy", "struggle", "fame",
        "portrait", "triumph", "ambition", "influence", "mentor", "rival", "destiny", "voice",
    ),
    "science": (
        "atom", "energy", "experiment", "theory", "molecule", "gravity", "cell", "evolution",
        "physics", "chemistry", "biology", "research", "discovery", "formula", "species", "data",
    ),
    "poetry": (
        "verse", "rhyme", "stanza", "metaphor", "lyric", "sonnet", "imagery", "rhythm",
        "silence", "moonlight", "ocean", "autumn", "whisper", "memory", "yearning", "dream",
    ),
    "horror": (
        "ghost", "haunted", "monster", "fear", "darkness", "nightmare", "curse", "grave",
        "demon", "scream", "blood", "terror", "vampire", "specter", "ritual", "dread",
    ),
    "adventure": (
        "treasure", "island", "explorer", "jungle", "mountain", "voyage", "danger", "map",
        "rescue", "wilderness", "expedition", "canyon", "river", "survival", "compass", "escape",
    ),
    "philosophy": (
        "truth", "reason", "ethics", "logic", "mind", "freedom", "justice", "meaning",
        "virtue", "wisdom", "existence", "morality", "knowledge", "doubt", "nature", "reality",
    ),
    "children": (
        "friend", "puppy", "garden", "rainbow", "playground", "cookie", "balloon", "kitten",
        "bedtime", "giggle", "picnic", "crayon", "bunny", "sunshine", "teddy", "lullaby",
    ),
}

# A general pool of common English words for the latent-pole topics. These carry no intrinsic
# theme — :func:`build_topics` slices the pool into ``2 * latent_dim`` disjoint latent topics, so
# each latent pole gets its own distinctive token cluster. Length comfortably exceeds the default
# ``2 * 16 = 32`` poles at >=16 words each.
GENERAL_POOL: tuple[str, ...] = (
    "forest", "stone", "window", "candle", "meadow", "bridge", "valley", "feather",
    "cottage", "orchard", "pebble", "willow", "thicket", "copper", "velvet", "amber",
    "marble", "ivory", "crimson", "golden", "silver", "winter", "summer", "spring",
    "morning", "evening", "twilight", "dawn", "desert", "glacier", "prairie", "lagoon",
    "reef", "dune", "clock", "mirror", "ribbon", "basket", "kettle", "spoon",
    "ladder", "anchor", "telescope", "journal", "envelope", "parchment", "quill", "ledger",
    "market", "tavern", "factory", "workshop", "warehouse", "courtyard", "balcony", "hedge",
    "fountain", "trellis", "arbor", "greenhouse", "vineyard", "echo", "murmur", "clamor",
    "thunder", "chime", "rustle", "sailor", "farmer", "weaver", "merchant", "shepherd",
    "hunter", "painter", "sculptor", "musician", "actor", "singer", "engine", "turbine",
    "gear", "piston", "circuit", "lever", "valve", "bread", "honey", "cheese",
    "apple", "berry", "pepper", "ginger", "cinnamon", "flame", "ember", "smoke",
    "spark", "furnace", "hearth", "wave", "tide", "current", "shore", "cliff",
    "cove", "cloud", "storm", "breeze", "frost", "mist", "drizzle", "wolf",
    "falcon", "otter", "badger", "sparrow", "salmon", "heron", "lynx", "maple",
    "cedar", "birch", "pine", "fern", "moss", "ruby", "emerald", "sapphire",
    "opal", "pearl", "topaz", "garnet", "jade", "tower", "gateway", "corridor",
    "attic", "cellar", "gallery", "parlor", "diary", "notebook", "almanac", "atlas",
    "pamphlet", "violin", "trumpet", "harp", "flute", "cello", "piano", "guitar",
    "linen", "cotton", "satin", "leather", "needle", "button", "buckle", "collar",
    "pocket", "sleeve", "pier", "mast", "ticket", "platform", "carriage", "railway",
    "tunnel", "junction", "whistle", "avalanche", "summit", "ridge", "plateau", "slope",
    "nectar", "pollen", "blossom", "petal", "thorn", "beacon", "torch", "chandelier",
    "glow", "shimmer", "riddle", "cipher", "pattern", "sequence", "symbol", "harvest",
    "scythe", "granary", "pasture", "haystack", "barn", "cavern", "grotto", "chasm",
    "hollow", "burrow", "comet", "meteor", "asteroid", "eclipse", "aurora", "horizon",
    "schooner", "galleon", "frigate", "clipper", "ferry", "barge", "loom", "shuttle",
    "fabric", "tapestry", "alley", "boulevard", "avenue", "plaza", "terrace", "footpath",
    "stairway", "doorway", "archway", "veranda", "goblet", "platter", "pitcher", "codex",
    "folio", "margin", "binding", "umbrella", "satchel", "pillow", "blanket", "mitten",
    "scarf", "jacket", "trousers", "sandal", "bracelet", "necklace", "pendant", "brooch",
    "lantern", "candelabra", "chalkboard", "notepad", "spinner", "domino", "kite", "pinwheel",
    "acorn", "pinecone", "chestnut", "walnut", "almond", "hazelnut", "sprout", "clover",
    "daisy", "tulip", "lily", "orchid", "daffodil", "poppy", "violet", "jasmine",
    "beetle", "cricket", "firefly", "dragonfly", "ladybug", "grasshopper", "moth", "hornet",
    "pelican", "flamingo", "penguin", "ostrich", "peacock", "robin", "finch", "swallow",
    "dolphin", "walrus", "seal", "beaver", "raccoon", "hedgehog", "squirrel", "chipmunk",
    "boulder", "gravel", "quartz", "granite", "limestone", "crystal", "flint", "obsidian",
    "harbor", "wharf", "lighthouse", "buoy", "rudder", "paddle", "oar", "hull",
    "pottery", "sculpture", "mural", "fresco", "canvas", "easel", "palette", "brush",
    "cottage", "mansion", "cabin", "bungalow", "lodge", "chalet", "shelter", "outpost",
    "whisker", "antler", "hoof", "talon", "feather", "mane", "scale", "fin",
    "biscuit", "muffin", "pastry", "custard", "pudding", "toffee", "caramel", "waffle",
    "notebook", "pencil", "eraser", "stapler", "scissors", "clipboard", "folder", "binder",
    "trophy", "medal", "ribbon", "banner", "trophy", "plaque", "emblem", "badge",
    "saddle", "bridle", "stirrup", "harness", "wagon", "cart", "sleigh", "chariot",
    "kettle", "skillet", "cauldron", "ladle", "whisk", "grater", "colander", "sieve",
    "pebble", "shell", "coral", "anemone", "starfish", "seaweed", "driftwood", "sandbar",
    "crater", "moonrise", "sunset", "sunrise", "daybreak", "nightfall", "starfall", "moonbeam",
    "snowflake", "icicle", "blizzard", "flurry", "sleet", "slush", "thaw", "frostbite",
    "bramble", "nettle", "bracken", "heather", "gorse", "reed", "rush", "sedge",
    "vineyard", "cellar", "barrel", "cask", "bottle", "cork", "vintage", "harvest",
    "spire", "turret", "buttress", "rampart", "drawbridge", "moat", "keep", "dungeon",
    "lantern", "torchlight", "firelight", "starlight", "sunbeam", "glimmer", "sparkle", "radiance",
    "satchel", "knapsack", "pouch", "duffel", "trunk", "crate", "barrel", "hamper",
    "whistle", "bellows", "anvil", "forge", "hammer", "chisel", "tongs", "awl",
)


def _dedup(words: tuple[str, ...]) -> list[str]:
    """Order-preserving de-duplication (vocabulary is a *set* of distinct tokens)."""
    seen: set[str] = set()
    out: list[str] = []
    for w in words:
        if w not in seen:
            seen.add(w)
            out.append(w)
    return out


def build_topics(n_genres: int, latent_dim: int) -> list[list[str]]:
    """Return topic word-lists in the generator's canonical topic order.

    Order (matching ``gen_catalog.generate_keywords`` feature columns):
    ``latent_pos (latent_dim)`` then ``latent_neg (latent_dim)`` then ``genre (n_genres)``.
    Latent topics are disjoint contiguous slices of :data:`GENERAL_POOL`; genre topics are the
    first ``n_genres`` thematic banks in ``gen_catalog.GENRE_NAMES`` order. Deterministic and
    network-free.
    """
    from gen_catalog import GENRE_NAMES  # local import avoids a cycle at module load

    n_latent_topics = 2 * latent_dim
    pool = _dedup(GENERAL_POOL)
    chunk = len(pool) // n_latent_topics
    if chunk < 4:
        raise ValueError(
            f"GENERAL_POOL too small: {len(pool)} words / {n_latent_topics} latent topics"
        )
    latent_topics = [pool[t * chunk : (t + 1) * chunk] for t in range(n_latent_topics)]

    genre_topics: list[list[str]] = []
    for name in GENRE_NAMES[:n_genres]:
        bank = GENRE_WORDBANKS.get(name)
        if not bank:
            raise ValueError(f"no word bank for genre {name!r}")
        genre_topics.append(list(bank))

    return latent_topics + genre_topics


def vocabulary(n_genres: int, latent_dim: int) -> list[str]:
    """Flat, order-preserving, de-duplicated list of every token across all topics."""
    flat: list[str] = []
    for topic in build_topics(n_genres, latent_dim):
        flat.extend(topic)
    return _dedup(tuple(flat))
