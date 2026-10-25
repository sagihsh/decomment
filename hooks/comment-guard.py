#!/usr/bin/env python3
"""PostToolUse hook: fires the decomment gate the moment Claude writes a comment.

Covers Bash as well as Write/Edit, because auto mode writes files with heredocs and sed
rather than the file tools, and a matcher on the file tools alone sees none of it.
"""
import json
import os
import re
import sys


def comments(line_start: str, trailing: str) -> re.Pattern:
    return re.compile(rf"^\s*(?:{line_start})|\S\s+(?:{trailing})(?:\s|$)")


C_STYLE = comments(r"//|/\*|\*(?:\s|$)|\{/\*", "//")
HASH = comments("#(?!!)", "#")
DASH = comments("--", "--")
MARKUP = comments(r"//|/\*|\*(?:\s|$)|\{/\*|<!--", "//|<!--")
LISP = comments(";", ";")

COMMENT_SYNTAX = {
    **dict.fromkeys((
        ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".go", ".rs", ".java", ".kt",
        ".swift", ".c", ".h", ".cc", ".cpp", ".cs", ".php", ".scala", ".dart",
        ".css", ".scss",
    ), C_STYLE),
    ".py": comments(r"#(?!!)|[rRuU]?(?:\"\"\"|''')", "#"),
    **dict.fromkeys((
        ".rb", ".sh", ".bash", ".zsh", ".ex", ".exs", ".r", ".pl", ".yaml", ".yml", ".toml",
    ), HASH),
    ".tf": comments(r"#|//|/\*", "#|//"),
    **dict.fromkeys((".sql", ".lua", ".hs"), DASH),
    **dict.fromkeys((".html", ".vue", ".svelte", ".astro"), MARKUP),
    **dict.fromkeys((".clj", ".cljs", ".el", ".lisp"), LISP),
}
CODE_SUFFIXES = tuple(COMMENT_SYNTAX)
SKIP_PATH = re.compile(
    r"(node_modules|/dist/|/build/|\.min\.|__generated__|\.generated\.|"
    r"/migrations/|/vendor/|\.d\.ts$|/\.git/)"
)
# Comments that are code, convention, or law. Never up for review, so never nag.
EXEMPT = re.compile(
    r"eslint-|biome-ignore|@ts-(expect-error|ignore|nocheck)|prettier-ignore|"
    r"istanbul ignore|[cv]8 ignore|webpackChunkName|@vite-ignore|///\s*<reference|"
    r"@jsxImportSource|__PURE__|go:generate|noqa|type:\s*ignore|sourceMappingURL|"
    r"SPDX-|Copyright|@license|ponytail:|#!/",
    re.IGNORECASE,
)

GATE = (
    "[decomment] {n} new comment line(s) in {path}. Default is deletion. Take each one:\n"
    "1. Can a rename, an extracted function, or a named constant carry it? Make that change and delete the comment.\n"
    "2. Would a competent engineer who did not write this miss anything without it? If not, delete.\n"
    "3. Name where the information lives outside this file: a ticket, a spec, a vendor bug, a measured limit, "
    "another system's contract. If you cannot name one, it is your own design reasoning. Delete it, or move it "
    "to a test name or the PR description.\n"
    "A comment justifying an alternative you rejected always goes. Shortening a comment is not a verdict. "
    "A survivor is one line. Invoke the decomment skill if a call is close."
)


# `> f.ts`, `>> f.ts`, `tee f.ts`, `sed -i ... f.ts`: a shell write aimed at a code file.
BASH_TARGET = re.compile(
    r"(?:>>?|\btee\b(?:\s+-\w+)*|\bsed\b[^|;]*?-i[^|;]*?)\s+[\"\']?([\w./~-]+(?:"
    + "|".join(re.escape(s) for s in sorted(CODE_SUFFIXES, key=len, reverse=True))
    + r"))(?![\w.])"
)


def bash_target(command: str) -> str:
    match = BASH_TARGET.search(command)
    return match.group(1) if match else ""


def new_text(tool: str, args: dict) -> tuple[str, str]:
    """(added text, prior text) for the edit, so untouched comments do not re-fire."""
    if tool == "Write":
        return args.get("content", ""), ""
    if tool == "Edit":
        return args.get("new_string", ""), args.get("old_string", "")
    if tool == "MultiEdit":
        edits = args.get("edits", []) or []
        return ("\n".join(e.get("new_string", "") for e in edits),
                "\n".join(e.get("old_string", "") for e in edits))
    if tool == "NotebookEdit":
        return args.get("new_source", ""), ""
    if tool == "Bash":
        return args.get("command", ""), ""
    return "", ""


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except Exception:
        return
    args = event.get("tool_input") or {}
    tool = event.get("tool_name", "")
    path = args.get("file_path") or args.get("notebook_path") or ""
    if tool == "Bash":
        path = bash_target(args.get("command", ""))
    syntax = COMMENT_SYNTAX.get(os.path.splitext(path)[1].lower())
    if not syntax or SKIP_PATH.search(path):
        return

    added, prior = new_text(tool, args)
    if not added:
        return
    was_there = {line.strip() for line in prior.splitlines()}
    hits = [
        line for line in added.splitlines()
        if syntax.search(line) and not EXEMPT.search(line) and line.strip() not in was_there
    ]
    if not hits:
        return

    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": GATE.format(n=len(hits), path=path.rsplit("/", 1)[-1]),
    }}))


main()
