# Ralph Loop

The ralph loop is an autonomous coding workflow where Claude runs iteratively inside a bubblewrap sandbox with `--dangerously-skip-permissions`. Each iteration Claude reads a prompt and progress file, does work, commits changes, and continues until done. The goal isn't to finish in one cycle — it's to force Claude to keep iterating on a task until completion reaches an exceptional standard.

## claude-tools

The loop infrastructure comes from [claude-tools](https://github.com/edgeandnode/claude-tools), which provides two scripts that should be installed on PATH:

**`loop`** — The orchestrator. Runs Claude iteratively in a sandbox, pipes output through clox for real-time viewing, and manages iteration state. Supports two prompt modes: `-f <prompt-file>` for a raw prompt file, or `-s <file>` to have Claude study task files (repeatable). Accepts `-n` for max iterations (default 20) and `-d` for a custom state directory. The loop exits when Claude creates a stop file, max iterations are reached, or Claude errors.

**`sandbox`** (symlinked to `sandbox/bubblewrap`) — The bubblewrap wrapper. Creates an isolated environment with read-only system directories, read-write access to the current git repo, isolated PID namespace, resource limits via prlimit, and a clean environment. Detects the git root automatically, handles git worktrees, and works with any repo. Network stays shared (needed for package managers).

**`clox`** is a required dependency — a TUI viewer that renders Claude's JSON stream output in real-time so you can watch it work, or review past sessions offline.

Usage examples:
```bash
loop -f PROMPT.md              # Run with a prompt file
loop -f PROMPT.md -n 10        # Cap at 10 iterations
loop -s PLAN.md                # Study a plan file, work through tasks
loop -s PLAN.md -s SPEC.md     # Multiple study files
touch target/loop/stop          # Stop early
clox target/loop/iter-0.json   # Review a past iteration
```

## Server Inventory (82.68.33.149, user: mainuser)

Everything needed to run ralph loops is already installed:

| Tool | Location | Notes |
|------|----------|-------|
| `claude` | `~/.local/bin/claude` | Native installer, not npm global |
| `clox` | `~/.local/bin/clox` | Pre-built binary |
| `bwrap` | `/usr/bin/bwrap` | System package |
| `loop` | `~/.local/bin/loop` | Symlink to `~/claude-tools/bin/loop` |
| `sandbox` | `~/.local/bin/sandbox` | Symlink to `~/ralph-loop/sandbox.sh` (Ubuntu-adapted, has npm cache + NODE_OPTIONS) |
| `node` | `/usr/local/bin/node` | v24, installed via `npx n lts` |
| `npm` | `/usr/local/bin/npm` | v11 |
| `cargo` | `~/.cargo/bin/cargo` | For building Rust tools if needed |

**AppArmor**: A profile at `/etc/apparmor.d/bwrap` grants bubblewrap permission to create unprivileged user namespaces (Ubuntu 24.04 restricts this by default).

**PATH in login shell**: `~/.local/bin:~/.cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`. Non-interactive SSH shells won't source the profile, so always use `bash -l -c "..."` or run scripts from an interactive session.

**Do NOT reinstall claude, clox, bwrap, node, or npm.** They are already present and working. If a non-interactive SSH check reports them missing, it's a PATH issue — verify with `bash -l -c "which claude"`.

**OAuth token expiry**: Claude's OAuth token expires periodically. Headless mode (`-p`) cannot refresh it — it will fail with "OAuth token has expired." To fix: SSH in interactively, run `claude` to open an interactive session, then type `/login` inside the session. Exit with `/exit`. Verify with `claude -p "say hello"`. The sandbox mounts `~/.claude.json` read-only, so the token must be refreshed outside the sandbox before starting a loop.

**Custom scripts**: `~/ralph-loop/` contains the Ubuntu-adapted sandbox (`sandbox.sh`, symlinked as `sandbox` on PATH) and a project-specific `loop.sh` with post-iteration verification and auto-deploy. The generic `loop` from claude-tools is preferred — verification logic belongs in the prompt instead.

## Running a Loop

1. **Write `PROMPT.md`** in the project root — the task description Claude reads each iteration. Should instruct Claude to read `PROGRESS.md`, do work, commit, update progress, verify (build/lint/test), and signal completion by creating `target/loop/stop`.
2. **Write or reset `PROGRESS.md`** — tracks what's been done across iterations. Claude reads this at the start of each cycle to know where it left off.
3. **Push to the server** — `git push`, then `ssh mainuser@82.68.33.149` and `cd ~/ProjectName && git pull`.
4. **Run the loop** — start inside a **tmux session**. Do NOT use `nohup`, `&`, or backgrounded SSH commands — clox is a TUI that requires a real terminal and will fail with "Failed to enable raw mode" if stdout is not a TTY. Use: `tmux new-session -s ralph "cd ~/ralph-loop && ./loop.sh -n 20"`. The loop script auto-detects whether a TTY is present and skips clox if not, but you lose the real-time rendering.
5. **Monitor** — attach to the tmux session with `ssh mainuser@82.68.33.149 -t tmux attach -t ralph`. Check `target/loop/progress.txt` for timing. Create `target/loop/stop` to halt early.
6. **Review** — iteration logs at `target/loop/iter-N.json`, viewable with `clox target/loop/iter-0.json`.

## Prompt Design

Verification logic belongs in the prompt, not the loop script. This keeps the loop generic and lets Claude adapt verification per-project. A good prompt should:

- Tell Claude to read `PROGRESS.md` first to understand current state
- Describe the task with enough context for independent work
- Specify what "done" looks like (acceptance criteria)
- Instruct Claude to run verification (build, lint, test) and fix failures before moving on
- Instruct Claude to commit after completing work
- Instruct Claude to update `PROGRESS.md` with what was accomplished
- Instruct Claude to create `target/loop/stop` when all work is complete

### Outcome-focused over prescriptive

Prompts produce better results when they describe the desired outcome rather than dictating implementation steps. Claude follows instructions literally — if you tell it to maintain backwards compatibility, it will, even when the old code path has no consumers. If you specify an exact file to edit, it won't consider whether a new file would be cleaner.

Describe what the feature should do and why, provide architectural context so Claude can make informed decisions, but leave the "how" open. Claude reasons better when it has room to evaluate tradeoffs rather than executing a checklist. Constraints that matter (don't bundle images, don't modify the contract, keep the dark theme) should still be explicit — the goal is fewer unnecessary constraints, not fewer constraints overall.

### Commit granularity

Left to its own devices, Claude will batch all work into a single monolithic commit at the end. This makes it impossible to review, revert, or bisect individual changes. Prompts should explicitly instruct Claude to commit after each logical unit of work — typically one commit per phase, feature, or meaningful milestone. A prompt covering 6 phases should produce at least 6 commits, not one.

## QA Testing

Build success, clean linting, and passing tests are necessary but insufficient. They verify that code compiles and conforms to style rules — they say nothing about whether the result actually works at runtime. A web page can build cleanly and look broken on mobile. An API can pass type checks and return wrong data under specific input. A CLI tool can lint perfectly and crash on edge-case arguments.

Prompts should include a QA step appropriate to the project type. The specific tooling varies — visual testing with a browser for frontends, curl/httpie for APIs, manual invocation for CLI tools — but the principle is the same: verify the output, not just the build. If a loop has access to relevant MCP tools (browser automation, HTTP clients, etc.), use them. If not, at minimum instruct Claude to exercise the changed functionality and verify the result matches expectations before marking a phase complete.
