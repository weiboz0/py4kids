from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from collections import Counter
from pathlib import Path

import yaml
from ci_local_text import ci_noncomment_lines, ci_text
from conftest import ROOT

from tools.aio.books import unit_dir
from tools.aio.checks.blueprint import check_blueprint
from tools.aio.checks.coverage import check_coverage
from tools.aio.checks.hygiene import check_hygiene
from tools.aio.checks.new_mocktest import scaffold_mocktest
from tools.aio.checks.overlap import REMEDY as OVERLAP_CORPUS_REMEDY
from tools.aio.checks.overlap import check_overlap
from tools.aio.checks.prereq import check_prereq
from tools.aio.model import load_syllabus, load_unit_manifests

BOOK1_ROOT = ROOT / "aio-ml"
BOOK2_ROOT = ROOT / "aio-dl"

PLAN019_PRE_CUTOVER_COMMIT = "4cc38946548f618ac131d246bfd4191d20e4e7d8"

NEW_CONCEPT_CLUSTERS = {
    "seaborn-programming": "python-scientific",
    "colab-markdown-solution-authoring": "competition-craft",
    "markdown-code-snippets": "competition-craft",
    "markdown-math-formulae": "competition-craft",
    "colab-coding-submission": "competition-craft",
    "cpu-and-gpu-round-boundary": "competition-craft",
    "conditional-probability": "probability-statistics",
    "bayes-rule": "probability-statistics",
    "hoeffding-inequality": "probability-statistics",
    "linear-regression-estimator-derivation": "ml-concepts",
    "ols-rank-identifiability-and-pseudoinverse": "ml-concepts",
    "pca-centered-covariance-eigenproblem-derivation": "ml-concepts",
    "numpy-pca-class-from-scratch": "ml-concepts",
    "pca-black-box-insufficiency": "ml-concepts",
    "positive-semidefinite-matrices": "linear-algebra",
    "kernel-validity": "linear-algebra",
    "convex-sets": "linear-algebra",
    "convex-functions": "calculus-multivar",
    "first-order-optimality": "calculus-multivar",
    "lagrangians": "calculus-multivar",
    "optimization-duality": "calculus-multivar",
}

EXPECTED_UNIT_SHAPES = {
    "F1-scientific-python": ([75, 90, 75, 70], 24, (310, 515, 50)),
    "C11-competition-craft": ([80, 85, 85, 85], 24, (335, 730, 55)),
    "F5-probability": ([80, 85, 85, 85, 80], 25, (415, 650, 55)),
    "C2-linear-models": ([85, 90, 85], 24, (260, 590, 55)),
    "C9-dimensionality-reduction": ([80, 90, 85, 85], 24, (340, 600, 60)),
    "F7-kernels-convex-optimization": ([85, 85, 85, 85], 20, (340, 640, 45)),
    "C8-neural-training": ([90, 90, 90, 90, 90], 24, (450, 1040, 60)),
    "C10-cnn-transfer": ([85, 85, 85, 90], 27, (345, 875, 60)),
}

PLAN016_C10_PROMOTED_CONCEPTS = (
    "colab-markdown-solution-authoring",
    "markdown-code-snippets",
    "markdown-math-formulae",
    "colab-coding-submission",
    "cpu-and-gpu-round-boundary",
)

F1_SEABORN_ARRAY_ONLY_FILES = {
    Path("lesson.ipynb"),
    Path("lessons/01-arrays-and-indexing.ipynb"),
    Path("lessons/02-broadcasting-and-vectorization.ipynb"),
    Path("lessons/03-randomness-and-plotting.ipynb"),
    Path("lessons/04-seaborn-with-arrays.ipynb"),
    Path("review.ipynb"),
    Path("practice/p22.ipynb"),
    Path("practice/p22_solution.ipynb"),
    Path("practice/p23.ipynb"),
    Path("practice/p23_solution.ipynb"),
    Path("practice/p24.ipynb"),
    Path("practice/p24_solution.ipynb"),
}

C9_PLAN016_CHANGED_NOTEBOOKS = (
    Path("lesson.ipynb"),
    Path("lessons/01-pca.ipynb"),
    Path("lessons/02-pca-covariance-and-numpy-class.ipynb"),
    Path("lessons/03-truncated-svd-practice.ipynb"),
    Path("lessons/04-maps-and-structure.ipynb"),
    Path("review.ipynb"),
    *(Path(f"practice/p{number:02d}.ipynb") for number in range(20, 25)),
)

PLAN017_NEW_CONCEPTS = {
    "softmax",
    "cross-entropy-loss",
    "manual-backpropagation",
    "autograd-training",
    "torch-optimizers",
    "trained-mlp",
    "batch-normalization",
    "dropout",
    "cnn-training",
}

PLAN019_B2_019_CONCEPTS = (
    "matrix-transpose",
    "query-key-value-attention",
    "scaled-dot-product-attention",
    "attention-mask",
    "causal-self-attention",
    "multi-head-attention",
    "sinusoidal-positional-encoding",
    "attention-complexity",
    "transformer-residual-layernorm",
    "position-wise-feed-forward",
    "transformer-block",
)

PLAN020_B2_020_CONCEPTS = (
    "embedding-model-training",
    "learned-token-embedding",
    "language-transformer",
    "causal-language-modeling",
    "masked-language-modeling",
    "nlp-pretraining-objectives",
    "nlp-fine-tuning-protocol",
    "transformer-nlp-task-design",
)

PLAN027_B2_022_CONCEPTS = (
    "multivariate-gaussian",
    "kl-divergence",
    "autoencoder",
    "gaussian-reparameterization",
    "variational-autoencoder",
)

PLAN028_B2_023_CONCEPTS = (
    "generative-adversarial-network",
    "denoising-diffusion-probabilistic-models",
    "stable-diffusion",
)

PLAN029_B2_024_CONCEPTS = (
    "gpu-colab-l4-workflow",
    "open-ended-experiment-design",
    "open-ended-model-evaluation",
    "semi-supervised-pseudo-labeling",
    "scientific-ml-inverse-problems",
    "mixture-parameter-regression",
)

PLAN021_B2_021_CONCEPTS = (
    "vision-transformers",
    "object-detection",
    "unet",
    "graph-neural-network-transformer-applications",
)

PLAN017_C11_CONCEPTS_USED = [
    "numpy-arrays",
    "array-indexing-slicing",
    "elementwise-ops",
    "broadcasting",
    "vectorization",
    "aggregation-axis",
    "random-seeding",
    "matplotlib-basics",
    "partial-derivatives",
    "gradient",
    "multivar-chain-rule",
    "gradient-descent",
    "learning-rate",
    "stochastic-gd",
    "loss-surfaces",
    "expectation",
    "variance",
    "perceptron",
    "activation-functions",
    "relu-activation",
    "mlp-architecture",
    "weight-init-variance",
    "overfitting",
    "l2-regularization",
    "python-inheritance",
    "torch-tensors",
    "nn-module",
    "requires-grad",
    "parameter-counting",
]

