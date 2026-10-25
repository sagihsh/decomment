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
assert not fires("Bash", command="echo '// x' > data.json")

assert not fires("Write", file_path="a.c", content="#include <stdio.h>\n#define MAX 10\n")
assert not fires("Write", file_path="a.c", content="void f(int *p) {\n  *p = 5;\n}\n")
assert not fires("Write", file_path="a.rs", content="#[derive(Debug)]\nstruct A;\n")
assert not fires("Write", file_path="a.css", content="#header {\n  color: red;\n}\n")
assert not fires("Write", file_path="a.py", content='url = "http://example.com"\n')
assert not fires("Write", file_path="a.rb", content='puts "a #{b}"\n')
assert not fires("Write", file_path="a.py", content="x = load()  # type: ignore\n")

assert fires("Write", file_path="a.c", content="/*\n * set up the buffer\n */\n")
assert fires("Write", file_path="a.ts", content="const x = 1; // set x\n")
assert fires("Write", file_path="a.py", content="x = 1  # set x\n")
assert fires("Write", file_path="a.py", content='def f():\n    """Return one."""\n    return 1\n')
assert fires("Write", file_path="a.sh", content="# loop over files\nfor f in *; do :; done\n")
assert fires("Write", file_path="a.yaml", content="# the port\nport: 80\n")
assert fires("Write", file_path="a.lua", content="-- set x\nx = 1\n")
assert fires("Write", file_path="a.ex", content="# set x\nx = 1\n")
assert fires("Write", file_path="a.dart", content="// set x\nvar x = 1;\n")
assert fires("Write", file_path="a.clj", content=";; set x\n(def x 1)\n")
assert fires("Write", file_path="a.vue", content="<template>\n  <!-- the header -->\n</template>\n")
assert fires("Write", file_path="a.R", content="# set x\nx <- 1\n")
assert fires("Bash", command="cat > src/lib.rs <<'EOF'\n// set x\nlet x = 1;\nEOF")

print("ok")
