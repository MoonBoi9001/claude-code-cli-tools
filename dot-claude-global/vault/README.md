# claude-vault

Encrypt Claude Code session transcripts older than 21 days at rest using
`age`. Recent sessions stay plaintext so `claude --resume` keeps working;
older ones get renamed from `foo.jsonl` to `foo.jsonl.age` and the plaintext
is deleted.

## Layout

- `bin/encrypt-old-sessions` — non-interactive. Runs on `SessionStart`. Uses
  the public recipient key only, no network needed.
- `bin/decrypt-session` — on-demand. Takes one or more session ids or paths
  and pipes the plaintext to stdout by default (never writes to disk). Pass
  `--write` to restore plaintext alongside the `.age` file instead (for
  un-archiving a session for `claude --resume`).

Personal config (recipient key, private vault repo slug, log path) lives
outside this repo in `~/.claude/vault-local/` and is not version-controlled
here. The scripts source `~/.claude/vault-local/config.sh` at runtime and
exit cleanly if it's missing.

## First-time setup

You need `age` (`brew install age`) and an authenticated `gh` CLI.

1. **Generate your keypair**:

   ```bash
   mkdir -p ~/.claude/vault-local && chmod 700 ~/.claude/vault-local
   TMP=$(mktemp -d -t claude-vault.XXXXXX)
   age-keygen -o "$TMP/identity.txt"
   grep '^# public key: ' "$TMP/identity.txt" | sed 's/^# public key: //' \
       > ~/.claude/vault-local/recipient.txt
   chmod 600 ~/.claude/vault-local/recipient.txt
   ```

2. **Create a private vault repo** for your identity (replace `YOU`):

   ```bash
   gh repo create YOU/your-vault-repo --private
   cd "$TMP"
   git init && git remote add origin "https://github.com/YOU/your-vault-repo.git"
   git add identity.txt && git -c commit.gpgsign=false commit -m "identity"
   git push -u origin HEAD
   cd - >/dev/null
   rm -rf "$TMP"
   ```

3. **Write your local config** at `~/.claude/vault-local/config.sh`:

   ```bash
   # shellcheck shell=bash
   export CLAUDE_VAULT_REPO="YOU/your-vault-repo"
   export CLAUDE_VAULT_RECIPIENT="$HOME/.claude/vault-local/recipient.txt"
   export CLAUDE_VAULT_LOG="$HOME/.claude/vault-local/encrypt.log"
   export CLAUDE_VAULT_CUTOFF_DAYS="21"
   ```

4. **Symlink the public scripts** into `~/.claude/`:

   ```bash
   ln -s "$PWD/dot-claude-global/vault" ~/.claude/vault
   ```

5. **Wire the `SessionStart` hook** in `~/.claude/settings.json`:

   ```json
   "SessionStart": [
     {
       "hooks": [
         { "type": "command",
           "command": "~/.claude/vault/bin/encrypt-old-sessions",
           "async": true }
       ]
     }
   ]
   ```

6. **Dry-run first**:

   ```bash
   CLAUDE_VAULT_DRY_RUN=1 ~/.claude/vault/bin/encrypt-old-sessions
   tail -20 ~/.claude/vault-local/encrypt.log
   ```

   Then run without `CLAUDE_VAULT_DRY_RUN` to encrypt the backlog.

## Usage

After setup, encryption runs on every Claude Code session start via the hook.

Decrypt a session on demand (plaintext is piped to stdout — nothing lands
on disk):

```bash
~/.claude/vault/bin/decrypt-session <session-id> | less
~/.claude/vault/bin/decrypt-session /path/to/file.jsonl.age | grep 'foo'

# bulk grep across the encrypted archive:
for f in ~/.claude/projects/**/*.jsonl.age; do
  if ~/.claude/vault/bin/decrypt-session "$f" | grep -q 'foo'; then
    echo "$f"
  fi
done
```

To restore plaintext alongside the `.age` (for example, to un-archive a
session so `claude --resume` can read it), pass `--write`:

```bash
~/.claude/vault/bin/decrypt-session --write <session-id>
```

## Behaviour notes

- If `~/.claude/vault-local/config.sh` is missing, `encrypt-old-sessions`
  exits 0 with a stderr hint — `SessionStart` won't fail, and your JSONL
  files stay plaintext until you finish setup.
- If `CLAUDE_VAULT_REPO` is unset when you invoke `decrypt-session`, it
  exits 1 with a setup message.
- Renamed `.age` files aren't recognised by Claude Code's built-in
  `cleanupPeriodDays` cleanup, so the encrypted archive is retained
  independently of that setting.
- When `decrypt-session --write` restores plaintext alongside a `.age`, it
  sets the plaintext mtime to match the `.age`. On the next `SessionStart`,
  `encrypt-old-sessions` reconciles any both-exist pair: plaintext
  strictly newer than the `.age` gets re-encrypted (capturing resumed
  sessions or manual edits) and replaces the `.age`; matching or older
  mtimes are treated as stale decrypt artifacts and the plaintext is
  dropped. This runs on every `SessionStart`, regardless of cutoff age,
  so the archive self-heals from forgotten decrypts.
