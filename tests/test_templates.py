from claude_tools.templates import TemplateError, get_template, list_templates, render_template


def test_list_templates_contains_expected_items() -> None:
    names = [item.name for item in list_templates()]
    assert "code_review" in names
    assert "diff_review" in names


def test_render_template_success() -> None:
    result = render_template("code_review", {"code": "print('hello')"})
    assert "print('hello')" in result
    assert "Review the following code" in result


def test_render_template_missing_variable() -> None:
    try:
        render_template("bug_fix", {"problem": "It crashes"})
        assert False, "Expected TemplateError"
    except TemplateError as exc:
        assert "context" in str(exc)


def test_get_template_variables() -> None:
    template = get_template("file_summary")
    assert template.variables == ["file_path", "content"]
