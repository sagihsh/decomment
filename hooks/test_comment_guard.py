import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).with_name("comment-guard.py")


def fires(tool: str, **tool_input: str) -> bool:
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps({"tool_name": tool, "tool_input": tool_input}),
        capture_output=True, text=True, check=True,
    )
    return "[decomment]" in result.stdout


assert fires("Write", file_path="src/user.ts", content="// fetch the user\nconst user = load();\n")
assert fires("Bash", command="cat > src/config.py <<'EOF'\n# load the config\nconfig = load()\nEOF")
assert fires("Edit", file_path="src/a.go", old_string="x := 1", new_string="// set x\nx := 1")

assert not fires("Write", file_path="src/a.ts", content="// eslint-disable-next-line no-console\nconsole.log(1);\n")
assert not fires("Write", file_path="src/a.ts", content="// ponytail: global lock, per-key locks if it contends\n")
assert not fires("Edit", file_path="src/a.ts", old_string="// 5 rps, PROJ-412\nfoo();", new_string="// 5 rps, PROJ-412\nbar();")
assert not fires("Write", file_path="README.md", content="# Title\n")
assert not fires("Write", file_path="node_modules/pkg/index.js", content="// vendored\n")
assert not fires("Bash", command="echo '# heading' > notes.md")

print("ok")
