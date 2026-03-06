---
name: ansi-table
description: >
  Present tabular data as color-coded ANSI tables in the terminal. Use when the user asks to
  display, visualise, or print data from CSV, parquet, dataframes, or any structured data source
  as a formatted table. Also trigger when presenting analysis results, sweep matrices, comparison
  grids, or monthly/yearly breakdowns.
allowed-tools:
  - Bash
  - Read
argument-hint: "[path-to-data or description]"
---

# ANSI Table Presentation

Present tabular data as beautifully formatted, color-coded tables in the terminal using inline Python.

## Principles

- Keep analysis scripts producing clean data (CSV/parquet). Do presentation formatting in separate inline Python (`python3 -c "..."`) so the data pipeline stays reusable.
- Always read from the data source (CSV, parquet, JSON) rather than hardcoding values.
- Use `pandas` for data loading when available; fall back to `csv` stdlib if not.

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

Build border strings dynamically based on the number of columns. Do not hardcode table widths.

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
import pandas as pd

df = pd.read_csv('data.csv')
rows = ['row1', 'row2', 'row3']
cols = ['col1', 'col2', 'col3']

for _, record in df.iterrows():
    title = record['name']
    print(f'  \033[1m{title}\033[0m')
    print()

    # Build dynamic borders
    top = '  \u250c' + '\u2500' * 18
    hdr = '  \u2502' + ' ' * 18
    mid = '  \u251c' + '\u2500' * 18
    bot = '  \u2514' + '\u2500' * 18

    for c in cols:
        top += '\u252c' + '\u2500' * 8
        hdr += '\u2502 ' + f'{c:>5s}' + '  '
        mid += '\u253c' + '\u2500' * 8
        bot += '\u2534' + '\u2500' * 8

    top += '\u2510'; hdr += '\u2502'
    mid += '\u2524'; bot += '\u2518'

    print(top); print(hdr); print(mid)

    for i, r in enumerate(rows):
        line = f'  \u2502 {r:<16s} '
        for c in cols:
            v = record[f'{r}_{c}']
            if v >= 25:
                cell = f'\033[31m{v:>5.1f}%\033[0m'
            elif v >= 15:
                cell = f'\033[33m{v:>5.1f}%\033[0m'
            else:
                cell = f'\033[32m{v:>5.1f}%\033[0m'
            line += f'\u2502 {cell} '
        line += '\u2502'
        print(line)
        if i < len(rows) - 1:
            print(mid)

    print(bot); print()
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

Adjust cell width to fit the widest value in each column plus padding.