PLAN017_C11_PRACTICE_ROWS = [
    ("C8-p01", "A", "mc", "intro", ["softmax"], 15),
    ("C8-p02", "A", "mc", "intro", ["cross-entropy-loss"], 15),
    ("C8-p03", "A", "mc", "intro", ["manual-backpropagation"], 15),
    ("C8-p04", "B", "mc-normal-form", "intro", ["dropout"], 15),
    ("C8-p05", "A", "constrained-coding", "intro", ["softmax"], 25),
    ("C8-p06", "B", "constrained-coding", "intro", ["cross-entropy-loss"], 25),
    (
        "C8-p07",
        "A",
        "constrained-coding",
        "core",
        ["manual-backpropagation", "trained-mlp"],
        35,
    ),
    (
        "C8-p08",
        "A",
        "constrained-coding",
        "core",
        ["autograd-training", "torch-optimizers"],
        35,
    ),
    ("C8-p09", "A", "constrained-coding", "core", ["batch-normalization"], 35),
    ("C8-p10", "A", "constrained-coding", "core", ["dropout"], 35),
    (
        "C8-p11",
        "B",
        "proof",
        "core",
        ["softmax", "cross-entropy-loss"],
        40,
    ),
    ("C8-p12", "B", "proof", "core", ["manual-backpropagation"], 40),
    ("C8-p13", "B", "proof", "core", ["batch-normalization"], 40),
    (
        "C8-p14",
        "C",
        "integrative",
        "core",
        ["softmax", "cross-entropy-loss"],
        60,
    ),
    (
        "C8-p15",
        "C",
        "integrative",
        "core",
        ["manual-backpropagation", "trained-mlp"],
        60,
    ),
    (
        "C8-p16",
        "C",
        "integrative",
        "core",
        ["autograd-training", "torch-optimizers"],
        60,
    ),
    ("C8-p17", "C", "scenario", "core", ["trained-mlp"], 50),
    (
        "C8-p18",
        "C",
        "scenario",
        "core",
        ["batch-normalization", "dropout"],
        50,
    ),
    (
        "C8-p19",
        "C",
        "scenario",
        "advanced",
        ["autograd-training", "torch-optimizers"],
        50,
    ),
    (
        "C8-p20",
        "C",
        "scenario",
        "advanced",
        ["trained-mlp", "batch-normalization", "dropout"],
        50,
    ),
    (
        "C8-p21",
        "C",
        "challenge",
        "advanced",
        ["softmax", "cross-entropy-loss"],
        70,
    ),
    (
        "C8-p22",
        "C",
        "challenge",
        "advanced",
        ["manual-backpropagation"],
        70,
    ),
    (
        "C8-p23",
        "C",
        "challenge",
        "advanced",
        ["autograd-training", "torch-optimizers", "trained-mlp"],
        75,
    ),
    (
        "C8-p24",
        "C",
        "challenge",
        "advanced",
        ["torch-optimizers", "trained-mlp", "batch-normalization", "dropout"],
        75,
    ),
]

PLAN017_C7_PRESERVED_CONCEPTS = {
    "C10-p10": {"layer-freezing", "nn-module", "requires-grad", "parameter-counting"},
    "C10-p24": {"tensor-shape-tracing"},
    "C10-p26": {"convolution", "tensor-shape-tracing"},
    "C10-p27": {"layer-freezing", "requires-grad"},
}

PLAN018_C12_CONCEPTS = [
    "logistic-regression",
    "svm",
    "margin-and-hinge-loss",
    "decision-trees",
    "tree-split-criteria",
    "ensemble-learning",
    "bagging-and-boosting",
    "k-means",
    "lloyd-algorithm",
    "classical-model-comparison",
]

PLAN018_C12_PRACTICE_LEDGER = [
    ("C12-p01", "A", "mc", "intro", 20, 1),
    ("C12-p02", "A", "mc", "intro", 20, 2),
    ("C12-p03", "A", "mc", "intro", 20, 4),
    ("C12-p04", "A", "mc", "intro", 20, 5),
    ("C12-p05", "A", "mc-normal-form", "intro", 20, 6),
    ("C12-p06", "A", "constrained-coding", "intro", 55, 1),
    ("C12-p07", "B", "constrained-coding", "core", 55, 1),
    ("C12-p08", "B", "constrained-coding", "core", 55, 2),
    ("C12-p09", "B", "constrained-coding", "advanced", 55, 3),
    ("C12-p10", "A", "constrained-coding", "intro", 55, 4),
    ("C12-p11", "B", "constrained-coding", "core", 55, 4),
    ("C12-p12", "B", "constrained-coding", "core", 55, 5),
    ("C12-p13", "A", "constrained-coding", "intro", 55, 6),
    ("C12-p14", "B", "proof", "core", 45, 1),
    ("C12-p15", "C", "proof", "advanced", 45, 3),
    ("C12-p16", "B", "proof", "core", 45, 4),
    ("C12-p17", "B", "proof", "core", 45, 6),
    ("C12-p18", "C", "integrative", "advanced", 65, 2),
    ("C12-p19", "C", "integrative", "advanced", 65, 5),
    ("C12-p20", "C", "integrative", "core", 65, 6),
    ("C12-p21", "C", "integrative", "advanced", 65, 6),
    ("C12-p22", "C", "scenario", "intro", 45, 2),
    ("C12-p23", "C", "scenario", "core", 45, 4),
    ("C12-p24", "C", "scenario", "core", 45, 5),
    ("C12-p25", "C", "scenario", "core", 45, 6),
    ("C12-p26", "C", "challenge", "core", 50, 1),
    ("C12-p27", "C", "challenge", "advanced", 50, 3),
    ("C12-p28", "C", "challenge", "core", 50, 4),
    ("C12-p29", "C", "challenge", "core", 50, 5),
    ("C12-p30", "C", "challenge", "advanced", 50, 6),
]

PLAN018_C12_CONCEPT_COVERAGE = {
    "logistic-regression": [1, 6, 7, 14, 18, 21, 22, 26],
    "svm": [2, 8, 9, 15, 18, 21, 22, 27],
    "margin-and-hinge-loss": [2, 8, 15, 18, 27],
    "decision-trees": [3, 10, 11, 16, 19, 21, 23, 28],
    "tree-split-criteria": [3, 10, 16, 23, 28],
    "ensemble-learning": [4, 12, 19, 21, 24, 29],
    "bagging-and-boosting": [4, 12, 19, 24, 29],
    "k-means": [5, 13, 17, 20, 21, 25, 30],
    "lloyd-algorithm": [5, 13, 17, 20, 30],
    "classical-model-comparison": [18, 21, 22, 24, 25],
}


def _manifest(unit_id: str) -> dict[str, object]:
    return yaml.safe_load((unit_dir(BOOK1_ROOT, unit_id) / "manifest.yaml").read_text())


def _notebook_cell_source(relative_path: str, cell_id: str) -> str:
    notebook = json.loads((BOOK1_ROOT / relative_path).read_text())
    cell = next(cell for cell in notebook["cells"] if cell.get("id") == cell_id)
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else source


def _canonical_syllabus_yaml() -> dict[str, object]:
    text = (BOOK1_ROOT / "syllabus.md").read_text()
    fenced = re.search(
        r"<!-- syllabus-canonical -->\s*```yaml\n(.*?)\n```", text, re.DOTALL
    )
    assert fenced is not None
    return yaml.safe_load(fenced.group(1))


def _syllabus_narrative() -> str:
    text = (BOOK1_ROOT / "syllabus.md").read_text()
    canonical_end = re.search(
        r"<!-- syllabus-canonical -->\s*```yaml\n.*?\n```", text, re.DOTALL
    )
    assert canonical_end is not None
    return text[canonical_end.end() :]


def _narrative_section(narrative: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\n\n(.*?)(?=^## |\Z)",
        narrative,
        re.MULTILINE | re.DOTALL,
    )
    assert match is not None
    return match.group(1)


def seed_repo(root: Path, *, registered: bool = False) -> Path:
    content_root = root / "aio-ml" if registered else root
    (content_root / "mocktests").mkdir(parents=True)
    (content_root / "mocktests" / "blueprint.yaml").write_text(
        (BOOK1_ROOT / "mocktests" / "blueprint.yaml").read_text()
    )
    (content_root / "syllabus.md").write_text((BOOK1_ROOT / "syllabus.md").read_text())
    if registered:
        (root / "books.yaml").write_text(
            "books_version: 2\n"
            "books:\n"
            "  - {id: aio-ml, number: 4, root: aio-ml, depends_on: [], content_model: aio, aio_round: 1}\n"
        )
        for relative in (
            "curriculum/course-schedule.yaml",
            "curriculum/coverage-map.yaml",
            "curriculum/material-inventory.yaml",
            "curriculum/official-topics.yaml",
            "curriculum/source-manifest.yaml",
            "docs/course-structure.md",
            "units/.gitkeep",
            "reference/.gitkeep",
        ):
            path = content_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}\n" if path.suffix == ".yaml" else "fixture\n")
    return content_root


