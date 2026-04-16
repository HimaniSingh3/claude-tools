from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.table import Table

from claude_tools import __version__
from claude_tools.batch import BatchResult, load_batch_jobs, dump_batch_results, BatchError
from claude_tools.client import ClaudeToolsClient, ClientError
from claude_tools.config import ConfigError, get_settings, redact_api_key
from claude_tools.io_utils import InputError, read_stdin_text, read_text_file, write_text_file
from claude_tools.templates import TemplateError, get_template, list_templates, render_template

app = typer.Typer(help="Practical CLI for Claude workflows.", no_args_is_help=True)
console = Console()


@app.command()
def version() -> None:
    """Show the installed version."""
    console.print(__version__)


@app.command()
def config() -> None:
    """Show resolved configuration with a redacted API key."""
    settings = get_settings(require_api_key=False)
    table = Table(title="Resolved Configuration")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("ANTHROPIC_API_KEY", redact_api_key(settings.api_key))
    table.add_row("CLAUDE_MODEL", settings.model)
    table.add_row("CLAUDE_MAX_TOKENS", str(settings.max_tokens))
    table.add_row("CLAUDE_SYSTEM_PROMPT", settings.system_prompt)
    console.print(table)


@app.command()
def templates(
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Show descriptions and variables.")] = False,
) -> None:
    """List built-in templates."""
    if not verbose:
        for template in list_templates():
            console.print(f"- {template.name}")
        return

    table = Table(title="Built-in Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Variables", style="magenta")
    table.add_column("Description")
    for template in list_templates():
        variables = ", ".join(template.variables) or "-"
        table.add_row(template.name, variables, template.description)
    console.print(table)


@app.command()
def render(
    template: Annotated[str, typer.Argument(help="Template name to render.")],
    var: Annotated[
        list[str], typer.Option(help="Template variable in key=value form. Can be passed multiple times.")
    ] = [],
) -> None:
    """Render a template locally without calling the API."""
    final_prompt = render_template(template, _parse_key_value_pairs(var))
    console.print(Panel(final_prompt, title=f"Template: {template}", expand=False))


