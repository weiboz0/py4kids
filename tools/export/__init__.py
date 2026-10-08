"""The learning-website content export (design 012 part A; plan 101).

`py4kids-tools export` turns each `site: true` book into a versioned, schema-checked JSON bundle.
The bundle schema lives in `schema/bundle.schema.json`; its `$id` ends in SCHEMA_VERSION.
"""

SCHEMA_VERSION = "1.1.0"  # 1.1.0: check.cpu_ms, answer_figures (plan 104 C)
