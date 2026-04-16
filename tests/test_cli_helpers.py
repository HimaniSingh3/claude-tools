from claude_tools.cli import _build_prompt, _parse_key_value_pairs


def test_parse_key_value_pairs() -> None:
    result = _parse_key_value_pairs(["code=print('hi')", "lang=python"])
    assert result["code"] == "print('hi')"
    assert result["lang"] == "python"


def test_build_prompt_from_template() -> None:
    prompt = _build_prompt(
        prompt=None,
        template="pr_summary",
        variables=["diff=Added tests and fixed imports"],
        stdin=False,
    )
    assert "Added tests and fixed imports" in prompt
    assert "pull request summary" in prompt.lower()


def test_build_prompt_with_direct_input() -> None:
    prompt = _build_prompt(
        prompt="Explain decorators",
        template=None,
        variables=[],
        stdin=False,
    )
    assert prompt == "Explain decorators"
