"""Named check registry used by the command-line interface."""

from tools.acsl import acsl_findings
from tools.concept_scan import concept_scan_findings
from tools.curriculum import coverage_findings, prereq_findings
from tools.fake_turtle import turtle_findings
from tools.judge import judge_findings
from tools.notebooks import (
    cell_lint_findings,
    exec_lessons_findings,
    exec_solutions_findings,
    exercise_structure_findings,
    hygiene_findings,
    manifest_findings,
    milestone_hygiene_findings,
    noexec_findings,
    structure_findings,
)
from tools.patterns import pattern_marker_findings, technique_spiral_findings
from tools.patterns_doc import patterns_doc_findings
from tools.source_policy import source_policy_findings
from tools.turtle_real import turtle_real_findings


def stretch_findings(root, book, unit=None):
    return exercise_structure_findings(root, book, unit, stretch_only=True)


CHECKS = {
    "manifest-check": manifest_findings,
    "hygiene-check": hygiene_findings,
    "structure-check": structure_findings,
    "noexec-check": noexec_findings,
    "exec-solutions": exec_solutions_findings,
    "exec-lessons": exec_lessons_findings,
    "milestone-check": milestone_hygiene_findings,
    "cell-lint": cell_lint_findings,
    "turtle-check": turtle_findings,
    "turtle-real-check": turtle_real_findings,
    "prereq-check": prereq_findings,
    "coverage-check": coverage_findings,
    "concept-scan": concept_scan_findings,
    "technique-spiral": technique_spiral_findings,
    "pattern-marker": pattern_marker_findings,
    "patterns-doc-check": patterns_doc_findings,
    "stretch-check": stretch_findings,
    "judge-check": judge_findings,
    "source-policy": source_policy_findings,
    "acsl-check": acsl_findings,
}

UNIT_ONLY_CHECKS = {"noexec-check", "stretch-check", "exec-lessons", "turtle-check", "turtle-real-check"}
