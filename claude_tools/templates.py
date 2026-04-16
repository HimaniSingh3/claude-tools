from __future__ import annotations

from dataclasses import dataclass
from string import Formatter
from typing import Any


@dataclass(frozen=True, slots=True)
class TemplateSpec:
    name: str
    description: str
    body: str

    @property
    def variables(self) -> list[str]:
        fields: list[str] = []
        for _, field_name, _, _ in Formatter().parse(self.body):
            if field_name and field_name not in fields:
                fields.append(field_name)
        return fields


TEMPLATES: dict[str, TemplateSpec] = {
    "code_review": TemplateSpec(
        name="code_review",
        description="Review code for correctness, clarity, edge cases, and improvements.",
        body=(
            "Review the following code. Focus on correctness, readability, edge cases, performance, "
            "and concrete improvements.\n\nCode:\n{code}"
        ),
    ),
    "bug_fix": TemplateSpec(
        name="bug_fix",
        description="Find likely root cause and suggest a fix.",
        body=(
            "You are helping debug an issue. Explain the likely root cause, the evidence for it, "
            "and a concrete fix.\n\nProblem:\n{problem}\n\nRelevant code or logs:\n{context}"
        ),
    ),
    "pr_summary": TemplateSpec(
        name="pr_summary",
        description="Write a pull request summary with changes, impact, and testing.",
        body=(
            "Write a concise pull request summary with sections for changes, impact, risks, and testing."
            "\n\nDiff or notes:\n{diff}"
        ),
    ),
    "meeting_notes": TemplateSpec(
        name="meeting_notes",
        description="Turn rough notes into clean decisions and action items.",
        body=(
            "Turn the following raw notes into clean meeting notes with sections for summary, decisions, "
            "action items, and open questions.\n\nNotes:\n{notes}"
        ),
    ),
    "file_summary": TemplateSpec(
        name="file_summary",
        description="Summarize a file and highlight key points.",
        body=(
            "Summarize the following file for an engineer. Include purpose, key details, risks, and "
            "recommended next steps.\n\nFile path: {file_path}\n\nContent:\n{content}"
        ),
    ),
    "error_explain": TemplateSpec(
        name="error_explain",
        description="Explain logs or stack traces and suggest fixes.",
        body=(
            "Explain the following error or log output. Identify the most likely cause, useful clues, "
            "and step-by-step fixes.\n\nSource: {source}\n\nError details:\n{error}"
        ),
    ),
    "diff_review": TemplateSpec(
        name="diff_review",
        description="Review a git diff for bugs, regressions, and missing tests.",
        body=(
            "Review this diff like a senior engineer. Look for correctness problems, regressions, edge "
            "cases, maintainability issues, and missing tests.\n\nDiff:\n{diff}"
        ),
    ),
    "test_generation": TemplateSpec(
        name="test_generation",
        description="Generate a test plan or tests for code.",
        body=(
            "Generate high-value test cases for the following code. Prioritize edge cases, error paths, "
            "and regressions.\n\nCode:\n{code}"
        ),
    ),
    "commit_message": TemplateSpec(
        name="commit_message",
        description="Generate a clean commit message from diff or notes.",
        body=(
            "Write a concise conventional commit message and a short body based on the following changes."
            "\n\nChanges:\n{changes}"
        ),
    ),
}


class TemplateError(ValueError):
    """Raised when template usage is invalid."""


class _SafeDict(dict[str, Any]):
    def __missing__(self, key: str) -> str:
        raise TemplateError(f"Missing required template variable: {key}")


def list_templates() -> list[TemplateSpec]:
    return [TEMPLATES[name] for name in sorted(TEMPLATES)]


def get_template(name: str) -> TemplateSpec:
    try:
        return TEMPLATES[name]
    except KeyError as exc:
        available = ", ".join(sorted(TEMPLATES))
        raise TemplateError(f"Unknown template '{name}'. Available templates: {available}") from exc


def required_variables(name: str) -> list[str]:
    return get_template(name).variables


def render_template(name: str, variables: dict[str, Any]) -> str:
    template = get_template(name)
    return template.body.format_map(_SafeDict(variables))
