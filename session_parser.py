"""
session_parser.py – loads Claude session data from ~/.claude/projects/
"""

import json
from pathlib import Path
from datetime import datetime, timezone

CLAUDE_DIR = Path.home() / ".claude" / "projects"

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Java / Spring Boot": [
        "java", "spring", "maven", "gradle", "springboot",
        "controller", "repository", "entity", "hibernate", "jpa",
        "bean", "autowired", "restful", "microservice",
        "tony", "tony-demo", "spring-boot",
    ],
    "Python": [
        "python", "pip", "django", "flask", "fastapi",
        "pandas", "numpy", "pytest", "schedule", "tkinter",
        "pyside", "pyqt", "script", "missing", "record",
        "scheduleapp", "pythonproject", "pycharm",
    ],
    "Claude 設定 / 工具": [
        "claude", "rule", "hook", "mcp", "plugin",
        "workflow", "flowchart", "session", "statusline",
        "config", "setting", "memory",
    ],
    "GitHub / Git": [
        "github", "git", "repo", "commit", "branch",
        "pull", "push", "merge", " pr ",
    ],
}


def get_display_name(dir_name: str) -> str:
    if dir_name == "C--Users-ian":
        return "全域對話"
    for prefix in [
        "C--Users-ian-PycharmProjects-",
        "C--Users-ian-OneDrive-Desktop-",
        "C--Users-ian-PyCharm",
        "C--Users-ian-",
    ]:
        if dir_name.startswith(prefix):
            name = dir_name[len(prefix):]
            return name if name else dir_name
    return dir_name


def _parse_content(content) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                return item.get("text", "").strip()
    return ""


def extract_user_messages(jsonl_path: Path, limit: int = 6) -> list[str]:
    msgs: list[str] = []
    try:
        with open(jsonl_path, "r", encoding="utf-8", errors="replace") as fh:
            raw = fh.read(80_000)          # read first 80 KB only
        for line in raw.splitlines():
            if len(msgs) >= limit:
                break
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") != "user":
                continue
            text = _parse_content(obj.get("message", {}).get("content", ""))
            # skip hook outputs, slash-commands, system tags, and very short lines
            if text and len(text) > 5 and not text.startswith(("[", "/", "<")):
                msgs.append(text[:200])
    except Exception:
        pass
    return msgs


def get_first_date(jsonl_path: Path) -> str:
    try:
        with open(jsonl_path, "r", encoding="utf-8", errors="replace") as fh:
            raw = fh.read(10_000)
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                ts = obj.get("timestamp", "")
                if ts:
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d")
            except Exception:
                continue
    except Exception:
        pass
    return "未知日期"


def classify(project_name: str, combined_text: str) -> str:
    haystack = (project_name + " " + combined_text).lower()
    scores = {cat: 0 for cat in CATEGORY_KEYWORDS}
    for cat, words in CATEGORY_KEYWORDS.items():
        scores[cat] = sum(1 for w in words if w in haystack)
    best, best_score = max(scores.items(), key=lambda kv: kv[1])
    return best if best_score > 0 else "其他"


def load_all_projects() -> dict[str, list[dict]]:
    """
    Returns:
        {
          category_name: [
            {
              "project":  str,
              "dir_name": str,
              "sessions": [
                {"id": str, "date": str, "summary": str, "path": Path}
              ]
            }
          ]
        }
    """
    result: dict[str, list[dict]] = {}

    if not CLAUDE_DIR.exists():
        return result

    for proj_dir in sorted(CLAUDE_DIR.iterdir()):
        if not proj_dir.is_dir():
            continue

        jsonl_files = sorted(
            f for f in proj_dir.glob("*.jsonl")
            if f.stat().st_size > 500
        )
        if not jsonl_files:
            continue

        display = get_display_name(proj_dir.name)
        sessions: list[dict] = []

        for jf in jsonl_files:
            msgs = extract_user_messages(jf)
            date = get_first_date(jf)
            summary = "\n".join(f"• {m}" for m in msgs) if msgs else "（無法讀取內容）"
            sessions.append({
                "id": jf.stem,
                "date": date,
                "summary": summary,
                "path": jf,
            })

        combined = (display + " " + proj_dir.name.lower() + " "
                    + " ".join(s["summary"] for s in sessions[:2]))
        cat = classify(display, combined)

        result.setdefault(cat, []).append({
            "project": display,
            "dir_name": proj_dir.name,
            "sessions": sessions,
        })

    return result
