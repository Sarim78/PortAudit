"""Entry point so `python -m portaudit ...` works."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
