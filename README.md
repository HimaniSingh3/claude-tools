<div align="center">

# Claude Tools

<p>
  <strong>A practical, developer-friendly CLI for running Claude workflows from your terminal.</strong>
</p>

<p>
  Turn repeatable prompting into reusable commands for code review, diff analysis, file summaries, error explanation, and batch jobs.
</p>

<p>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/interface-CLI-6f42c1.svg" alt="CLI" />
  <img src="https://img.shields.io/badge/anthropic-Claude-orange.svg" alt="Anthropic Claude" />
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License" />
</p>

</div>

---

## Overview

**Claude Tools** is a clean Python CLI that helps you use Claude for common engineering and writing workflows without rewriting prompts every time.

It gives you:

- a simple terminal interface
- reusable prompt templates
- environment-based configuration
- file and stdin support
- JSON / JSONL batch execution
- a clean base for adding more Claude-powered commands later

This project is intentionally lightweight: no web app, no database, no heavy framework. Just a solid CLI that is easy to install, extend, and ship.

---

## Features

<table>
  <tr>
    <td><strong>Terminal-first workflow</strong></td>
    <td>Run Claude directly from your shell using a small, focused CLI.</td>
  </tr>
  <tr>
    <td><strong>Reusable templates</strong></td>
    <td>Built-in prompt templates for code review, PR summaries, diff review, test generation, commit messages, meeting notes, file summaries, and error analysis.</td>
  </tr>
  <tr>
    <td><strong>File + stdin support</strong></td>
    <td>Pass prompts directly, read piped input, or analyze local text files.</td>
  </tr>
  <tr>
    <td><strong>Batch processing</strong></td>
    <td>Run multiple jobs from <code>.json</code> or <code>.jsonl</code> files.</td>
  </tr>
  <tr>
    <td><strong>Configurable defaults</strong></td>
    <td>Use <code>.env</code> and environment variables for API key, model, token limits, and system prompt.</td>
  </tr>
  <tr>
    <td><strong>Developer-friendly output</strong></td>
    <td>Rich terminal output, optional JSON responses, and file export support.</td>
  </tr>
  <tr>
    <td><strong>Production-ready project scaffold</strong></td>
    <td>Includes packaging, tests, and GitHub Actions CI.</td>
  </tr>
</table>

---

## Built-in Commands

| Command | Purpose |
|---|---|
| `claude-tools version` | Show installed version |
| `claude-tools config` | Show resolved configuration with redacted API key |
| `claude-tools templates` | List available templates |
| `claude-tools templates -v` | Show templates with descriptions and variables |
| `claude-tools template-info <name>` | Show one template in detail |
| `claude-tools render <template>` | Render a template locally without calling the API |
| `claude-tools ask ...` | Send a direct prompt or template-based prompt to Claude |
| `claude-tools summarize-file <path>` | Summarize a local text file |
| `claude-tools explain-error <path>` | Explain an error log or stack trace |
| `claude-tools review-diff <path>` | Review a Git diff |
| `claude-tools batch <jobs.json>` | Run multiple prompts from JSON or JSONL |
| `claude-tools save-example-batch <path>` | Generate a sample batch file |

---

## Built-in Templates

| Template | What it does |
|---|---|
| `code_review` | Reviews code for bugs, clarity, maintainability, and test gaps |
| `pr_summary` | Summarizes a pull request or change set |
| `meeting_notes` | Converts rough notes into structured meeting notes |
| `file_summary` | Summarizes a file with key risks and next steps |
| `error_explain` | Explains stack traces or logs and suggests fixes |
| `diff_review` | Reviews a Git diff like a senior engineer |
| `test_generation` | Generates high-value test ideas |
| `commit_message` | Produces a concise conventional commit message |

---

## Installation

### 1) Clone the repository

```bash
git clone https://github.com/HimaniSingh3/claude-tools.git
cd claude-tools
```

### 2) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3) Install the package

```bash
pip install -e .
```

For development tools as well:

```bash
pip install -e .[dev]
```

---

## Configuration

Create a local environment file from the example:

```bash
cp .env.example .env
```

Set your Anthropic API key:

```env
ANTHROPIC_API_KEY=your_api_key_here
CLAUDE_MODEL=claude-sonnet-4-6
CLAUDE_MAX_TOKENS=1200
CLAUDE_SYSTEM_PROMPT=You are a concise and practical assistant.
```

### Supported environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Yes for API calls | — | Your Anthropic API key |
| `CLAUDE_MODEL` | No | `claude-sonnet-4-6` | Default Claude model |
| `CLAUDE_MAX_TOKENS` | No | `1200` | Default max output tokens |
| `CLAUDE_SYSTEM_PROMPT` | No | `You are a concise and practical assistant.` | Default system prompt |

Check the resolved configuration anytime:

```bash
claude-tools config
```

---

## Quick Start

### Ask Claude directly

