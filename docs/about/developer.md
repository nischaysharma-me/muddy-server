# Developer Guidelines & Conventions 🛠️

This document outlines engineering standards, environment setup, testing practices, and Git workflows for developing and maintaining **Muddy Server**.

---

## 💻 1. Local Development Setup

### Prerequisites
- **Python >= 3.12**
- **uv** (Extremely fast Python package manager)
- **Git**

### Installation
```bash
# Clone the repository
git clone git@github.desktop.com:nischaysharma-me/muddy-server.git
cd muddy-server

# Create virtual environment with Python 3.12
uv venv --python 3.12 .venv
source .venv/bin/activate

# Install in editable mode with development dependencies
uv pip install -e .

# Setup environment configuration
cp .env.example .env
```

### Running the Development Server
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)  
Interactive Markdown Portal: [http://localhost:8000/documentation](http://localhost:8000/documentation)

---

## 🌿 2. Git Workflow & Branching Strategy

### The Golden Rule
> **NEVER push commits directly to `main` or `master`.**  
> Every feature, fix, or refactor must be developed on a dedicated feature branch, covered by automated tests, and merged via a Pull Request linked to an issue.

### Branch Naming Convention
Branches must follow the pattern `<username>/<feature-name>`:
- `nishuns/feat-openrouter-gateway`
- `nishuns/feat-transactional-pipelines`
- `nishuns/fix-memory-queue-cancellation`
- `nishuns/docs-api-endpoints`

### Semantic Commit Messages
All commit messages must include a type tag and clear description:
- `feat(ai): integrate OpenRouter model alias resolver`
- `fix(queue): resolve race condition in task cancellation`
- `refactor(db): optimize connection pool settings for Postgres`
- `docs(api): add cURL examples for compute endpoints`
- `test(pipeline): add failure rollback recovery test`

---

## 🧪 3. Testing Standards

Muddy Server enforces rigorous automated test coverage. All tests run via `pytest` with `pytest-asyncio`:

```bash
# Run the entire test suite
uv run pytest -v

# Run specific unit tests
uv run pytest tests/unit/test_pipeline_runner.py -v

# Run integration tests
uv run pytest tests/integration/test_compute_api.py -v
```

### Writing Tests
1. **Mock AI in Unit Tests**: Always use `provider="mock"` in tests to avoid incurring API costs or requiring live network credentials.
2. **Database Isolation**: Unit tests utilize `aiosqlite` in-memory/temp databases, initialized via `await init_db()` in pytest fixtures.
3. **Async Fixtures**: Mark asynchronous test functions with `@pytest.mark.asyncio`.

---

## 📐 4. Code Standards & Architecture Rules

1. **No Top-Level Heavy Imports**:
   - Never write `import torch`, `import transformers`, or `import ray` at the top level of any module loaded on startup.
   - All heavy compute/ML libraries must be dynamically imported inside methods guarded by `if settings.ENABLE_*:`.
2. **Layer Separation**:
   - Controllers (`app/api/`) only handle HTTP request parsing, status codes, and DTO conversion.
   - Services (`app/services/`) execute business logic, persistence, and telemetry.
   - Providers (`app/providers/`) interact with external SDKs and low-level compute engines.
3. **Type Annotations**:
   - Every function signature must contain explicit type hints (`typing.Optional`, `typing.List`, `typing.Dict`, `typing.Any`).