@app.command()
def ask(
    prompt: Annotated[str | None, typer.Argument(help="Prompt text.")] = None,
    template: Annotated[str | None, typer.Option(help="Template name to render before sending.")] = None,
    var: Annotated[
        list[str], typer.Option(help="Template variable in key=value form. Can be passed multiple times.")
    ] = [],
    stdin: Annotated[bool, typer.Option(help="Read prompt text from stdin.")] = False,
    system: Annotated[str | None, typer.Option(help="Override the system prompt.")] = None,
    model: Annotated[str | None, typer.Option(help="Override the configured model.")] = None,
    max_tokens: Annotated[int | None, typer.Option(help="Override max tokens.")] = None,
    temperature: Annotated[float | None, typer.Option(help="Optional temperature value.")] = None,
    dry_run: Annotated[bool, typer.Option(help="Render the prompt but do not call the API.")] = False,
    output_json: Annotated[bool, typer.Option("--json", help="Print response metadata as JSON.")] = False,
    save: Annotated[Path | None, typer.Option(help="Write the final response text to a file.")] = None,
) -> None:
    """Send a prompt to Claude."""
    final_prompt = _build_prompt(prompt=prompt, template=template, variables=var, stdin=stdin)

    if dry_run:
        console.print(Panel(final_prompt, title="Rendered Prompt", expand=False))
        return

    settings = get_settings()
    response = ClaudeToolsClient(settings).ask(
        final_prompt,
        system_prompt=system,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    if save:
        write_text_file(save, response.text)
        console.print(f"Saved response to {save}")

    if output_json:
        payload = response.to_dict() | {"prompt": final_prompt}
        console.print(JSON.from_data(payload))
        return

    console.print(Panel(response.text or "[empty response]", title="Claude Response", expand=False))


@app.command("summarize-file")
def summarize_file(
    path: Annotated[Path, typer.Argument(help="File to summarize.")],
    instructions: Annotated[
        str | None, typer.Option(help="Optional extra instruction appended to the summary prompt.")
    ] = None,
    dry_run: Annotated[bool, typer.Option(help="Render the prompt but do not call the API.")] = False,
    save: Annotated[Path | None, typer.Option(help="Write the response to a file.")] = None,
) -> None:
    """Summarize a local file using the file_summary template."""
    content = read_text_file(path)
    prompt = render_template(
        "file_summary",
        {
            "file_path": str(path),
            "content": content,
        },
    )
    if instructions:
        prompt = f"{prompt}\n\nExtra instructions:\n{instructions}"
    _run_single_prompt(prompt, dry_run=dry_run, save=save)


@app.command("explain-error")
def explain_error(
    source: Annotated[
        Path | None,
        typer.Argument(help="Path to a log file or error text file. Omit when using --stdin."),
    ] = None,
    stdin: Annotated[bool, typer.Option(help="Read error details from stdin.")] = False,
    dry_run: Annotated[bool, typer.Option(help="Render the prompt but do not call the API.")] = False,
    save: Annotated[Path | None, typer.Option(help="Write the response to a file.")] = None,
) -> None:
    """Explain an error log or stack trace."""
    text, source_name = _read_text_input(source, stdin=stdin, fallback_label="stdin")
    prompt = render_template(
        "error_explain",
        {
            "source": source_name,
            "error": text,
        },
    )
    _run_single_prompt(prompt, dry_run=dry_run, save=save)


@app.command("review-diff")
def review_diff(
    source: Annotated[
        Path | None,
        typer.Argument(help="Path to a diff file. Omit when piping a diff with --stdin."),
    ] = None,
    stdin: Annotated[bool, typer.Option(help="Read diff text from stdin.")] = False,
    dry_run: Annotated[bool, typer.Option(help="Render the prompt but do not call the API.")] = False,
    save: Annotated[Path | None, typer.Option(help="Write the response to a file.")] = None,
) -> None:
    """Review a git diff."""
    text, _ = _read_text_input(source, stdin=stdin, fallback_label="stdin")
    prompt = render_template("diff_review", {"diff": text})
    _run_single_prompt(prompt, dry_run=dry_run, save=save)


@app.command()
def batch(
    jobs_file: Annotated[Path, typer.Argument(help="Path to a JSON or JSONL batch file.")],
    output: Annotated[Path | None, typer.Option(help="Write batch results to a JSON file.")] = None,
    dry_run: Annotated[bool, typer.Option(help="Render prompts without calling the API.")] = False,
    fail_fast: Annotated[bool, typer.Option(help="Stop on the first failed job.")] = False,
) -> None:
    """Run prompts from a JSON or JSONL batch file."""
    jobs = load_batch_jobs(jobs_file)
    settings = None if dry_run else get_settings()
    client = None if dry_run else ClaudeToolsClient(settings)

    results: list[BatchResult] = []
    table = Table(title=f"Batch Run: {jobs_file.name}")
    table.add_column("Job")
    table.add_column("Status")
    table.add_column("Preview")

    for job in jobs:
        try:
            final_prompt = _build_prompt(
                prompt=job.prompt,
                template=job.template,
                variables=[f"{key}={value}" for key, value in job.variables.items()],
                stdin=False,
            )
            if dry_run:
                response_text = final_prompt
                status = "dry-run"
            else:
                assert client is not None
                response_text = client.ask(final_prompt, system_prompt=job.system).text
                status = "ok"

            results.append(
                BatchResult(
                    name=job.name,
                    prompt=final_prompt,
                    response=response_text,
                    template=job.template,
                    variables=job.variables,
                    system=job.system,
                    metadata=job.metadata,
                )
            )
            preview = response_text.replace("\n", " ")[:60]
            table.add_row(job.name, status, preview)
        except Exception as exc:  # noqa: BLE001
            table.add_row(job.name, "error", str(exc)[:60])
            if fail_fast:
                raise

    if output:
        dump_batch_results(results, output)
        console.print(f"Saved batch results to {output}")

    console.print(table)


@app.callback()
def main() -> None:
    """Claude tools command group."""


@app.command("template-info")
def template_info(
    name: Annotated[str, typer.Argument(help="Template name to inspect.")],
) -> None:
    """Show one template's description and variables."""
    template = get_template(name)
    table = Table(title=f"Template: {template.name}")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Description", template.description)
    table.add_row("Variables", ", ".join(template.variables) or "-")
    table.add_row("Body", template.body)
    console.print(table)


def _run_single_prompt(prompt: str, dry_run: bool, save: Path | None) -> None:
    if dry_run:
        console.print(Panel(prompt, title="Rendered Prompt", expand=False))
        return

    settings = get_settings()
    response = ClaudeToolsClient(settings).ask(prompt)
    if save:
        write_text_file(save, response.text)
        console.print(f"Saved response to {save}")
    console.print(Panel(response.text or "[empty response]", title="Claude Response", expand=False))


def _build_prompt(
    prompt: str | None,
    template: str | None,
    variables: list[str],
    stdin: bool,
) -> str:
    input_prompt = prompt

    if stdin:
        piped = read_stdin_text()
        if piped:
            input_prompt = piped

    if template:
        rendered = render_template(template, _parse_key_value_pairs(variables))
        if input_prompt:
            return f"{rendered}\n\nAdditional user input:\n{input_prompt}"
        return rendered

    if not input_prompt:
        raise ValueError("Provide a prompt, use --stdin, or choose --template.")

    return input_prompt


def _parse_key_value_pairs(items: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid --var value '{item}'. Expected key=value.")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError("Template variable key cannot be empty.")
        parsed[key] = value
    return parsed


def _read_text_input(
    source: Path | None,
    *,
    stdin: bool,
    fallback_label: str,
) -> tuple[str, str]:
    if stdin:
        text = read_stdin_text()
        if text:
            return text, fallback_label
    if source is not None:
        return read_text_file(source), str(source)
    raise ValueError("Provide a file path or use --stdin.")


@app.command("save-example-batch")
def save_example_batch(
    path: Annotated[Path, typer.Argument(help="Where to write the example JSON batch file.")],
) -> None:
    """Write an example batch file."""
    example: list[dict[str, Any]] = [
        {
            "name": "readme-summary",
            "prompt": "Summarize this project in 5 bullets.",
        },
        {
            "name": "review-snippet",
            "template": "code_review",
            "variables": {
                "code": "def add(a, b): return a + b",
            },
        },
    ]
    write_text_file(path, json.dumps(example, indent=2))
    console.print(f"Wrote example batch file to {path}")


if __name__ == "__main__":
    try:
        app()
    except (ConfigError, TemplateError, ClientError, InputError, BatchError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1) from exc