```bash
claude-tools ask "Explain Python context managers with a simple example"
```

### Render a template without calling the API

```bash
claude-tools render code_review --var code="def add(a,b): return a+b"
```

### Use a template and send it to Claude

```bash
claude-tools ask --template code_review --var code="def add(a,b): return a+b"
```

### Read prompt content from stdin

```bash
echo "Summarize the pros and cons of using SQLite in desktop apps" | claude-tools ask --stdin
```

### Save the response to a file

```bash
claude-tools ask "Draft a release note for version 1.0.0" --save RELEASE_NOTES.md
```

### Output machine-readable JSON

```bash
claude-tools ask "List 3 API design mistakes" --json
```

---

## Workflow Examples

### Summarize a local file

```bash
claude-tools summarize-file README.md
```

Add extra instructions:

```bash
claude-tools summarize-file README.md --instructions "Focus on developer onboarding gaps"
```

### Explain a stack trace or log file

```bash
claude-tools explain-error logs.txt
```

Or pipe logs from another command:

```bash
python app.py 2>&1 | claude-tools explain-error --stdin
```

### Review a diff file

```bash
git diff > changes.diff
claude-tools review-diff changes.diff
```

Or pipe the diff directly:

```bash
git diff | claude-tools review-diff --stdin
```

### Inspect available templates

```bash
claude-tools templates -v
claude-tools template-info diff_review
```

---

## Batch Jobs

Claude Tools can run multiple jobs from either a JSON array or a JSONL file.

### Generate an example batch file

```bash
claude-tools save-example-batch examples/jobs.json
```

### Run a batch

```bash
claude-tools batch examples/jobs.json
```

### Save batch results

```bash
claude-tools batch examples/jobs.json --output results.json
```

### Dry run a batch without calling the API

```bash
claude-tools batch examples/jobs.json --dry-run
```

### Example batch format

```json
[
  {
    "name": "readme-summary",
    "prompt": "Summarize this project in 5 bullets."
  },
  {
    "name": "review-snippet",
    "template": "code_review",
    "variables": {
      "code": "def add(a, b): return a + b"
    }
  }
]
```

Each job supports:

- `name` — optional human-readable identifier
- `prompt` — direct prompt text
- `template` — template name instead of raw prompt
- `variables` — template variables object
- `system` — optional system prompt override
- `metadata` — extra metadata preserved in results

A job must define either `prompt` or `template`.

---

## Command Reference

### `ask`

```bash
claude-tools ask [PROMPT] [OPTIONS]
```

Common options:

- `--template` — render a named template first
- `--var key=value` — pass template variables
- `--stdin` — read the prompt body from stdin
- `--system` — override the default system prompt
- `--model` — override the configured model
- `--max-tokens` — override the configured max token count
- `--temperature` — set request temperature
- `--dry-run` — render only, do not call the API
- `--json` — print structured response metadata
- `--save PATH` — write response text to a file

### `summarize-file`

Summarizes a **local text file** using the built-in `file_summary` template.

```bash
claude-tools summarize-file path/to/file.txt
```

### `explain-error`

Explains a text log, stack trace, or piped stderr output.

```bash
claude-tools explain-error error.log
```

### `review-diff`

Reviews a Git diff from a file or stdin.

```bash
claude-tools review-diff changes.diff
```

### `render`

Renders a template locally for inspection or debugging.

```bash
claude-tools render commit_message --var changes="fix auth timeout"
```

---

## Project Structure

```text
claude-tools/
├── .github/workflows/ci.yml
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── examples/
│   └── jobs.json
├── claude_tools/
│   ├── __init__.py
│   ├── batch.py
│   ├── cli.py
│   ├── client.py
│   ├── config.py
│   ├── io_utils.py
│   └── templates.py
├── tests/
│   ├── test_batch.py
│   ├── test_cli_helpers.py
│   └── test_templates.py
└── pyproject.toml
```

---

## Development

### Run tests

```bash
pytest
```

### Run Ruff

```bash
ruff check .
```

### Build the package

```bash
python -m build
```

---

## Troubleshooting

### “ANTHROPIC_API_KEY is missing”

Set your API key in `.env` or in your shell environment.

### “The 'anthropic' package is not installed”

Install the package in editable mode:

```bash
pip install -e .
```

### Template variable errors

If you see an error like:

```text
Missing required template variable: code
```

make sure every required template field is passed with `--var key=value`.

### Non-text files

`summarize-file`, `explain-error`, and `review-diff` are designed for text input. Binary files are not supported.

---

## Why this project exists

A lot of Claude usage starts as ad hoc prompting and stays that way for too long.

This project turns that into a repeatable tool:

- prompts become reusable templates
- terminal workflows become one-liners
- repeated tasks become scripts instead of copy-paste rituals

It is a strong base for future commands like:

- `review-pr`
- `summarize-commit`
- `generate-tests-from-file`
- Git-aware repository helpers
- custom user-defined templates

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
