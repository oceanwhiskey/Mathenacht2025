# Mathenacht 2025

This repository contains solutions, helpers, and small scripts for the Mathenacht 2025 problems (puzzles found at https://www.mathenacht.de/).

## Overview

The repo collects individual puzzle solutions as small Python scripts, plus supporting utilities (for example, `primes.py`). The intent is to be simple and runnable locally for study, learning, and verifying puzzle solutions.

## Project Structure

- `1_1.py`, `1_2.py`, ... : Individual puzzle solution scripts.
- `primes.py` : Utility functions for prime-related tasks used by some problems.
- `README.md` : This file.
- `__init__.py` : Package marker (optional).

Files with `.md` (like `1_4.md`) may include notes or problem statements.

## Requirements

- Python 3.8 or newer.

No external packages are required unless a specific puzzle script mentions one; check the top of each script for any imports beyond the standard library.

## Usage

Run a single puzzle script from a terminal (Windows PowerShell example):

```
python 1_1.py
```

To run all puzzle scripts that follow the `1_*.py` pattern in PowerShell:

```
Get-ChildItem -Filter "1_*.py" | ForEach-Object { python $_.FullName }
```

If a script prints results, they will appear in the console. If a script is implemented as a module (no direct output), open the file and check its `if __name__ == '__main__':` block to see how it's intended to be executed.

## Utilities

- `primes.py` contains helper routines for prime checks/generation. Import and reuse functions from it in other scripts.

Example:
```
from primes import is_prime
print(is_prime(17))
```

## Contributing

Contributions, improvements, and corrections are welcome. When adding or updating solutions:

- Keep scripts small and focused on a single problem.
- Add short comments or a brief header explaining the approach.
- If you add third-party dependencies, include them in a `requirements.txt` and document why they are needed.

## License

This repository does not include an explicit license file. If you want to share or reuse these solutions, please add a license or check with the repository owner for permission.

## References

- Original event / problem source: https://www.mathenacht.de/

---

If you'd like, I can also:

- Add a `requirements.txt` if any scripts need packages.
- Add a small test harness or a `run_all.py` script that imports each puzzle and prints structured outputs.

Tell me which option you prefer and I'll make it next.


