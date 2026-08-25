# Developer Guidelines & Conventions 🛠️

Guidelines for contributing to and maintaining **Muddy Server**.

---

## 🌿 Git & Branching Strategy
- **Branch Naming**: `<username>/<feature-name>` (e.g. `nishuns/feat-docs-engine-and-documentation`).
- **Commits**: Strictly follow semantic commit conventions: `feat():`, `fix():`, `refactor():`, `docs():`, `test():`.
- **Pull Requests**: Never push directly to `main`. Every change must go through a PR linking its respective GitHub issue.

---

## 🧪 Testing Standard
- Tests are executed with `pytest` and `pytest-asyncio`:
  ```bash
  uv run pytest -v
  ```
- All new features must include unit tests in `tests/unit/` or integration tests in `tests/integration/`.
