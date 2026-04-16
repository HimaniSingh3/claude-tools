import json
from pathlib import Path

from claude_tools.batch import BatchError, load_batch_jobs


def test_load_json_batch(tmp_path: Path) -> None:
    path = tmp_path / "jobs.json"
    path.write_text(
        json.dumps([
            {"name": "a", "prompt": "hello"},
            {"name": "b", "template": "code_review", "variables": {"code": "x=1"}},
        ]),
        encoding="utf-8",
    )

    jobs = load_batch_jobs(path)
    assert len(jobs) == 2
    assert jobs[0].name == "a"
    assert jobs[1].template == "code_review"


def test_load_jsonl_batch(tmp_path: Path) -> None:
    path = tmp_path / "jobs.jsonl"
    path.write_text(
        '{"name": "one", "prompt": "hello"}\n'
        '{"name": "two", "template": "pr_summary", "variables": {"diff": "added tests"}}\n',
        encoding="utf-8",
    )

    jobs = load_batch_jobs(path)
    assert len(jobs) == 2
    assert jobs[1].variables["diff"] == "added tests"


def test_invalid_batch_requires_prompt_or_template(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text(json.dumps([{"name": "broken"}]), encoding="utf-8")

    try:
        load_batch_jobs(path)
        assert False, "Expected BatchError"
    except BatchError as exc:
        assert "prompt" in str(exc)
