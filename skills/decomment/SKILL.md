---
name: decomment
description: "Use when code contains comments and it is worth deciding whether they should exist at all: a request to reduce, trim, remove, review or clean up comments, a complaint that code is over-commented, or a PR whose diff adds comments. ALSO use proactively at two moments in every coding task, without being asked: the moment you are about to write a comment of any kind (in a new function, component, hook, test, script, config, bug fix or refactor), and again before you hand the edit back. Freshly written code carries step narration, section banners, docblocks that echo types, and notes justifying choices the author made, and none of those should reach the user. If you are writing or editing code right now, this skill applies."
---

# decomment

**A comment is an apology for code that failed to speak.** Occasionally the apology is warranted, because some information genuinely cannot live in code. Usually it is not, and the honest fix is better code.

Deletion is the default. Keeping is the exception, and it has to be earned.

## The contract

Every comment in scope ends in exactly one of four states, and you name the state for each:

| State | What it means |
|---|---|
| **Deleted** | The default. Needs no justification. |
| **Replaced by code** | A rename, an extracted function, or a named constant now carries it. |
| **Moved** | The information was real but belongs elsewhere: a test name, the PR description, a ticket. |
| **Kept** | Survived all three questions. One line. Source named in the report. |

**"Shortened" is not a state. "Reworded" is not a state. "Made it more concise" is not a state.** A comment you rewrote is a comment you kept, and it owes exactly the same justification as one you left untouched. Trimming the words while keeping the count is the failure this skill exists to prevent.

## The three questions

One comment at a time, in order. Most die at question 1.

### 1. Could the code have carried this?

Before asking whether it is a *good* comment, find the change that makes it unnecessary.

1. **Rename.** `const d` plus `// days until expiry` becomes `daysUntilExpiry`. A name is checked by the compiler and read by everyone; a comment is checked by nobody.
2. **Extract and name.** `// validate and normalize the payload` above twelve lines becomes `normalizePayload(raw)`. The comment is now the signature, and it cannot drift from the code it names.
3. **Name the constant.** `// 5 retries max` next to a bare `5` becomes `MAX_RETRIES`. Same for magic strings, timeouts, thresholds.
4. **Restructure.** An early return deletes `// only for admins`. Splitting a function that does two things deletes the comment announcing the second half.

Make the change, then delete the comment. Keep renames and extractions inside the scope you were already editing: if one would touch an exported symbol or ripple across files, propose it in the report instead and keep the comment until it lands.

> When a clean comment is hard to write, the difficulty is in the design, not the description. (Ousterhout)

### 2. Would a competent engineer miss anything without it?

Not a beginner. Someone who knows this language, this framework and this codebase, but was not in the room when the code was written.

If they reach the same conclusions unaided, it was noise. Leave it deleted.

If not, say out loud the one thing they would have missed. That sentence is the comment, and it is almost always shorter and more specific than what was there. If you cannot finish the sentence, it was noise after all.

### 3. Where does this information live?

Point at the thing outside this file that the comment reports: a ticket, a spec section, a vendor bug, a measured rate limit, another system's contract, a platform quirk.

**If the only source is your own reasoning while writing the code, it is a design note, not a comment.** Design notes go in the PR description, the ticket, or a test name. They do not go in the source, where nothing keeps them true and every future reader pays to read them.

## You do not get to annotate the roads you did not take

The most common survivor in freshly written code, and it always goes:

```ts
// setDate, not a fixed 24h stride: that drifts across a DST boundary.
// Not toISOString().slice(0, 10): that is UTC, so a late breach buckets to tomorrow.
// Unmemoized on purpose: the fresh clock is what flips a ticket to breached.
// Sequential rather than Promise.all here.
```

Each fails question 3. The source is you, five minutes ago, holding an alternative that nobody else is holding. No reader arrives at that line carrying your rejected option, so the comment answers a question never asked, and it is the first thing to go stale when the code moves.

If choosing the other way would break something, **a test named for that case catches it and survives refactoring.** A comment does neither.

```ts
it("keeps the bucket key stable across a DST boundary", ...)
```

Delete the comment, write the test. The one exception: the rejected alternative is the thing a reader will actively try to "fix", *and* there is external evidence it fails, such as a ticket, a reverted commit, or a benchmark. Cite the evidence or delete the comment.

## Authorship makes you lenient, not right

**A comment you wrote minutes ago gets the harshest read, not the gentlest.** You know why the code is right, so every note you left feels load-bearing. You are reading your own intent back off the page instead of testing what the page actually says. Judge it as if a stranger wrote it and you have to keep it true for two years.

Comments in a diff you just produced should almost all die. If most survive your pass, you did not run the gate, you defended your work.

## Delete on sight

No deliberation. Where the third column names a code change, make it and delete the comment.

