# logslice

Fast log filtering and slicing tool with time-range and pattern support.

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/yourname/logslice.git && cd logslice && pip install .
```

---

## Usage

```bash
# Filter logs by time range
logslice --start "2024-01-15 08:00:00" --end "2024-01-15 09:00:00" app.log

# Filter by pattern
logslice --pattern "ERROR|CRITICAL" app.log

# Combine time range and pattern
logslice --start "2024-01-15 08:00:00" --end "2024-01-15 09:00:00" --pattern "ERROR" app.log

# Output to a file
logslice --start "2024-01-15 08:00:00" --pattern "WARN" app.log -o output.log
```

You can also use it as a Python library:

```python
from logslice import slice_logs

results = slice_logs(
    filepath="app.log",
    start="2024-01-15 08:00:00",
    end="2024-01-15 09:00:00",
    pattern="ERROR"
)

for line in results:
    print(line)
```

---

## Features

- ⚡ Fast line-by-line streaming — handles large log files efficiently
- 🕐 Time-range slicing with flexible timestamp formats
- 🔍 Regex pattern matching
- 📂 Supports plain text and `.gz` compressed logs

---

## License

This project is licensed under the [MIT License](LICENSE).