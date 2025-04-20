import pytest
from ..utils import (
    print_colored,
    print_success,
    print_error,
    print_warning,
    print_info,
    format_json,
    format_markdown
)

def test_print_colored(capsys):
    print_colored("Test message", "red", "bold")
    captured = capsys.readouterr()
    assert "Test message" in captured.out

def test_print_success(capsys):
    print_success("Success message")
    captured = capsys.readouterr()
    assert "Success message" in captured.out

def test_print_error(capsys):
    print_error("Error message")
    captured = capsys.readouterr()
    assert "Error message" in captured.out

def test_print_warning(capsys):
    print_warning("Warning message")
    captured = capsys.readouterr()
    assert "Warning message" in captured.out

def test_print_info(capsys):
    print_info("Info message")
    captured = capsys.readouterr()
    assert "Info message" in captured.out

def test_format_json():
    data = {
        "answer": "Test answer",
        "sources": ["Source 1", "Source 2"],
        "filters_applied": {"surah": 1, "verse": None}
    }
    formatted = format_json(data)
    assert "Test answer" in formatted
    assert "Source 1" in formatted
    assert "Source 2" in formatted
    assert "surah" in formatted
    assert "verse" in formatted

def test_format_markdown():
    data = {
        "answer": "Test answer",
        "sources": ["Source 1", "Source 2"],
        "filters_applied": {"surah": 1, "verse": None}
    }
    formatted = format_markdown(data)
    assert "# Answer" in formatted
    assert "Test answer" in formatted
    assert "## Sources" in formatted
    assert "- Source 1" in formatted
    assert "- Source 2" in formatted
    assert "## Filters Applied" in formatted
    assert "- surah: 1" in formatted 