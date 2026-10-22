# Comment taxonomy and hard cases

Reference for `decomment`. Read this when a call is close, when a decision needs justifying to a reviewer, or when working in a language the main skill file does not illustrate.

## Contents

- [The two philosophies, and how they reconcile](#the-two-philosophies-and-how-they-reconcile)
- [Bad comments, by category](#bad-comments-by-category)
- [Good comments, by category](#good-comments-by-category)
- [Ousterhout's red flags](#ousterhouts-red-flags)
- [Before and after, by language](#before-and-after-by-language)
- [Design notes are not comments](#design-notes-are-not-comments)
- [Hard judgment calls](#hard-judgment-calls)
- [Sources](#sources)

## The two philosophies, and how they reconcile

There is an apparent disagreement in the literature, and knowing where it actually lands prevents both over-deleting and rationalized keeping.

**Robert Martin (Clean Code, ch. 4)** opens with "comments are, at best, a necessary evil" and "the proper use of comments is to compensate for our failure to express ourselves in code." On this view a comment is an admission that the code is not clear enough, so the first move is always to fix the code.

**John Ousterhout (A Philosophy of Software Design, ch. 12 to 16)** rejects that framing explicitly. Comments carry information of a kind code cannot: abstractions, design intent, the reasoning behind a decision. He argues most codebases are badly *under*-commented, and that in-code documentation is what lets a reader work at the interface level instead of reading every implementation.

They agree on the part that matters here:

> Comments should describe things that aren't obvious from the code.

Martin's bad-comment list is that principle applied negatively: every category on it is a comment whose content was already obvious. Ousterhout's interface comments are the same principle applied positively: a caller's contract is genuinely not obvious from an implementation.

**Where this skill lands.** Martin's framing runs first, because it is the one that produces action: a comment is an apology for code that failed to speak, so the opening move on every comment is to look for the rename, extraction, or restructure that makes it unnecessary. Ousterhout supplies the stopping condition: some information (a why, a contract, a constraint, an invariant) cannot be encoded in any name or signature, and deleting it destroys knowledge. So the order is fixed. Try to fix the code. If the information cannot survive in code, keep it in a comment, sharpened.

The net effect is fewer comments, each carrying more. Neither author would defend `// increment i` and neither would delete a note explaining why a loop has to run backwards.

Where this skill leans hardest away from Ousterhout: he writes for large systems with long-lived module boundaries, where interface comments pay for themselves, and he is arguing against a culture that under-comments. AI-written application code has the opposite problem, and it has real types, short functions, and named exports that carry much of what his interface comments carry. So the bar for a docblock here is well above what his examples suggest.

## Bad comments, by category

Martin's taxonomy, with the reason each one fails the test.

**Redundant.** Takes longer to read than the code and says no more. `// the day of the month` above `dayOfMonth`.

**Mumbling.** Written for the author's own benefit, meaningless to anyone else. `// tried this a couple of ways`.

**Misleading.** Almost true, which is worse than absent. A comment saying a method returns when a condition is met, where it actually returns slightly later. Comments rot silently because nothing tests them; the code moved and the comment did not.

**Mandated.** A docblock on every function because a rule says so. Produces walls of `@param` lines that restate the signature and train readers to skip all comments, including the useful ones.

**Journal.** A changelog at the top of a file. Version control does this better and does not go stale.

**Noise.** Restates the obvious with no new information. `/** Default constructor. */`, `// private instance variable`.

**Position markers.** `// ===== ACTIONS =====`. Occasionally a genuine signpost, usually clutter. If a file needs internal signage to be navigable, the file is too long, and splitting it is the real fix.

**Closing brace comments.** `} // end for`. A sign the block is long enough to need marking, which means it should be extracted.

**Attributions and bylines.** `// added by RCM`. Blame knows.

**Commented-out code.** Nobody dares delete it because they assume it is there for a reason. It is not. Delete it; git has it.

**Nonlocal information.** A comment describing behavior controlled somewhere else, such as documenting a default port next to a function that does not set it. It will drift the moment the real source changes.

**Too much information.** A paragraph of RFC history in a decoder. Link the spec instead.

**Inobvious connection.** A comment needing its own explanation to connect it to the code, so the reader now has two puzzles.

**Function headers.** A short well-named function needs no header. `// Deletes the user` above `deleteUser` is pure restatement.

**Docblocks on non-public code.** Formal API documentation for an internal helper is ceremony with a maintenance cost.

One more, not in Martin's list because it predates the pattern, and the most common category in AI-written code:

**Edit narration.** `// switched to useReducer`, `// new helper`, `// keeping this for now`, `// removed the old call`. The comment describes the diff, not the code. It is meaningless the moment the change is merged and actively confusing a month later.

## Good comments, by category

**Legal.** License and copyright headers. Not up for review.

**Intent.** Why this approach and not the obvious one. `// Sorting in place: the caller relies on identity for its memo key.`

**Warning of consequences.** `// Not thread-safe: callers hold the lock.` `// Do not await in this loop, the API rate-limits at 5 rps.`

**Clarification of something you cannot change.** A third-party return value or a fixed protocol quirk. Prefer wrapping it in a well-named function; when you cannot, a comment is right.

**Amplification.** Flagging that something apparently trivial actually matters. `// The trim matters: the upstream ID arrives padded and the lookup is exact-match.`

**Actionable TODO.** With an owner or ticket and a concrete action. `// TODO(PROJ-533): drop once the v1 endpoint is retired.` An untracked TODO is a wish, and wishes accumulate.

**Interface contracts that types cannot express.** Units, mutation, nullability semantics beyond the type, ordering requirements, side effects, error behavior. This is where a docblock genuinely pays.

**Decoders for dense code.** State the intent of a regex, a bit manipulation, or a formula, and cite the source for a named algorithm.

## Ousterhout's red flags

Useful as diagnostics, because each points at a fix in the code rather than in the comment.

**Comment repeats code.** Everything in the comment is visible in the code beside it. Delete.

**Vague name.** A variable or function whose name needs a comment to be understood. Rename, then delete.

**Hard to describe.** If a clean comment for something is hard to write, that is evidence the thing has a muddled interface or does too much. The difficulty is in the design, not the description. This is the single most useful signal in the book, and it argues for restructuring rather than for a longer comment.

**Implementation documentation contaminates the interface.** A caller-facing docblock explaining internals. Callers now depend on details that were meant to be free to change. Move it inside.

## Before and after, by language

### TypeScript: an API function

```ts
// Function to get all tickets for a user
// Takes a userId and returns a promise of tickets
export const getTickets = async (userId: string): Promise<Ticket[]> => {
  // Build the URL
  const url = `/api/tickets?userId=${userId}`;

  // Make the request
  const res = await fetchJson(url);

  // Map the raw data to models
  // We use fromJson because the server sends snake_case
  return res.data.map(Ticket.fromJson);
};
```

After:

```ts
export const getTickets = async (userId: string): Promise<Ticket[]> => {
  const res = await fetchJson(`/api/tickets?userId=${userId}`);
  return res.data.map(Ticket.fromJson);
};
```

The signature carries what the first two lines said. `// Build the URL` and `// Make the request` restate their own expressions. The snake_case note describes what `fromJson` exists to do, and belongs at that function's definition if anywhere, not repeated at every call site.

### React: a component

```tsx
// Props for the TicketRow component
interface TicketRowProps {
  /** The ticket */
  ticket: Ticket;
  /** Callback when clicked */
  onSelect: (id: string) => void;
}

export const TicketRow: FC<TicketRowProps> = ({ ticket, onSelect }) => {
  // Handler for the click event
  const handleClick = () => {
    // Pass the id up to the parent
    onSelect(ticket.id);
  };

  // Render the row
  return (
    <div className="flex items-center gap-2" onClick={handleClick}>
      {/* The ticket title */}
      <span>{ticket.title}</span>
    </div>
  );
};
```

After:

```tsx
interface TicketRowProps {
  ticket: Ticket;
  onSelect: (id: string) => void;
}

export const TicketRow: FC<TicketRowProps> = ({ ticket, onSelect }) => (
  <div className="flex items-center gap-2" onClick={() => onSelect(ticket.id)}>
    <span>{ticket.title}</span>
  </div>
);
```

Every comment echoed a name. Note the JSX comment: `{/* The ticket title */}` above a `<span>` rendering the title is the same failure in different syntax, and JSX comments are easy to overlook because they look structural.

If `TicketRow` has an autodocs story, keep prop docblocks that say something real, for example `/** Rendered muted when the ticket is archived. */`, and still drop `/** The ticket */`.

### Python

```python
def normalize_emails(rows):
    # Loop over the rows
    for row in rows:
        # Get the email
        email = row.get("email")
        # Skip if empty
        if not email:
            continue
        # Lowercase and strip it
        # We lowercase because the lookup table is case sensitive and
        # the upstream CRM exports mixed case
        row["email"] = email.strip().lower()
    return rows
```

After:

```python
def normalize_emails(rows):
    for row in rows:
        email = row.get("email")
        if not email:
            continue
        # The lookup table is case sensitive and the CRM exports mixed case.
        row["email"] = email.strip().lower()
    return rows
```

Four narration comments went. The fifth stayed because the reason lives in two systems outside this file, and it was tightened from three lines to one.

### Go

```go
// Retry the request up to maxRetries times
for i := 0; i < maxRetries; i++ {
    resp, err = client.Do(req)
    // If no error, break out of the loop
    if err == nil {
        break
    }
    // Sleep before retrying
    // Exponential backoff, doubling each time, because the gateway
    // returns 429 under burst and recovers within a few seconds
    time.Sleep(time.Duration(1<<i) * baseDelay)
}
```

After:

```go
for i := 0; i < maxRetries; i++ {
    resp, err = client.Do(req)
    if err == nil {
        break
    }
    // Exponential backoff: the gateway 429s under burst, recovers in seconds.
    time.Sleep(time.Duration(1<<i) * baseDelay)
}
```

`1<<i` is the kind of expression that earns its note, and the note now says the thing a reader cannot see.

### TypeScript: question 1 doing the work

Every comment here is arguably "a why", and every one is still avoidable.

```ts
export const submit = async (form: FormValues) => {
  // trim and lowercase so the exact-match lookup finds the user
  const e = form.email.trim().toLowerCase();

  // 3 attempts, then give up
  for (let i = 0; i < 3; i++) {
    // build the payload the v2 endpoint expects
    const body = {
      email: e,
      display_name: form.name,
      role_ids: form.roles.map((r) => r.id),
    };

    const res = await fetchJson("/v2/users", { body });
    if (res.ok) return res;
  }
};
```

After:

```ts
const MAX_ATTEMPTS = 3;

const toV2UserPayload = (form: FormValues, email: string) => ({
  email,
  display_name: form.name,
  role_ids: form.roles.map((role) => role.id),
});

export const submit = async (form: FormValues) => {
  // The user lookup is exact-match and the CRM exports mixed case.
  const normalizedEmail = form.email.trim().toLowerCase();

  for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
    const res = await fetchJson("/v2/users", { body: toV2UserPayload(form, normalizedEmail) });
    if (res.ok) return res;
  }
};
```

Three of the four comments became code: a constant, a function name, and a variable name. The fourth stayed because the reason lives in two systems outside this file. Note that the rename to `normalizedEmail` already carried the *what*, so the comment shrank to the *why* alone, which is the only part it was ever needed for.

## Design notes are not comments

A design note records why you chose this approach over another. It is genuinely valuable and it does not belong in the source, because the source is the one place it cannot be checked, tested, or retired.

| Information | Where it belongs |
|---|---|
| Why this approach beat the alternative | PR description, or an ADR for a decision with reach |
| The edge case that made the alternative wrong | A test named for that edge case |
| A constraint imposed by another system | A comment, with the ticket or spec cited |
| What is still left to do | A ticket, or a TODO that names it |
| What changed in this edit | The commit message |

The test is the strongest of these. `it("keeps the bucket key stable across a DST boundary")` fails when someone breaks the property; `// setDate, not a fixed stride: DST` sits there being true, then sits there being false.

## Hard judgment calls

**Section headers in a very long file.** Delete them. They are a symptom, and the fix is splitting the file. If splitting is out of scope, say so in the report rather than silently keeping the banners as a compromise.

**Intentional duplication.** Genuinely a keeper, and one of the few cases where the same why appears twice legitimately. Put it in one place, at the copy that would be deleted first by someone tidying up, and reference the other location. Do not write it at both sites.

**Comments in tests.** A test name is the comment. `// Arrange / // Act / // Assert` is structure that the test's shape already shows. What does earn a comment in a test is a non-obvious setup requirement, for example why a specific fixture value triggers the bug, or why an assertion is loose.

**Comments in config and infrastructure files.** The bar is lower here, not higher. A magic number in a Terraform file, a Docker layer ordered a certain way for cache reasons, or a CI step with a non-obvious dependency all benefit, because the surrounding language has almost no expressive power to carry intent. Delete the restatements, keep the rationale.

**Type definition files.** Field-level docs on a shared domain type are often the only documentation a consumer will find, and consumers may be in another repo. Hold these to the "adds what the type cannot" test, but expect more of them to pass it than elsewhere.

**A comment that is the only record of a bug.** `// Do not remove: prevents the double-submit from PROJ-221.` Never delete this class of comment on the theory that the code looks redundant. That comment is the reason the code looks redundant. If it seems wrong, verify before touching it, and if verifying is not possible, flag it.

**Copy that happens to be in a comment.** Placeholder text, i18n notes, or a translator hint. Not a code comment; leave it.

**Disagreement with the user.** If asked to remove a comment that is genuinely load-bearing, say which one and why in a sentence, then do as asked. It is their codebase.

## Sources

- John Ousterhout, *A Philosophy of Software Design*, ch. 12 to 16 (comments, comment style, modifying existing code, comments and names).
- Robert C. Martin, *Clean Code*, ch. 4 (comments).
- Google engineering practices, [what to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html): comments should explain why rather than what, and are distinct from API documentation, which states purpose, usage, and behavior.
- *Software Engineering at Google*, ch. 9: if a reviewer does not understand why the code does something, that is a signal for better structure or better comments, in that order.
