"""
Tests for session_parser.py
Tests only pure-logic functions that don't require Qt or real file I/O.
"""
import json
import pytest
from pathlib import Path

from session_parser import (
    get_display_name,
    _parse_content,
    extract_user_messages,
    get_first_date,
    classify,
)


# ─── get_display_name ────────────────────────────────────────────────────────

class TestGetDisplayName:
    def test_global_dir_returns_chinese_label(self):
        assert get_display_name("C--Users-ian") == "全域對話"

    def test_pycharm_projects_prefix_stripped(self):
        assert get_display_name("C--Users-ian-PycharmProjects-MyApp") == "MyApp"

    def test_desktop_prefix_stripped(self):
        assert get_display_name("C--Users-ian-OneDrive-Desktop-Notes") == "Notes"

    def test_generic_ian_prefix_stripped(self):
        assert get_display_name("C--Users-ian-Documents") == "Documents"

    def test_unknown_dir_returned_as_is(self):
        assert get_display_name("D--SomeOtherPath") == "D--SomeOtherPath"

    def test_prefix_only_returns_dir_name_when_name_empty(self):
        # prefix matches but nothing after → return original dir_name
        result = get_display_name("C--Users-ian-PycharmProjects-")
        assert result == "C--Users-ian-PycharmProjects-"


# ─── _parse_content ───────────────────────────────────────────────────────────

class TestParseContent:
    def test_plain_string_stripped(self):
        assert _parse_content("  hello  ") == "hello"

    def test_list_with_text_item_extracted(self):
        content = [{"type": "text", "text": "  world  "}]
        assert _parse_content(content) == "world"

    def test_list_with_no_text_type_returns_empty(self):
        content = [{"type": "image", "text": "ignored"}]
        assert _parse_content(content) == ""

    def test_empty_list_returns_empty(self):
        assert _parse_content([]) == ""

    def test_list_picks_first_text_item(self):
        content = [
            {"type": "tool_result", "text": "x"},
            {"type": "text", "text": "first"},
            {"type": "text", "text": "second"},
        ]
        assert _parse_content(content) == "first"

    def test_none_returns_empty(self):
        assert _parse_content(None) == ""

    def test_integer_returns_empty(self):
        assert _parse_content(42) == ""


# ─── extract_user_messages ───────────────────────────────────────────────────

class TestExtractUserMessages:
    def _write_jsonl(self, tmp_path: Path, records: list[dict]) -> Path:
        p = tmp_path / "session.jsonl"
        p.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
        return p

    def test_returns_user_messages_only(self, tmp_path):
        records = [
            {"type": "user", "message": {"content": "hello there"}},
            {"type": "assistant", "message": {"content": "hi"}},
            {"type": "user", "message": {"content": "what is this?"}},
        ]
        path = self._write_jsonl(tmp_path, records)
        result = extract_user_messages(path)
        assert result == ["hello there", "what is this?"]

    def test_skips_slash_commands(self, tmp_path):
        records = [
            {"type": "user", "message": {"content": "/goal something"}},
            {"type": "user", "message": {"content": "normal message"}},
        ]
        path = self._write_jsonl(tmp_path, records)
        result = extract_user_messages(path)
        assert result == ["normal message"]

    def test_skips_bracket_prefixed_lines(self, tmp_path):
        records = [
            {"type": "user", "message": {"content": "[hook output] done"}},
            {"type": "user", "message": {"content": "real question"}},
        ]
        path = self._write_jsonl(tmp_path, records)
        result = extract_user_messages(path)
        assert result == ["real question"]

    def test_skips_very_short_messages(self, tmp_path):
        records = [
            {"type": "user", "message": {"content": "ok"}},
            {"type": "user", "message": {"content": "good message here"}},
        ]
        path = self._write_jsonl(tmp_path, records)
        result = extract_user_messages(path)
        assert result == ["good message here"]

    def test_respects_limit(self, tmp_path):
        records = [
            {"type": "user", "message": {"content": f"message number {i}"}}
            for i in range(10)
        ]
        path = self._write_jsonl(tmp_path, records)
        result = extract_user_messages(path, limit=3)
        assert len(result) == 3

    def test_truncates_long_messages_to_200(self, tmp_path):
        long_msg = "a" * 300
        records = [{"type": "user", "message": {"content": long_msg}}]
        path = self._write_jsonl(tmp_path, records)
        result = extract_user_messages(path)
        assert len(result[0]) == 200

    def test_missing_file_returns_empty(self, tmp_path):
        result = extract_user_messages(tmp_path / "nonexistent.jsonl")
        assert result == []

    def test_invalid_json_lines_skipped(self, tmp_path):
        p = tmp_path / "bad.jsonl"
        p.write_text('{"type":"user","message":{"content":"valid message here"}}\nnot-json\n', encoding="utf-8")
        result = extract_user_messages(p)
        assert result == ["valid message here"]


# ─── get_first_date ───────────────────────────────────────────────────────────

class TestGetFirstDate:
    def _write_jsonl(self, tmp_path: Path, records: list[dict]) -> Path:
        p = tmp_path / "session.jsonl"
        p.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
        return p

    def test_returns_utc_date_from_timestamp(self, tmp_path):
        records = [{"timestamp": "2025-03-15T10:30:00Z", "type": "user"}]
        path = self._write_jsonl(tmp_path, records)
        assert get_first_date(path) == "2025-03-15"

    def test_returns_date_from_iso_offset_timestamp(self, tmp_path):
        records = [{"timestamp": "2025-06-01T08:00:00+08:00", "type": "user"}]
        path = self._write_jsonl(tmp_path, records)
        assert get_first_date(path) == "2025-06-01"

    def test_skips_lines_without_timestamp(self, tmp_path):
        records = [
            {"type": "user"},
            {"timestamp": "2024-01-20T00:00:00Z", "type": "assistant"},
        ]
        path = self._write_jsonl(tmp_path, records)
        assert get_first_date(path) == "2024-01-20"

    def test_missing_file_returns_unknown(self, tmp_path):
        result = get_first_date(tmp_path / "none.jsonl")
        assert result == "未知日期"

    def test_empty_file_returns_unknown(self, tmp_path):
        p = tmp_path / "empty.jsonl"
        p.write_text("", encoding="utf-8")
        assert get_first_date(p) == "未知日期"


# ─── classify ────────────────────────────────────────────────────────────────

class TestClassify:
    def test_java_keywords_classified_correctly(self):
        assert classify("tony-demo", "spring boot controller") == "Java / Spring Boot"

    def test_python_keywords_classified_correctly(self):
        assert classify("PythonProject", "pytest fastapi") == "Python"

    def test_claude_keywords_classified_correctly(self):
        assert classify("my-rules", "claude hook mcp config") == "Claude 設定 / 工具"

    def test_github_keywords_classified_correctly(self):
        assert classify("deploy", "git commit push repo") == "GitHub / Git"

    def test_no_keywords_falls_back_to_other(self):
        assert classify("zzz", "nothing relevant here") == "其他"

    def test_higher_score_wins(self):
        # python has 3 matches, java has 1
        result = classify("project", "python pip pytest django spring")
        assert result == "Python"