| Pattern | Example | Fix instead |
|---|---|---|
| Restates the code | `// increment the counter` above `counter++` | nothing, just delete |
| Restates the code with a "because" | `// Only admins can delete` above `if (!isAdmin) return false` | nothing, a why that restates is still restating |
| Justifies an alternative not taken | `// Not Promise.all: ...`, `// on purpose`, `// deliberately` | a test named for the case, or delete |
| Narrates steps | `// 1. Fetch the user`, `// then map to the model` | extract a function per step if the steps are real |
| Describes the edit, not the code | `// changed from useState to useReducer` | nothing, git has it |
| Banner or section divider | `// ===== HELPERS =====`, `// --- state ---` | split the file |
| Echoes a name or type | `/** The user's ID */` above `userId: string` | nothing, just delete |
| Explains a vague name | `// the count of unread messages` above `const n` | rename to `unreadCount` |
| Explains a magic value | `// 30 second timeout` above `30_000` | name the constant |
| Announces a block | `// build the request body`, then ten lines | extract `buildRequestBody()` |
| Tracks which branch you are in | `// admin path`, `// non-admin path` | early return, or split the function |
| Commented-out code | any disabled block, however short | nothing, git has it |
| End-of-block marker | `} // end useEffect` | the block is too long, extract |
| Teaches the language or framework | `// useEffect runs after render`, `// toISOString is UTC` | nothing, just delete |
| Vague TODO | `// TODO: improve this`, `// TODO: refactor later` | do it, or drop it |
| Repeats a why already stated at the definition site | the same reason in two files | keep the one at the definition |
| Signposts the obvious | `// early return`, `// error handling`, `// cleanup` | nothing, just delete |
| Attribution or date stamp | `// added by X, 2026-03-01` | nothing, blame has it |
| Runs to two or more lines | any of the above, wrapped | the length is the tell: it is a design note |

A surviving comment is one line. If it needs two, either the code needs the fix or the content belongs in the PR description.

## What earns a comment

Only after all three questions have failed. Four kinds, and each one **points at something you can name**:

1. **A constraint that lives in another system.** A platform quirk, an upstream bug, a contract you do not control. Link the ticket so the comment can be retired with the constraint.
   `// Safari fires blur before click; the timeout lets the click land. PROJ-318.`

2. **Non-obvious correctness that types cannot express.** Units, timezone, encoding, a required ordering, an invariant.
   `// Epoch seconds here, ms on /v2. Do not pass this straight to Date.`

3. **A decoder for genuinely dense code.** A regex, bit math, a named algorithm, a formula.
   `// Matches "3d 4h" and "45m": repeated [value][unit] pairs, unit required.`

4. **A pointer that changes what a caller does.** A deprecation with its replacement, or a TODO with a ticket and a concrete action.
   `/** @deprecated Use useTicketQuery. Removed once PROJ-520 lands. */`

If you cannot point at the ticket, the spec, the other system, or the measurement, it is not one of these. **"It is sort of a why" is not a pass**, and there is deliberately no category for "a choice a reader might second-guess" — that category licenses annotating every decision you made, which is question 3's job to stop.

### Docblocks are comments too

A `/** */` gets the same three questions. A good signature and real types already document shape, so a docblock earns its place only by adding what they cannot: units, a caller contract, a footgun, a deprecation.

```ts
/** The user's ID */          // delete: the name and type already said this
userId: string;

/** Epoch ms, UTC. The backend sends seconds; multiply before use. */   // keep
expiresAt: number;
```

Drop `@param` and `@returns` lists that restate typed parameter names. Keep a `@param` stating a constraint the type cannot express ("must be lowercased", "pass null to clear"), and consider whether a narrower type could carry it instead.

One exception: when a docblock is the source of user-facing documentation, most often component props in Storybook autodocs or hover tooltips on a widely used utility, it is load-bearing even where it reads as obvious. Check for an autodocs story before stripping a component's prop docs.

## Never touch

**Directives a tool reads.** Code wearing a comment's clothes; deleting them changes behavior: `eslint-disable*`, `biome-ignore`, `@ts-expect-error`, `@ts-ignore`, `@ts-nocheck`, `prettier-ignore`, `istanbul ignore`, `c8`/`v8 ignore`, bundler magic comments (`webpackChunkName`, `@vite-ignore`), `/// <reference>`, `@jsxImportSource`, `/* @__PURE__ */`, `//go:generate`, `# noqa`, `# type: ignore`, shebangs, `sourceMappingURL`. Prose next to one is usually load-bearing too: it says why the error is expected or why the rule is off.

**Markers another tool requires.** Some workflows mandate a tagged comment, such as the `ponytail:` notes that record a deliberate shortcut and its upgrade path. They belong to that tool. Out of scope here.

**Legal text.** License, copyright, SPDX headers.

**Generated and vendored files.** Anything with an "autogenerated, do not edit" banner, plus lockfiles, snapshots, vendored source, and migrations that already ran.

**Comments outside the change you were asked to make.** They may encode context you do not have. If a pre-existing one looks stale, say so in the report rather than deleting it, unless a full sweep was requested.

**Any comment you do not understand.** Not understanding it is evidence it carries information. Flag it and move on.

Do not add a comment noting that comments were removed, and do not reformat, rewrap, or reorder code on the way through. Apart from the renames and extractions question 1 calls for, the diff should be deletions.

