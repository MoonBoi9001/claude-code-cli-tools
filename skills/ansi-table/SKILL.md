---
name: ansi-table
description: >
  Render new ANSI tables in the terminal from a data source. Use ONLY when the user asks you to
  CREATE, DISPLAY, or PRINT tabular data from CSV, parquet, dataframes, or structured data as a
  formatted table. Also trigger when presenting analysis results, sweep matrices, comparison grids,
  or monthly/yearly breakdowns. Do NOT trigger when the user merely references, discusses, or asks
  questions about an existing table already shown in the conversation.
allowed-tools:
  - Bash
  - Read
argument-hint: "[path-to-data or description]"
---

# ANSI Table Presentation

Present tabular data as beautifully formatted, color-coded tables in the terminal.

**IMPORTANT: Do NOT write a Python script file.** Always render the table directly with a single `Bash(python3 -c "...")` call. Never use the Write tool to create a .py file and then run it.

## Principles

- Render tables inline via `python3 -c "..."` in a single Bash call. No script files.
- Always read from the data source (CSV, parquet, JSON) rather than hardcoding values.
- Use `pandas` for data loading when available; fall back to `csv` stdlib if not.

## Terminal Width

Tables must fit the terminal. Always detect width and constrain output accordingly.

```python
import shutil
term_width = shutil.get_terminal_size((80, 24)).columns
```

**Hard cap**: total table width (including borders and 2-char left indent) must never exceed `term_width`. If the natural column widths would overflow, shrink the widest column(s) and wrap cell text. When a cell's content is wrapped, continuation lines repeat the border characters but leave other columns empty.

**Column sizing strategy**:
1. Compute each column's natural width from the widest value (header or data)
2. Add 2 chars padding per column (1 each side)
3. Add border characters: `num_columns + 1` vertical bars
4. Add 2 chars for left indent
5. If total exceeds `term_width`, reduce the widest column iteratively until it fits, with a minimum column width of 10 characters
6. Wrap cell text in shrunk columns using `textwrap.wrap()`

## Table Construction

Use Unicode box-drawing characters for borders:

| Character | Name | Usage |
|-----------|------|-------|
| `\u250c` | `┌` | Top-left corner |
| `\u2510` | `┐` | Top-right corner |
| `\u2514` | `└` | Bottom-left corner |
| `\u2518` | `┘` | Bottom-right corner |
| `\u251c` | `├` | Left T-junction |
| `\u2524` | `┤` | Right T-junction |
| `\u252c` | `┬` | Top T-junction |
| `\u2534` | `┴` | Bottom T-junction |
| `\u253c` | `┼` | Cross junction |
| `\u2500` | `─` | Horizontal line |
| `\u2502` | `│` | Vertical line |

Build border strings dynamically based on column widths. Do not hardcode table widths.

## Color Coding

Use ANSI escape codes to color-code cell values based on thresholds. Choose thresholds contextually based on what the data represents.

```python
GREEN  = '\033[32m'  # Good / low / within target
YELLOW = '\033[33m'  # Warning / moderate / approaching limit
RED    = '\033[31m'  # Bad / high / exceeding limit
BOLD   = '\033[1m'   # Headers and titles
RESET  = '\033[0m'   # Reset after each colored value
```

When thresholds are not obvious from context, ask the user or use sensible defaults (e.g. terciles of the data range).

## Layout

- Bold the title/header above each table with `\033[1m`
- Include contextual metadata on the title line (e.g. totals, date range, units)
- Separate row/column headers from data with box-drawing borders
- Right-align numeric values within cells
- Use consistent cell widths per column
- Add a blank line between multiple tables

## Example Pattern

```python
python3 -c "
import shutil, textwrap

term_width = shutil.get_terminal_size((80, 24)).columns
INDENT = 2
BOLD = '\033[1m'; RESET = '\033[0m'
GREEN = '\033[32m'; YELLOW = '\033[33m'; RED = '\033[31m'

headers = ['Name', 'Status', 'Description']
rows = [
    ['alpha', 'OK', 'A short description of the first item'],
    ['beta', 'WARN', 'A longer description that might need wrapping in narrow terminals'],
    ['gamma', 'FAIL', 'Another description'],
]

# 1. Compute natural column widths from data
col_widths = [len(h) for h in headers]
for row in rows:
    for i, cell in enumerate(row):
        col_widths[i] = max(col_widths[i], len(cell))

# 2. Add padding (1 each side)
padded = [w + 2 for w in col_widths]

# 3. Check total: indent + borders + padded widths
num_cols = len(headers)
total = INDENT + (num_cols + 1) + sum(padded)

# 4. Shrink widest columns if needed (min 10 inner width)
while total > term_width:
    widest = max(range(num_cols), key=lambda i: padded[i])
    if padded[widest] <= 12:  # min 10 + 2 padding
        break
    padded[widest] -= 1
    total -= 1

inner = [p - 2 for p in padded]  # usable char width per column

# 5. Build helpers
def hline(left, mid, right):
    return ' ' * INDENT + left + mid.join('\u2500' * p for p in padded) + right

def render_row(cells, colors=None):
    wrapped = [textwrap.wrap(c, w) or [''] for c, w in zip(cells, inner)]
    max_lines = max(len(w) for w in wrapped)
    for ln in range(max_lines):
        parts = []
        for i, w in enumerate(wrapped):
            text = w[ln] if ln < len(w) else ''
            color = (colors[i] if colors else '') if ln == 0 or (colors and colors[i]) else ''
            reset = RESET if color else ''
            parts.append(f' {color}{text:<{inner[i]}}{reset} ')
        print(' ' * INDENT + '\u2502' + '\u2502'.join(parts) + '\u2502')

# 6. Print table
print()
print(f'{\" \" * INDENT}{BOLD}Example Table{RESET}')
print()
print(hline('\u250c', '\u252c', '\u2510'))
render_row(headers, [BOLD] * num_cols)
print(hline('\u251c', '\u253c', '\u2524'))
for i, row in enumerate(rows):
    status_color = {\"OK\": GREEN, \"WARN\": YELLOW, \"FAIL\": RED}.get(row[1], '')
    render_row(row, ['', status_color, ''])
    if i < len(rows) - 1:
        print(hline('\u251c', '\u253c', '\u2524'))
print(hline('\u2514', '\u2534', '\u2518'))
print()
"
```

## Multi-table Output

When presenting data with multiple groups (e.g. monthly breakdowns, per-category views):

- Print each group as its own table with a bold title
- Keep column structure consistent across all tables so they visually stack
- Use the same color thresholds across all tables for comparability

## Adapting to Data

- **Percentages**: Right-align, 1 decimal place, append `%`
- **Currency/GRT**: Right-align, comma-separated, appropriate decimal places
- **Counts**: Right-align, comma-separated integers
- **Mixed types**: Align each column independently based on its data type

Adjust cell width to fit the widest value in each column plus padding, then apply the terminal width constraint described above.
