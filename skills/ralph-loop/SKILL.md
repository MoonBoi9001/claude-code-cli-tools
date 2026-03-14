---
name: ralph-loop
description: Autonomous coding workflow using Claude in a bubblewrap sandbox with iterative execution. Use when the user mentions a ralph loop, setting up a ralph loop, or designing prompts for autonomous work.
---

# Ralph Loop

The ralph loop is an autonomous coding workflow where Claude runs iteratively inside a bubblewrap sandbox with `--dangerously-skip-permissions`. Each iteration Claude reads a prompt and progress file, does work, commits changes, and continues until done. The goal isn't to finish in one cycle -- it's to force Claude to keep iterating on a task until completion reaches an exceptional standard.

## claude-tools

The loop infrastructure comes from [claude-tools](https://github.com/edgeandnode/claude-tools), which provides two scripts that should be installed on PATH:

**`loop`** -- The orchestrator. Runs Claude iteratively in a sandbox, pipes output through clox for real-time viewing, and manages iteration state. Supports two prompt modes: `-f <prompt-file>` for a raw prompt file, or `-s <file>` to have Claude study task files (repeatable). Accepts `-n` for max iterations (default 20) and `-d` for a custom state directory. The loop exits when Claude creates a stop file, max iterations are reached, or Claude errors.

**`sandbox`** (symlinked to `sandbox/bubblewrap`) -- The bubblewrap wrapper. Creates an isolated environment with read-only system directories, read-write access to the current git repo, isolated PID namespace, resource limits via prlimit, and a clean environment. Detects the git root automatically, handles git worktrees, and works with any repo. Network stays shared (needed for package managers).

**`clox`** is a required dependency -- a TUI viewer that renders Claude's JSON stream output in real-time so you can watch it work, or review past sessions offline.

Usage examples:

```bash
loop -f PROMPT.md              # Run with a prompt file
loop -f PROMPT.md -n 10        # Cap at 10 iterations
loop -s PLAN.md                # Study a plan file, work through tasks
loop -s PLAN.md -s SPEC.md     # Multiple study files
touch target/loop/stop          # Stop early
clox target/loop/iter-0.json   # Review a past iteration
```

## Server Inventory

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

**Do NOT reinstall claude, clox, bwrap, node, or npm.** They are already present and working. If a non-interactive SSH check reports them missing, it's a PATH issue -- verify with `bash -l -c "which claude"`.

**OAuth token expiry**: Tokens expire periodically and headless mode (`-p`) cannot refresh them. Refresh interactively: SSH into the server, then run `claude > /login > /exit`. Verify with `claude -p "say hello"`. Must be done outside sandbox since `~/.claude.json` is mounted read-only.

**Custom scripts**: `~/ralph-loop/` contains the Ubuntu-adapted sandbox (`sandbox.sh`, symlinked as `sandbox` on PATH) and a project-specific `loop.sh` with post-iteration verification and auto-deploy. The generic `loop` from claude-tools is preferred -- verification logic belongs in the prompt instead.

## Running a Loop

1. **Write `PROMPT.md`** in the project root -- the task description Claude reads each iteration. Should instruct Claude to read `PROGRESS.md`, do work, commit, update progress, verify (build/lint/test), and signal completion by creating `target/loop/stop`.
2. **Write or reset `PROGRESS.md`** -- tracks what's been done across iterations. Claude reads this at the start of each cycle to know where it left off.
3. **Push to the server** -- `git push`, then `ssh <user>@<server>` and `cd ~/ProjectName && git pull`.
4. **Run the loop** -- start inside a **tmux session**. Do NOT use `nohup`, `&`, or backgrounded SSH commands -- clox is a TUI that requires a real terminal and will fail with "Failed to enable raw mode" if stdout is not a TTY. Use: `tmux new-session -s ralph "cd ~/ralph-loop && ./loop.sh -n 20"`. The loop script auto-detects whether a TTY is present and skips clox if not, but you lose the real-time rendering.
5. **Monitor** -- attach to the tmux session with `ssh <user>@<server> -t tmux attach -t ralph`. Check `target/loop/progress.txt` for timing. Create `target/loop/stop` to halt early.
6. **Review** -- iteration logs at `target/loop/iter-N.json`, viewable with `clox target/loop/iter-0.json`.

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

Describe what the feature should do and why, not how. Claude follows instructions literally -- specifying an exact file to edit prevents it from considering a cleaner structure. Provide architectural context, leave implementation open, but keep real constraints explicit (don't bundle images, keep the dark theme, etc.).

### Commit granularity

Without explicit instruction, Claude might incorrectly batch all work into one commit. Prompts should instruct it to commit after each logical unit of work -- one per sub phase, feature, or milestone. A 6-phase prompt should ideally produce more than 6 commits.

## QA Testing

Build success, linting, and passing tests are necessary but insufficient -- they say nothing about runtime correctness. Prompts should include a QA step that verifies actual output: browser testing for frontends, curl/httpie for APIs, manual invocation for CLIs, etc. Use MCP tools (browser automation, HTTP clients) when available. At minimum, instruct Claude to exercise changed functionality and verify results before marking a phase complete.