## Rationalization table

Every one of these has been used to keep a comment that should have gone.

| Excuse | Reality |
|---|---|
| "This one is a genuine why" | Most narration is phrased as a why. "Because X" where X is the next line is still restatement. |
| "A reader would second-guess this" | You are the only one who knows what was second-guessed. Nobody arrives holding your rejected alternative. |
| "It documents a subtle bug I avoided" | Then it is a test, and the test name is the comment. A test fails when the code changes; a comment does not. |
| "It explains non-obvious library behaviour" | Non-obvious to whom? A competent user of that library knows it. Teaching the framework is delete-on-sight. |
| "I will just make it shorter" | Shortening is not a verdict. A shortened comment is a kept comment and owes the same justification. |
| "It is one line, it costs nothing" | It costs every reader attention and every editor a second artifact that nothing keeps true. |
| "I wrote this code, so I know the note is needed" | Authorship is the strongest bias toward keeping, not evidence. Judge it as a stranger's. |
| "The user asked me to explain the tricky parts" | Explain them in names, tests and the report. If they truly want prose in the source, say what you would do instead in one sentence, then comply. |
| "Deleting loses knowledge" | Only if it has nowhere to go. Move it: test name, PR description, ticket. |
| "It is only a small diff, not worth a pass" | The smallest diffs are where narration hides best, because nobody rereads three lines. |

## Red flags

Stop and rerun the gate when you notice any of these:

- The comment starts with "Not X:", "X, not Y:", "on purpose", "deliberately", "intentionally", "we do this because".
- You are editing a comment's wording rather than deciding its fate.
- A survivor runs to two lines.
- Most comments in a diff you wrote yourself survived.
- The pass produced deletions but no renames, extractions, or named constants.
- You reached for a keep category and had to argue the comment into it.

## Running it

**Proactively, while writing code.** The cheap path: a comment never written costs nothing to remove. Write the code, then reread every comment in the edit before it is final and run the gate. Expect nearly all to go and a few to become names. No report needed, just do not ship the narration.

**As an explicit pass over existing code.**

1. **Scope it.** Use the file, path, or selection if named. Otherwise take the changed code: `git diff`, `git diff --staged`, and untracked files. If nothing is changed and nothing was named, ask rather than sweeping the repo.
2. **Read whole files, not diff hunks.** A comment can only be judged with its surroundings visible.
3. **Work one comment at a time** through all three questions. Targeted edits, not rewrites.
4. **Verify.** `git diff` should show deletions plus the renames question 1 called for, nothing else. If a rename or extraction happened, run the project's typecheck and lint.
5. **Report.**

## Report format

```
Removed 14 comments in 3 files.

Replaced by code, 3:
- utils/expiry.ts:12 `d` renamed `daysUntilExpiry`
- api/tickets.ts:40 request-body block extracted as buildTicketBody()
- hooks/usePoll.ts:8 `30_000` named POLL_INTERVAL_MS

Moved, 1:
- sla.ts:19 DST bucket-key rationale is now the test name in sla.test.ts

Kept 2 — comment, then the source outside this file:
- api/tickets.ts:88 5 rps rate limit — measured, PROJ-412
- hooks/useSession.ts:22 epoch seconds vs ms — backend /v2 contract

Proposed, not done:
- models/user.ts:30 exported `fmt` should be `formatDisplayName`; 14 call sites, comment kept until renamed

Flagged, not touched:
- utils/dates.ts:12 pre-existing, claims a DST workaround I could not verify
```

**A kept line with no source in the second column is not kept, it is deleted.** Writing the source is the check; if you find yourself writing "because it is clearer" or "helps future readers", the comment just failed.

No prose beyond the report unless something needs a decision from the user.

## Calibration

- **Ordinary application code** (components, hooks, API calls, glue, tests): zero comments. Zero is the normal result for the whole file, not an aggressive one.
- **A freshly written diff of a few hundred lines:** zero or one survivor. Three or more means the gate was not run.
- **Genuinely dense code** (a parser, a scheduler, a bit-packed protocol, date math): several legitimately survive. There is no quota, only the questions.
- **A pass with no renames, extractions, or named constants** almost certainly skipped question 1. Comments cluster exactly where names are weak and functions are long.

## Worked example

A hook as first written, seven comments:

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

After:

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

Six restated the code, the hook's own name, or the language. The seventh survived all three questions (no name expresses a rate limit, and the limit lives in the API), and it was *sharpened* on the way through: "rate-limits us" became the actual number. Survivors are usually vague, and specificity is what makes one worth maintaining.

## More detail

`references/taxonomy.md` has the full bad-comment and good-comment taxonomy, the Martin and Ousterhout positions and how they reconcile, worked before/after pairs in TypeScript, React, Python and Go, a worked example of question 1 replacing four comments with code, and the hard judgment calls (section headers in a long file, intentional duplication, comments in tests, config files, shared type definitions, i18n copy). Read it when a call is genuinely close or a decision needs justifying to a reviewer.