def test_plan016_c9_changed_markdown_has_no_decoded_tex_control_characters():
    unit = unit_dir(BOOK1_ROOT, "C9-dimensionality-reduction")
    forbidden = {"\t", "\f", "\r"}
    failures = []
    for relative in C9_PLAN016_CHANGED_NOTEBOOKS:
        notebook = json.loads((unit / relative).read_text())
        for cell_index, cell in enumerate(notebook["cells"]):
            if cell["cell_type"] != "markdown":
                continue
            source = "".join(cell.get("source", []))
            controls = sorted({repr(character) for character in source if character in forbidden})
            if controls:
                failures.append(f"{relative}: cell {cell_index}: {', '.join(controls)}")
    assert not failures, "decoded TeX control characters:\n" + "\n".join(failures)


def test_plan016_new_concepts_have_exact_clusters_and_single_owners():
    syllabus = load_syllabus(BOOK1_ROOT)

    assert len(NEW_CONCEPT_CLUSTERS) == 21
    assert {concept: syllabus.concepts.get(concept) for concept in NEW_CONCEPT_CLUSTERS} == (
        NEW_CONCEPT_CLUSTERS
    )

    syllabus_owner_counts = Counter(
        concept for unit in syllabus.units.values() for concept in unit.teaches
    )
    manifest_owner_counts = Counter(
        concept
        for manifest in load_unit_manifests(BOOK1_ROOT)
        for concept in manifest.concepts_taught
    )
    assert {concept: syllabus_owner_counts[concept] for concept in NEW_CONCEPT_CLUSTERS} == {
        concept: 1 for concept in NEW_CONCEPT_CLUSTERS
    }
    assert {concept: manifest_owner_counts[concept] for concept in NEW_CONCEPT_CLUSTERS} == {
        concept: 1 for concept in NEW_CONCEPT_CLUSTERS
    }


def test_plan018_manifests_have_exact_final_counts_and_minutes():
    for unit_id, (sessions, practice_count, minute_totals) in EXPECTED_UNIT_SHAPES.items():
        manifest = _manifest(unit_id)
        minutes = manifest["estimated_minutes"]
        assert minutes["lesson_sessions"] == sessions
        assert (minutes["lesson"], minutes["practice"], minutes["review"]) == minute_totals
        assert len(manifest["practice"]) == practice_count

    manifests = load_unit_manifests(BOOK1_ROOT)
    assert len(manifests) == 19
    assert sum(len(manifest.practice) for manifest in manifests) == 437
    assert sum(len(manifest.lesson_sessions or []) for manifest in manifests) == 69
    minute_totals = {
        field: sum(
            _manifest(manifest.unit_id)["estimated_minutes"][field]
            for manifest in manifests
        )
        for field in ("lesson", "practice", "review")
    }
    assert minute_totals == {"lesson": 5820, "practice": 11890, "review": 925}
    assert sum(minute_totals.values()) == 18635


def test_concepts_have_manifest_owners_for_live_b2_019():
    syllabus = load_syllabus(BOOK1_ROOT)
    book2_syllabus = load_syllabus(BOOK2_ROOT)
    manifests = load_unit_manifests(BOOK1_ROOT)
    book2_manifests = load_unit_manifests(BOOK2_ROOT)
    roadmap = yaml.safe_load((BOOK2_ROOT / "curriculum" / "coverage-map.yaml").read_text())
    syllabus_owner_counts = Counter(
        concept for unit in syllabus.units.values() for concept in unit.teaches
    )
    manifest_owner_counts = Counter(
        concept
        for manifest in manifests
        for concept in manifest.concepts_taught
    )
    manifest_owner_units = {
        concept: manifest.unit_id
        for manifest in manifests
        for concept in manifest.concepts_taught
    }
    planned_units = {row["id"]: row for row in roadmap["planned_units"]}
    knowledge_points = {row["id"]: row for row in roadmap["knowledge_points"]}
    nonlive_book2_units = set(book2_syllabus.units) - {
        manifest.unit_id for manifest in book2_manifests
    }

    assert set(syllabus.concepts) == set(syllabus_owner_counts)
    assert set(syllabus_owner_counts.values()) == {1}
    assert set(manifest_owner_counts) <= set(syllabus.concepts)
    assert set(manifest_owner_counts.values()) == {1}
    assert nonlive_book2_units == set()
    assert [manifest.unit_id for manifest in book2_manifests] == [
        "B2-019-attention-transformers",
        "B2-020-language-transformers",
        "B2-021-cross-modal-transformers-vision",
        "B2-022-probabilistic-latent-models",
        "B2-023-generative-models-diffusion",
        "B2-024-gpu-scientific-ml-capstone",
    ]
    assert book2_syllabus.units["B2-019-attention-transformers"].teaches == list(
        PLAN019_B2_019_CONCEPTS
    )
    assert set(book2_syllabus.concepts) == set(PLAN019_B2_019_CONCEPTS) | set(
        PLAN020_B2_020_CONCEPTS
    ) | set(PLAN021_B2_021_CONCEPTS) | set(PLAN027_B2_022_CONCEPTS) | set(
        PLAN028_B2_023_CONCEPTS
    ) | set(PLAN029_B2_024_CONCEPTS)
    assert (
        set(planned_units)
        - {
            "B2-019-attention-transformers",
            "B2-020-language-transformers",
            "B2-021-cross-modal-transformers-vision",
            "B2-022-probabilistic-latent-models",
            "B2-023-generative-models-diffusion",
            "B2-024-gpu-scientific-ml-capstone",
        }
    ).isdisjoint(book2_syllabus.units)

    for unit in syllabus.units.values():
        manifest_counts = {
            concept: manifest_owner_counts[concept] for concept in unit.teaches
        }
        assert manifest_counts == {concept: 1 for concept in unit.teaches}
        assert {
            concept: manifest_owner_units[concept] for concept in unit.teaches
        } == {concept: unit.id for concept in unit.teaches}

    for unit in book2_syllabus.units.values():
        assert re.fullmatch(r"B2-[0-9]{3}-.+", unit.id)
        planned = planned_units[unit.id]
        assert planned["layer"] == "round-2-extension"
        memberships = planned["knowledge_points"]
        assert memberships
        assert len(memberships) == len(set(memberships))
        for point_id in memberships:
            point = knowledge_points[point_id]
            assert point["destination"] == unit.id
            assert point["coverage"] == "covered"
            assert point["shipped_concepts"]
            assert all(
                evidence["lesson_anchors"]
                and evidence["practices"]
                and not evidence["assessments"]
                for evidence in point["evidence_by_modality"].values()
            )
            assert point["deficits"] == {"modalities_missing": []}
        assert {
            concept: sum(
                concept in manifest.concepts_taught for manifest in book2_manifests
            )
            for concept in unit.teaches
        } == {concept: 1 for concept in unit.teaches}

    assert {concept: syllabus_owner_counts[concept] for concept in PLAN017_NEW_CONCEPTS} == {
        concept: 1 for concept in PLAN017_NEW_CONCEPTS
    }
    assert {concept: manifest_owner_counts[concept] for concept in PLAN017_NEW_CONCEPTS} == {
        concept: 1 for concept in PLAN017_NEW_CONCEPTS
    }


def test_plan017_c11_manifest_is_the_exact_pinned_training_contract():
    manifest = _manifest("C8-neural-training")

    assert manifest["prereq_units"] == [
        "F3-multivar-calculus",
        "C3-gradient-descent",
        "C6-neural-networks",
        "C7-pytorch",
    ]
    assert manifest["concepts_taught"] == [
        "softmax",
        "cross-entropy-loss",
        "manual-backpropagation",
        "autograd-training",
        "torch-optimizers",
        "trained-mlp",
        "batch-normalization",
        "dropout",
    ]
    assert manifest["concepts_used"] == PLAN017_C11_CONCEPTS_USED
    assert manifest["estimated_minutes"] == {
        "lesson": 450,
        "lesson_sessions": [90, 90, 90, 90, 90],
        "practice": 1040,
        "review": 60,
    }
    actual_rows = [
        (
            row["id"],
            row["set"],
            row["type"],
            row["difficulty"],
            row["concepts"],
            row["path"],
            row["solution_path"],
            row["minutes"],
        )
        for row in manifest["practice"]
    ]
    expected_rows = [
        (
            problem_id,
            set_id,
            problem_type,
            difficulty,
            concepts,
            f"practice/p{index:02}.ipynb",
            f"practice/p{index:02}_solution.ipynb",
            minutes,
        )
        for index, (
            problem_id,
            set_id,
            problem_type,
            difficulty,
            concepts,
            minutes,
        ) in enumerate(PLAN017_C11_PRACTICE_ROWS, start=1)
    ]

    assert actual_rows == expected_rows
    assert all(type(row[-1]) is int and row[-1] > 0 for row in actual_rows)
    assert sum(row[-1] for row in actual_rows) == 1040


