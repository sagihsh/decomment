# decomment

**A comment is an apology for code that failed to speak.**

Telling your agent to stop over-commenting doesn't work. It agrees, apologizes, and writes `// Return the result`.

A rule in CLAUDE.md gets read once and then loses to habit. decomment is a Claude Code skill and hook that asks the question at the moment a comment is written, every time. Step-by-step narration, section banners, docblocks that echo the types and notes defending choices nobody asked about don't make it through. When a better name or an extracted function can say the same thing, the agent makes that change instead. What you get back is clean code that explains itself, plus the few comments that actually tell you something.

A comment survives only if it passes three questions:

1. **Could the code have carried this?** If a rename, an extracted function, or a named constant can say it, make that change and delete the comment.
2. **Would a competent engineer miss anything without it?** If not, it was noise.
3. **Where does this information live?** A kept comment has to name a source outside the file: a ticket, a spec, a vendor bug, a measured limit, another system's contract. If the only source is the author's own reasoning, it belongs in the PR description or a test name, not the code.

"Shortened" doesn't count as a verdict. A rewritten comment is still a kept comment and has to pass the same three questions.

## Before and after

A React hook, the way an agent usually writes it:

```ts
// Custom hook to fetch and filter tickets
export const useOpenTickets = (userId: string) => {
  // State for the tickets
  const [tickets, setTickets] = useState<Ticket[]>([]);

  // Fetch the tickets when the userId changes
  useEffect(() => {
    // Guard against an empty userId
    if (!userId) return;

    // We fetch one page at a time because the API rate-limits us
    void fetchTickets(userId).then(setTickets);
  }, [userId]);

  // Filter down to only the open tickets
  return tickets.filter((ticket) => ticket.status === "open");
};
```

The same code with decomment:

```ts
export const useOpenTickets = (userId: string) => {
  const [tickets, setTickets] = useState<Ticket[]>([]);

  useEffect(() => {
    if (!userId) return;
    // One page at a time: the tickets API rate-limits at 5 rps.
    void fetchTickets(userId).then(setTickets);
  }, [userId]);

  return tickets.filter((ticket) => ticket.status === "open");
};
```

Six of the seven comments restated the code. The one that survived carries something the code can't, and it got more specific on the way: "rate-limits us" became the actual number.

## How it works

- **The skill** (`skills/decomment`) runs the three questions, the delete-on-sight patterns, and a report that sorts every comment into deleted, replaced by code, moved, or kept. `references/taxonomy.md` covers the close calls: section headers in long files, comments in tests, config files, shared types, and i18n copy.
- **The hook** (`hooks/comment-guard.py`) runs after every Write, Edit, and Bash call. When new comment lines land in a code file, it puts the three questions in front of the agent right away. It also catches files written with heredocs, `tee`, and `sed -i`, which a hook on the file tools alone would miss. It never flags lint and type directives, license headers, shebangs, or markers other tools require, such as `ponytail:`.

Heads-up: the skill is meant to trigger on every coding task, not only when you ask for a cleanup. That's the point, since the cheapest comment to remove is one that was never written.

## Install

As a plugin, which installs the skill and the hook together:

```
/plugin marketplace add sagihsh/decomment
/plugin install decomment@decomment
```

Manually: copy `skills/decomment` to `~/.claude/skills/decomment` and `hooks/comment-guard.py` next to it. Then register the hook in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit|NotebookEdit|Bash",
        "hooks": [{ "type": "command", "command": "python3 ~/.claude/skills/decomment/comment-guard.py", "timeout": 10 }]
      }
    ]
  }
}
```

The hook needs `python3` on your PATH and has no other dependencies. Run `python3 hooks/test_comment_guard.py` to check it.

## License

MIT