def test_plan018_c12_manifest_is_the_exact_double_length_contract():
    syllabus = _canonical_syllabus_yaml()
    units = {unit["id"]: unit for unit in syllabus["units"]}
    c12 = units["C12-classical-models"]
    manifest = _manifest("C12-classical-models")

    assert c12["length"] == "double"
    assert c12["prereqs"] == [
        "C1-ml-fundamentals",
        "C2-linear-models",
        "C3-gradient-descent",
        "C4-classical-ml-practice",
        "F7-kernels-convex-optimization",
    ]
    assert c12["teaches"] == PLAN018_C12_CONCEPTS
    assert manifest["prereq_units"] == c12["prereqs"]
    assert manifest["concepts_taught"] == PLAN018_C12_CONCEPTS
    assert manifest["concept_sessions"] == {
        "logistic-regression": 1,
        "svm": 2,
        "margin-and-hinge-loss": 2,
        "decision-trees": 4,
        "tree-split-criteria": 4,
        "ensemble-learning": 5,
        "bagging-and-boosting": 5,
        "k-means": 6,
        "lloyd-algorithm": 6,
        "classical-model-comparison": 2,
    }
    assert manifest["estimated_minutes"] == {
        "lesson": 540,
        "lesson_sessions": [90, 90, 90, 90, 90, 90],
        "practice": 1410,
        "review": 60,
    }

    actual_ledger = [
        (
            row["id"],
            row["set"],
            row["type"],
            row["difficulty"],
            row["minutes"],
            row["after_session"],
        )
        for row in manifest["practice"]
    ]
    assert actual_ledger == PLAN018_C12_PRACTICE_LEDGER
    assert [row["path"] for row in manifest["practice"]] == [
        f"practice/p{number:02}.ipynb" for number in range(1, 31)
    ]
    assert [row["solution_path"] for row in manifest["practice"]] == [
        f"practice/p{number:02}_solution.ipynb" for number in range(1, 31)
    ]
    assert [row["provenance"] for row in manifest["practice"]] == ["original"] * 30
    assert all("adapted-from" not in row for row in manifest["practice"])
    assert sum(row["minutes"] for row in manifest["practice"]) == 1410

    for concept, problem_numbers in PLAN018_C12_CONCEPT_COVERAGE.items():
        assert [
            row["id"]
            for row in manifest["practice"]
            if concept in row["concepts"]
        ] == [f"C12-p{number:02}" for number in problem_numbers]


def test_plan019_phase1_exact_live_corpus_counts_and_double_length_roster():
    manifests = load_unit_manifests(BOOK1_ROOT)
    syllabus = load_syllabus(BOOK1_ROOT)
    book2_syllabus = load_syllabus(BOOK2_ROOT)

    assert len(manifests) == 19
    assert len(syllabus.concepts) == 149
    assert len(book2_syllabus.concepts) == 37
    assert set(syllabus.concepts).isdisjoint(book2_syllabus.concepts)
    assert sum(len(manifest.practice) for manifest in manifests) == 437
    assert sum(len(manifest.lesson_sessions or []) for manifest in manifests) == 69
    minute_total = sum(
        sum(_manifest(manifest.unit_id)["estimated_minutes"][field] for field in (
            "lesson",
            "practice",
            "review",
        ))
        for manifest in manifests
    )
    assert minute_total == 18635

    double_units = {
        unit.id for unit in syllabus.units.values() if unit.length == "double"
    }
    assert double_units == {
        "F5-probability",
        "F6-svd-spectral",
        "C10-cnn-transfer",
        "C8-neural-training",
        "C12-classical-models",
    }
    standards = (ROOT / "aio-ml" / "docs" / "unit-standards.md").read_text()
    assert (
        "Double-length units (F5, F6, C8, C10, C12, B2-019, B2-020, B2-021, B2-022, B2-023, and B2-024) use 4–6 sessions."
        in standards
    )


def _plan019_commit_available(root: Path, commit: str) -> bool:
    return subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=root,
        capture_output=True,
        check=False,
    ).returncode == 0


def test_plan019_task3_book1_pdf_sources_match_the_pinned_r1_set() -> None:
    proc = subprocess.run(
        ["bash", "scripts/aio/build-pdf.sh", "--book", "aio-ml", "--list-inputs"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    listed = tuple(
        path.removeprefix("aio-ml/") for path in proc.stdout.splitlines() if path.strip()
    )
    # Plan 030 D4: build-pdf also reads the syllabus, every live unit's practice statements
    # (handouts), and the mock solutions. The r1-001 paper sources stay the pinned set.
    current = tuple(
        path for path in listed
        if path == "mocktests/r1-001/test.md"
        or (path.startswith("mocktests/r1-001/theory/") and path.endswith(".md"))
        or (path.startswith("mocktests/r1-001/problems/") and path.endswith(".ipynb"))
    )
    assert "docs/course-structure.md" in listed
    statements = {
        path for path in listed if path.startswith("units/") and "/practice/" in path
    }
    expected_statements = {
        path.relative_to(ROOT / "aio-ml").as_posix()
        for path in (ROOT / "aio-ml" / "units").glob("*/practice/p*.ipynb")
        if not path.name.endswith("_solution.ipynb")
    }
    assert statements == expected_statements
    assert not any(path.startswith("units/") and path.endswith("_solution.ipynb") for path in listed)
    assert {
        "mocktests/r1-001/solutions/answers.md",
        "mocktests/r1-001/rubric.md",
        "mocktests/r1-001/solutions/p05_solution.ipynb",
        "mocktests/r1-001/solutions/p09_solution.ipynb",
    } <= set(listed)
    if _plan019_commit_available(ROOT, PLAN019_PRE_CUTOVER_COMMIT):
        pinned = tuple(
            path
            for path in subprocess.run(
                [
                    "git",
                    "ls-tree",
                    "-r",
                    "--name-only",
                    PLAN019_PRE_CUTOVER_COMMIT,
                    "--",
                    "mocktests/r1-001",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.splitlines()
            if path == "mocktests/r1-001/test.md"
            or (path.startswith("mocktests/r1-001/theory/") and path.endswith(".md"))
            or (path.startswith("mocktests/r1-001/problems/") and path.endswith(".ipynb"))
        )
    else:
        pinned = current

    assert len(current) == 10
    assert current == pinned
    assert hashlib.sha256("\n".join(current).encode()).hexdigest() == (
        "b07a045f699ba6df93ad4429ae29926b99ade1083ecab005638f478aa614e6e4"
    )


def test_plan019_task3_r1_mock_solution_executes_from_book1_cwd(tmp_path: Path) -> None:
    output = tmp_path / "p09-executed.ipynb"
    env = {**os.environ, "AIO_BOOK_ROOT": str(BOOK1_ROOT)}
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "jupyter",
            "execute",
            "mocktests/r1-001/solutions/p09_solution.ipynb",
            "--output",
            str(output),
        ],
        cwd=BOOK1_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert output.is_file() and output.stat().st_size > 0


def test_plan017_c7_manifest_is_double_length_and_preserves_capstone_contracts():
    syllabus = _canonical_syllabus_yaml()
    syllabus_units = {unit["id"]: unit for unit in syllabus["units"]}
    syllabus_c7 = syllabus_units["C10-cnn-transfer"]
    manifest = _manifest("C10-cnn-transfer")

    assert syllabus_c7["length"] == "double"
    assert syllabus_c7["prereqs"] == ["C7-pytorch", "C8-neural-training"]
    assert "cnn-training" in syllabus_c7["teaches"]
    assert manifest["prereq_units"] == ["C7-pytorch", "C8-neural-training"]
    assert "cnn-training" in manifest["concepts_taught"]
    assert manifest["estimated_minutes"] == {
        "lesson": 345,
        "lesson_sessions": [85, 85, 85, 90],
        "practice": 875,
        "review": 60,
    }
    assert len(manifest["practice"]) == 27
    assert len({row["id"] for row in manifest["practice"]}) == 27
    assert len({row["path"] for row in manifest["practice"]}) == 27

    practices = {row["id"]: row for row in manifest["practice"]}
    assert {
        problem_id
        for problem_id, problem in practices.items()
        if "cnn-training" in problem["concepts"]
    } == set(PLAN017_C7_PRESERVED_CONCEPTS)
    for problem_id, preserved in PLAN017_C7_PRESERVED_CONCEPTS.items():
        assert preserved | {"cnn-training"} <= set(practices[problem_id]["concepts"])


def test_plan017_c11_p04_inverted_dropout_scaling_changes_the_answer():
    statement = _notebook_cell_source(
        "units/15-C8-neural-training/practice/p04.ipynb", "p04-m1"
    )

    assert "E[h_tilde_1^2] / E[h_tilde_2 + h_tilde_3]" in statement
    assert "16/15" in statement
    assert "4/5" in statement
    assert "derive both expectations from the Bernoulli keep mask and the 1/q scale" in statement
    assert "gcd(|a|,b) = 1" in statement
    assert "E[h_tilde_1] / E[h_tilde_2 + h_tilde_3]" not in statement


def test_plan017_c7_p26_pins_construction_to_reference_draw_order():
    statement = _notebook_cell_source(
        "units/17-C10-cnn-transfer/practice/p26.ipynb", "p26-00"
    )

    assert (
        "construct the convolution/ReLU stack in the listed spec order, then "
        "construct adaptive pool `(1,1)`, flatten, and the 3-class linear head last"
        in statement
    )
    assert "exactly 20 SGD steps (`lr=0.12`)" in statement


def test_plan017_c11_p10_replaces_effectively_zero_linspace_coordinate():
    setup = _notebook_cell_source(
        "units/15-C8-neural-training/practice/p10.ipynb", "p10-c2"
    )

    assert "x_p10[torch.abs(x_p10) < 1e-9] = 0.125" in setup
    assert "x_p10[x_p10 == 0]" not in setup


def test_plan017_c11_lessons_cover_lambda_rng_and_optimizer_state_contracts():
    lesson_03 = _notebook_cell_source(
        "units/15-C8-neural-training/lessons/03-numpy-mlp-training.ipynb",
        "c11s3015",
    )
    assert "$\\lambda/2$" in lesson_03
    assert "$\\lambda W$" in lesson_03
    assert "$lambda/2$" not in lesson_03
    assert "$lambda W$" not in lesson_03

    lesson_04_path = BOOK1_ROOT / "units/15-C8-neural-training/lessons/04-pytorch-autograd-and-optimizers.ipynb"
    lesson_04 = json.loads(lesson_04_path.read_text())
    cell_sources = {
        cell.get("id"): (
            "".join(cell.get("source", []))
            if isinstance(cell.get("source", []), list)
            else cell.get("source", "")
        )
        for cell in lesson_04["cells"]
    }
    all_source = "\n".join(cell_sources.values())

    assert "torch.Generator(device=\"cpu\")" in all_source
    assert "generator=data_generator" in all_source
    assert "local generator does not advance or reset the global generator" in all_source
    assert "torch.manual_seed(SEED)" in cell_sources["c11s4010"]
    assert "torch.use_deterministic_algorithms(True)" in all_source
    assert "raises instead of silently using only a nondeterministic implementation" in all_source
    assert "optimizer.state[first_parameter]" in all_source
    assert "adam_optimizer.state[adam_parameter]" in all_source
    assert '["step"]' in all_source
    assert "**Checkpoint 5C.**" in all_source
    assert "**5C.**" in cell_sources["c11s4016"]


def test_plan016_existing_unit_register_extensions_are_exact():
    expected = {
        "F1-scientific-python": {
            "F1-p22": ("A", "constrained-coding", "intro", ["seaborn-programming"]),
            "F1-p23": ("B", "constrained-coding", "core", ["seaborn-programming"]),
            "F1-p24": (
                "C",
                "integrative",
                "advanced",
                ["seaborn-programming", "random-seeding", "aggregation-axis"],
            ),
        },
        "F5-probability": {
            "F5-p20": ("A", "drill", "intro", ["conditional-probability"]),
            "F5-p21": (
                "B",
                "constrained-coding",
                "core",
                ["conditional-probability", "bayes-rule"],
            ),
            "F5-p22": (
                "B",
                "proof",
                "core",
                ["conditional-probability", "bayes-rule"],
            ),
            "F5-p23": ("B", "mc-normal-form", "core", ["hoeffding-inequality"]),
            "F5-p24": (
                "B",
                "constrained-coding",
                "core",
                ["hoeffding-inequality"],
            ),
            "F5-p25": (
                "C",
                "integrative",
                "advanced",
                [
                    "conditional-probability",
                    "bayes-rule",
                    "hoeffding-inequality",
                    "sampling-simulation",
                ],
            ),
        },
        "C2-linear-models": {
            "C2-p19": (
                "B",
                "proof",
                "core",
                ["linear-regression-estimator-derivation"],
            ),
            "C2-p20": (
                "B",
                "constrained-coding",
                "core",
                ["linear-regression-estimator-derivation"],
            ),
            "C2-p21": (
                "C",
                "integrative",
                "core",
                ["linear-regression-estimator-derivation"],
            ),
            "C2-p22": (
                "B",
                "proof",
                "advanced",
                ["ols-rank-identifiability-and-pseudoinverse"],
            ),
            "C2-p23": (
                "B",
                "constrained-coding",
                "core",
                ["ols-rank-identifiability-and-pseudoinverse"],
            ),
            "C2-p24": (
                "C",
                "challenge",
                "advanced",
                ["ols-rank-identifiability-and-pseudoinverse"],
            ),
        },
        "C9-dimensionality-reduction": {
            "C9-p20": (
                "B",
                "proof",
                "core",
                ["pca-centered-covariance-eigenproblem-derivation"],
            ),
            "C9-p21": (
                "B",
                "proof",
                "advanced",
                ["pca-centered-covariance-eigenproblem-derivation"],
            ),
            "C9-p22": (
                "B",
                "constrained-coding",
                "core",
                ["numpy-pca-class-from-scratch", "pca-black-box-insufficiency"],
            ),
            "C9-p23": (
                "C",
                "integrative",
                "advanced",
                [
                    "pca-centered-covariance-eigenproblem-derivation",
                    "numpy-pca-class-from-scratch",
                    "pca-black-box-insufficiency",
                ],
            ),
            "C9-p24": (
                "C",
                "challenge",
                "advanced",
                ["numpy-pca-class-from-scratch", "pca-black-box-insufficiency"],
            ),
        },
    }
    for unit_id, expected_problems in expected.items():
        actual = {
            problem["id"]: (
                problem["set"],
                problem["type"],
                problem["difficulty"],
                problem["concepts"],
            )
            for problem in _manifest(unit_id)["practice"]
            if problem["id"] in expected_problems
        }
        assert actual == expected_problems

    c10 = {
        problem["id"]: problem for problem in _manifest("C11-competition-craft")["practice"]
    }
    expected_c10_concepts = {
        "C11-p15": ["writeup-quality", *PLAN016_C10_PROMOTED_CONCEPTS],
        "C11-p17": [
            "writeup-quality",
            *PLAN016_C10_PROMOTED_CONCEPTS,
            "train-test-split",
            "f1-macro",
            "knn",
            "feature-scaling",
            "sklearn-pipelines",
        ],
        "C11-p18": [
            "writeup-quality",
            *PLAN016_C10_PROMOTED_CONCEPTS,
            "train-test-split",
            "class-imbalance",
            "accuracy-precision-recall",
            "f1-macro",
            "knn",
            "feature-scaling",
            "sklearn-pipelines",
        ],
    }
    for problem_id, expected_concepts in expected_c10_concepts.items():
        assert c10[problem_id]["concepts"] == expected_concepts
    for concept in PLAN016_C10_PROMOTED_CONCEPTS:
        assert [
            problem_id
            for problem_id, problem in c10.items()
            if concept in problem["concepts"]
        ] == ["C11-p15", "C11-p17", "C11-p18"]


def test_plan016_f1_register_rows_are_under_truthful_set_comments():
    text = (unit_dir(BOOK1_ROOT, "F1-scientific-python") / "manifest.yaml").read_text()
    set_a, after_a = text.split("# --- Set B: exam register ---", 1)
    set_b, set_c = after_a.split("# --- Set C: integration + challenge ---", 1)

    assert "id: F1-p22" in set_a
    assert "id: F1-p23" in set_b
    assert "id: F1-p24" in set_c


def test_f1_seaborn_array_only_boundary():
    f1_dir = unit_dir(BOOK1_ROOT, "F1-scientific-python")
    actual_files = {
        path.relative_to(f1_dir) for path in (f1_dir / "lessons").glob("*.ipynb")
    }
    actual_files.update(
        path.relative_to(f1_dir)
        for path in (f1_dir / "practice").glob("p2[234]*.ipynb")
    )
    actual_files.update({Path("lesson.ipynb"), Path("review.ipynb")})

    assert len(F1_SEABORN_ARRAY_ONLY_FILES) == 12
    assert actual_files == F1_SEABORN_ARRAY_ONLY_FILES
    assert all((f1_dir / relative).is_file() for relative in F1_SEABORN_ARRAY_ONLY_FILES)

    forbidden = {
        "import pandas": re.compile(r"\bimport\s+pandas\b", re.IGNORECASE),
        "from pandas": re.compile(r"\bfrom\s+pandas\b", re.IGNORECASE),
        "pd.": re.compile(r"\bpd\s*\."),
        "DataFrame": re.compile(r"\bdataframe\b", re.IGNORECASE),
    }
    for relative in sorted(F1_SEABORN_ARRAY_ONLY_FILES):
        text = (f1_dir / relative).read_text()
        hits = [name for name, pattern in forbidden.items() if pattern.search(text)]
        assert hits == [], f"{relative}: forbidden pandas surface {hits}"


def test_plan016_f7_manifest_has_exact_foundation_contract_and_register():
    syllabus = load_syllabus(BOOK1_ROOT)
    unit = syllabus.units["F7-kernels-convex-optimization"]
    assert unit.track == "foundation"
    assert unit.prereqs == [
        "F4-matrices",
        "F3-multivar-calculus",
        "F6-svd-spectral",
        "C3-gradient-descent",
    ]
    assert unit.teaches == [
        "positive-semidefinite-matrices",
        "kernel-validity",
        "convex-sets",
        "convex-functions",
        "first-order-optimality",
        "lagrangians",
        "optimization-duality",
    ]

    manifest = _manifest(unit.id)
    expected_rows = [
        ("F7-p01", "A", "mc", "intro", ["positive-semidefinite-matrices"]),
        ("F7-p02", "A", "mc", "intro", ["kernel-validity"]),
        ("F7-p03", "A", "mc", "intro", ["convex-sets"]),
        ("F7-p04", "B", "mc-normal-form", "core", ["convex-functions", "first-order-optimality"]),
        ("F7-p05", "A", "constrained-coding", "intro", ["positive-semidefinite-matrices"]),
        ("F7-p06", "B", "constrained-coding", "core", ["positive-semidefinite-matrices", "kernel-validity"]),
        ("F7-p07", "B", "constrained-coding", "core", ["positive-semidefinite-matrices", "kernel-validity"]),
        ("F7-p08", "A", "constrained-coding", "intro", ["convex-sets"]),
        ("F7-p09", "B", "constrained-coding", "core", ["convex-functions"]),
        ("F7-p10", "B", "constrained-coding", "advanced", ["lagrangians", "optimization-duality"]),
        ("F7-p11", "B", "proof", "core", ["positive-semidefinite-matrices", "kernel-validity"]),
        ("F7-p12", "B", "proof", "advanced", ["positive-semidefinite-matrices", "convex-functions", "first-order-optimality"]),
        ("F7-p13", "C", "integrative", "core", ["positive-semidefinite-matrices", "kernel-validity"]),
        ("F7-p14", "C", "integrative", "advanced", ["convex-sets", "convex-functions", "first-order-optimality", "lagrangians", "optimization-duality"]),
        ("F7-p15", "C", "scenario", "core", ["positive-semidefinite-matrices", "kernel-validity"]),
        ("F7-p16", "C", "scenario", "core", ["convex-functions", "first-order-optimality"]),
        ("F7-p17", "C", "challenge", "advanced", ["kernel-validity"]),
        ("F7-p18", "C", "challenge", "advanced", ["lagrangians", "optimization-duality"]),
        ("F7-p19", "A", "drill", "intro", ["convex-sets", "convex-functions"]),
        ("F7-p20", "B", "drill", "core", ["lagrangians", "optimization-duality"]),
    ]
    assert [
        (row["id"], row["set"], row["type"], row["difficulty"], row["concepts"])
        for row in manifest["practice"]
    ] == expected_rows


def test_plan018_coverage_map_preserves_prior_rows_and_retires_classical_placeholder():
    roadmap = yaml.safe_load((BOOK1_ROOT / "curriculum" / "coverage-map.yaml").read_text())
    planned = {unit["id"]: unit for unit in roadmap["planned_units"]}
    points = {point["id"]: point for point in roadmap["knowledge_points"]}

    assert "P015-R1-MATH-KERNEL-OPT" not in planned
    assert "P015-R1-CLASSICAL-BREADTH" not in planned
    book2_roadmap = yaml.safe_load(
        (BOOK2_ROOT / "curriculum" / "coverage-map.yaml").read_text()
    )
    book2_planned = {unit["id"]: unit for unit in book2_roadmap["planned_units"]}
    assert "aio-ml:C12-classical-models" in book2_planned[
        "B2-024-gpu-scientific-ml-capstone"
    ]["prerequisites"]
    assert points["seaborn-programming"]["depends_on"] == [
        "numpy-programming",
        "matplotlib-pyplot-programming",
    ]
    assert "array" in points["seaborn-programming"]["rationale"].lower()
    expected_mappings = {
        "valid-kernel-positive-definite-proof": [
            "positive-semidefinite-matrices",
            "kernel-validity",
        ],
        "convex-sets-functions-and-optimality": [
            "convex-sets",
            "convex-functions",
            "first-order-optimality",
        ],
        "constrained-optimization-lagrangian-duality": [
            "lagrangians",
            "optimization-duality",
        ],
    }
    for point_id, shipped_concepts in expected_mappings.items():
        point = points[point_id]
        assert point["coverage"] == "covered"
        assert point["evidence_by_modality"]
        assert all(
            evidence["lesson_anchors"]
            and evidence["practices"]
            and not evidence["assessments"]
            for evidence in point["evidence_by_modality"].values()
        )
        assert point["disposition"] == "keep"
        assert point["destination"] == "F7-kernels-convex-optimization"
        assert point["shipped_concepts"] == shipped_concepts
        assert point["deficits"] == {"modalities_missing": []}


def test_plan019_phase1_book1_narrative_order_and_book2_dependency_contract():
    syllabus = _canonical_syllabus_yaml()
    units = {unit["id"]: unit for unit in syllabus["units"]}
    book1_units = dict(units)
    assert units["F5-probability"]["length"] == "double"
    assert units["F6-svd-spectral"]["length"] == "double"
    assert units["C10-cnn-transfer"]["length"] == "double"
    assert units["C8-neural-training"]["length"] == "double"
    assert units["C12-classical-models"]["length"] == "double"
    narrative = _syllabus_narrative()
    foundation = _narrative_section(narrative, "Foundation track — rationale")
    core = _narrative_section(narrative, "Core track — rationale")
    normalized_foundation = " ".join(foundation.split())
    normalized_core = " ".join(core.split())
    assert "`F5-probability` is a double-length unit" in normalized_foundation
    assert "`F6-svd-spectral` is also a double-length unit" in normalized_foundation
    assert "the other double-length unit" not in normalized_foundation
    assert "`F7-kernels-convex-optimization`" in normalized_foundation
    assert (
        "`C2-linear-models` session 02 ships closed-form unregularized OLS fitting and the "
        "`linear-regression-estimator-derivation`, including rank, identifiability, and "
        "pseudoinverse behavior."
    ) in normalized_core
    assert (
        "Only iterative gradient-based fitting remains deferred to `C3-gradient-descent`."
    ) in normalized_core
    assert "Fitting itself is deferred to `C3-gradient-descent`" not in normalized_core
    engineering_ladder = (
        "`C6-neural-networks` → `C7-pytorch` → `C8-neural-training` → "
        "`C10-cnn-transfer`"
    )
    assert normalized_core.count(engineering_ladder) == 1

    order_section = _narrative_section(
        narrative, "Suggested order (one feasible topological sort)"
    )
    order = re.search(r"^F1 → .* → C12$", order_section, re.MULTILINE)
    assert order is not None
    by_short_id = {unit_id.split("-", 1)[0]: unit_id for unit_id in book1_units}
    ordered_unit_ids = [by_short_id[short_id] for short_id in order.group(0).split(" → ")]
    expected_order = [
        "F1-scientific-python",
        "F2-vectors",
        "F3-multivar-calculus",
        "F4-matrices",
        "F5-probability",
        "C1-ml-fundamentals",
        "C2-linear-models",
        "C3-gradient-descent",
        "C4-classical-ml-practice",
        "C5-embeddings",
        "C6-neural-networks",
        "F6-svd-spectral",
        "C7-pytorch",
        "F7-kernels-convex-optimization",
        "C8-neural-training",
        "C9-dimensionality-reduction",
        "C10-cnn-transfer",
        "C11-competition-craft",
        "C12-classical-models",
    ]
    assert ordered_unit_ids == expected_order
    assert set(ordered_unit_ids) == set(book1_units)
    assert len(ordered_unit_ids) == len(set(ordered_unit_ids)) == 19
    positions = {unit_id: index for index, unit_id in enumerate(ordered_unit_ids)}
    for unit_id in ordered_unit_ids:
        assert all(
            positions[prereq] < positions[unit_id]
            for prereq in book1_units[unit_id]["prereqs"]
        )
    book2 = load_syllabus(BOOK2_ROOT).units["B2-019-attention-transformers"]
    assert (
        book2.book,
        book2.round,
        book2.layer,
        book2.track,
    ) == (2, 2, "round-2-extension", "extension")
    assert book2.prereqs == [
        "aio-ml:C7-pytorch",
        "aio-ml:C10-cnn-transfer",
        "aio-ml:C5-embeddings",
        "aio-ml:C8-neural-training",
    ]
    book2_position = len(ordered_unit_ids)
    assert all(
        positions[prereq.removeprefix("aio-ml:")] < book2_position
        for prereq in book2.prereqs
    )

    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    # py4kids: usaaio's project dependencies are the `aio` dependency group (design 014).
    assert any(dependency.startswith("seaborn>=") for dependency in project["dependency-groups"]["aio"])
    assert re.search(r'^name = "seaborn"$', (ROOT / "uv.lock").read_text(), re.MULTILINE)
    standards = (ROOT / "aio-ml" / "docs" / "unit-standards.md").read_text()
    assert (
        "Double-length units (F5, F6, C8, C10, C12, B2-019, B2-020, B2-021, B2-022, B2-023, and B2-024) use 4–6 sessions."
        in standards
    )


def test_plan016_practice_coverage_is_green():
    report = check_coverage(BOOK1_ROOT)

    assert report.ok
    assert report.warnings == []
    assert report.errors == []


def test_ci_checks_other_than_plan016_pending_coverage_are_green():
    overlap = check_overlap(BOOK1_ROOT)
    reports = [
        check_prereq(BOOK1_ROOT),
        check_hygiene(BOOK1_ROOT),
        check_blueprint(BOOK1_ROOT),
        overlap,
    ]
    for report in reports:
        assert not report.errors
        assert report.ok
    corpus_present = any((BOOK1_ROOT / "reference").glob("*/index.yaml")) or any(
        (BOOK1_ROOT / "reference").glob("*/*.pdf")
    )
    if corpus_present:
        assert overlap.skipped is None
    else:
        assert overlap.skipped == OVERLAP_CORPUS_REMEDY


def test_cli_exit_codes(tmp_path):
    seed_repo(tmp_path, registered=True)
    ok = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.aio.cli",
            "--root",
            str(tmp_path),
            "--book",
            "aio-ml",
            "prereq-check",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert ok.returncode == 0
    fail_root = tmp_path / "fail"
    fail_book = seed_repo(fail_root, registered=True)
    manifest = fail_book / "mocktests" / "r1-001"
    manifest.mkdir(parents=True)
    manifest.joinpath("manifest.yaml").write_text(
        """
test: r1-001
blueprint_version: 1
duration_minutes: 180
total_points: 300
time_budget: {}
problems:
  - id: p01
    section: concept-block
    units: [F1-scientific-python]
    concepts: [vectors-and-norms]
    cluster: linear-algebra
    points: 1
    difficulty: intro
    type: theory
    answer_form: short
    provenance: original
    spec: x
    answer_key: x
"""
    )
    fail = subprocess.run(
        [sys.executable, "-m", "tools.aio.cli", "--root", str(fail_root), "--book", "aio-ml", "prereq-check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert fail.returncode == 1
    skip_root = tmp_path / "skip"
    skip_book = seed_repo(skip_root, registered=True)
    scaffold_mocktest(skip_book, "r1-001", "2026-08-15")
    skipped = subprocess.run(
        [sys.executable, "-m", "tools.aio.cli", "--root", str(skip_root), "--book", "aio-ml", "blueprint-check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert skipped.returncode == 3


def test_full_pipeline_on_synthetic_test(tmp_path):
    seed_repo(tmp_path)
    unit_dir = tmp_path / "units" / "01-F1-scientific-python"
    (unit_dir / "practice").mkdir(parents=True)
    for number in range(1, 4):
        (unit_dir / "practice" / f"p{number:02}.ipynb").write_text(
            '{"cells":[],"metadata":{},"nbformat":4,"nbformat_minor":5}'
        )
        (unit_dir / "practice" / f"p{number:02}_solution.ipynb").write_text(
            '{"cells":[{"cell_type":"code","source":"assert True",'
            '"metadata":{},"outputs":[],"execution_count":null}],'
            '"metadata":{},"nbformat":4,"nbformat_minor":5}'
        )
    (unit_dir / "manifest.yaml").write_text(
        """
unit: F1-scientific-python
concepts_taught: [numpy-arrays, array-indexing-slicing, broadcasting, vectorization, elementwise-ops, aggregation-axis, random-seeding, matplotlib-basics, seaborn-programming]
concepts_used: [variables-and-types]
prereq_units: []
practice:
  - id: p01
    concepts: [numpy-arrays, array-indexing-slicing, broadcasting, vectorization, elementwise-ops, aggregation-axis, random-seeding, matplotlib-basics, seaborn-programming]
    path: practice/p01.ipynb
    solution_path: practice/p01_solution.ipynb
  - id: p02
    concepts: [numpy-arrays, array-indexing-slicing, broadcasting, vectorization, elementwise-ops, aggregation-axis, random-seeding, matplotlib-basics, seaborn-programming]
    path: practice/p02.ipynb
    solution_path: practice/p02_solution.ipynb
  - id: p03
    concepts: [numpy-arrays, array-indexing-slicing, broadcasting, vectorization, elementwise-ops, aggregation-axis, random-seeding, matplotlib-basics, seaborn-programming]
    path: practice/p03.ipynb
    solution_path: practice/p03_solution.ipynb
"""
    )
    scaffold_mocktest(tmp_path, "r1-001", "2026-08-15")
    assert check_prereq(tmp_path).ok
    assert check_coverage(tmp_path).ok
    assert check_hygiene(tmp_path).ok
    report = check_blueprint(tmp_path)
    assert report.skipped
    assert report.warnings


def test_ci_flags_draft_manifest_loudly(tmp_path):
    book = seed_repo(tmp_path, registered=True)
    scaffold_mocktest(book, "r1-001", "2026-08-15")
    proc = subprocess.run(
        [sys.executable, "-m", "tools.aio.cli", "--root", str(tmp_path), "--book", "aio-ml", "blueprint-check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 3
    assert "DRAFT manifest" in proc.stdout


def test_scope_cli_is_registered_and_loader_errors_are_blocking(tmp_path):
    seed_repo(tmp_path, registered=True)

    proc = subprocess.run(
        [sys.executable, "-m", "tools.aio.cli", "--root", str(tmp_path), "--book", "aio-ml", "scope-check"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 1
    assert "source_schema_version" in proc.stderr
    assert "invalid choice" not in proc.stderr


def test_ci_checks_book2_material_inventory_freshness(tmp_path: Path) -> None:
    lines = ci_noncomment_lines()
    assert (
        'uv run --group aio python -m tools.aio.audit_curriculum --root "$aio_round2_root" --check'
        in lines
    )

    (tmp_path / "books.yaml").write_text((ROOT / "books.yaml").read_text())
    (tmp_path / "aio-ml").mkdir()
    copied_book2 = tmp_path / "aio-dl"
    shutil.copytree(ROOT / "aio-dl", copied_book2)
    lesson = (
        copied_book2
        / "units"
        / "B2-019-attention-transformers"
        / "lessons"
        / "01-query-key-value-and-scaled-dot-product.ipynb"
    )
    notebook = json.loads(lesson.read_text())
    notebook["cells"][0]["source"] = "# Stale inventory heading\n"
    lesson.write_text(json.dumps(notebook))

    proc = subprocess.run(
        [
            str(ROOT / ".venv" / "bin" / "python"),
            "-m",
            "tools.aio.audit_curriculum",
            "--root",
            str(copied_book2),
            "--check",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 1
    assert "ERROR material inventory stale" in proc.stderr


# --- plan aio-001 Phase E: the usaaio ci-local wiring test, rewritten against the py4kids
# --- scripts/ci-local.sh aio routing.

AIO_MODULE = "uv run --group aio python -m tools.aio."


def test_ci_local_wires_both_mutation_runners_and_generated_document_checks():
    lines = ci_noncomment_lines()

    audit = AIO_MODULE + 'audit_curriculum --root "$aio_round1_root" --check'
    aggregate = AIO_MODULE + 'render_curriculum_roadmap --root "$repo_root" --check'
    structure = AIO_MODULE + 'render_course_structure --root "$book_root" --check'
    training = AIO_MODULE + 'verify_training_mutations --repo-root "$repo_root"'
    classical = AIO_MODULE + 'verify_classical_mutations --repo-root "$repo_root"'
    for command in (audit, aggregate, structure, training, classical):
        assert lines.count(command) == 1
    assert lines.index(audit) < lines.index(aggregate) < lines.index(structure)
    assert lines.index(structure) < lines.index(training) < lines.index(classical)
    # The course-structure check runs for every registered aio root (usaaio: Book 1, then the rest).
    assert lines[lines.index(structure) - 1] == 'for book_root in "${AIO_ROOTS[@]}"; do'
    assert any(
        line.startswith('aio_tools --book "$book" "$c"') for line in lines
    )
    assert any("scope-check" in line for line in lines)


def test_ci_executes_book2_boundary_before_derived_and_preserves_r1_checks() -> None:
    lines = ci_noncomment_lines()
    checks = next(line for line in lines if line.startswith("for c in prereq-check"))

    assert "layer-boundary-check" in checks
    assert AIO_MODULE + 'render_course_structure --root "$book_root" --check' in lines
    build = lines.index('uv run --group aio bash scripts/aio/build-pdf.sh --book "$book" \\')
    assert lines[build + 1].startswith('|| { rc=$?; [[ $rc -eq 3 ]] || exit "$rc"; echo "SKIP: ')
    assert "prereq-check" in checks
    assert "coverage-check" in checks
    assert "blueprint-check" in checks
    assert 'find "$book_root/units" "$book_root/mocktests" -type f \\' in lines


def test_ci_executes_book2_schedule_check() -> None:
    lines = ci_noncomment_lines()
    checks = next(line for line in lines if line.startswith("for c in prereq-check"))
    assert "schedule-check" in checks
    assert any(
        line.startswith('aio_tools --book "$book" "$c"') for line in lines
    )


def test_ci_executes_attention_mutations() -> None:
    lines = ci_noncomment_lines()
    assert AIO_MODULE + 'verify_attention_mutations --repo-root "$repo_root"' in lines
    assert not any("SKIP attention mutations" in line for line in lines)


def test_ci_registry_probe_reports_noncanonical_roots_without_id_fallback(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    (repo / "round1").mkdir(parents=True)
    (repo / "advanced").mkdir()
    (repo / "books.yaml").write_text(
        "books_version: 2\nbooks:\n"
        "  - {id: aio-ml, number: 4, root: round1, depends_on: [], content_model: aio, aio_round: 1}\n"
        "  - {id: aio-dl, number: 4, root: advanced, depends_on: [aio-ml], content_model: aio,"
        " aio_round: 2}\n",
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            "bash", str(ROOT / "scripts/ci-local.sh"), "--registry-probe", "--root", str(repo),
        ],
        cwd=ROOT,
        env={**os.environ, "PATH": f"{Path.home() / '.local/bin'}:{os.environ['PATH']}"},
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    # The second column is aio_round (the adapter's BookSpec.number), not the series number 4.
    assert proc.stdout.splitlines() == [
        f"aio-ml\t1\t{repo / 'round1'}",
        f"aio-dl\t2\t{repo / 'advanced'}",
    ]
    script = ci_text()
    assert "$PWD/$book" not in script
    assert "--root aio-ml" not in script
    assert "--root aio-dl" not in script


def test_ci_routes_aio_exec_through_the_aio_ci_scope_and_filters_both_loops() -> None:
    """Plan aio-001 Phase E (design 014 D9): exec is change-routed; --all-books runs it in full."""
    lines = ci_noncomment_lines()
    assert (
        'aio_exec_routes=$(uv run --group aio python -m tools.aio.ci_scope --exec "${scope_args[@]}")'
        in lines
    )
    # A book with no route line runs in full (fail-safe), and both notebook loops are filtered.
    assert 'read -r aio_exec_mode aio_exec_rest <<< "${AIO_EXEC[$book]:-full}"' in lines
    assert lines.count('aio_in_exec_scope "$relative" || continue') == 2
    # Hygiene precedes the route decision, so it always runs.
    assert lines.index('aio_tools --book "$book" hygiene-check || { rc=$?; [[ $rc -eq 3 ]] || exit "$rc"; }') < (
        lines.index('read -r aio_exec_mode aio_exec_rest <<< "${AIO_EXEC[$book]:-full}"')
    )


def test_ci_aio_exec_scope_filter_matches_only_routed_folders(tmp_path: Path) -> None:
    text = ci_text()
    start = text.index("aio_in_exec_scope() {")
    function = text[start:text.index("\n}\n", start) + 3]
    probe = tmp_path / "probe.sh"
    probe.write_text(
        function
        + 'aio_exec_mode=scoped\n'
        + 'aio_exec_prefixes=("units/10-C5-embeddings/" "mocktests/r1-001/")\n'
        + 'for path in "$@"; do aio_in_exec_scope "$path" && echo "in $path" || echo "out $path"; done\n'
        + 'aio_exec_mode=full\naio_exec_prefixes=()\naio_in_exec_scope units/x/y.ipynb && echo "full in"\n',
        encoding="utf-8",
    )
    proc = subprocess.run(
        ["bash", str(probe), "units/10-C5-embeddings/practice/p01_solution.ipynb",
         "units/10-C5-embeddings-extra/lesson.ipynb", "mocktests/r1-001/solutions/p05_solution.ipynb",
         "mocktests/r1-0010/solutions/p01_solution.ipynb", "units/11-C6-x/lesson.ipynb"],
        capture_output=True, text=True, check=True,
    )
    assert proc.stdout.splitlines() == [
        "in units/10-C5-embeddings/practice/p01_solution.ipynb",
        "out units/10-C5-embeddings-extra/lesson.ipynb",
        "in mocktests/r1-001/solutions/p05_solution.ipynb",
        "out mocktests/r1-0010/solutions/p01_solution.ipynb",
        "out units/11-C6-x/lesson.ipynb",
        "full in",
    ]

