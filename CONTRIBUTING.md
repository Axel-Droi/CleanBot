# Contributing to CleanBot

Thank you for your interest in contributing. Whether you're fixing a bug, improving the model, or adding new features, this guide will help you get started.

## Ground Rules

- Be respectful and constructive in all discussions.
- Open an issue before starting significant work so we can align on direction.
- All contributions must respect CleanBot's privacy-first design: no code that enables face detection, license plate recognition, or persistent image storage may be merged.

## How to Contribute

### 1. Fork & Clone

```bash
git clone https://github.com/your-username/CleanBot.git
cd CleanBot
```

### 2. Create a Branch

Use a descriptive name:

```bash
git checkout -b feat/improve-plastic-detection
git checkout -b fix/navigation-collision-edge-case
git checkout -b docs/add-hardware-setup-guide
```

### 3. Set Up the Development Environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Make Your Changes

- Keep commits focused and atomic.
- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code.
- Add or update tests for any logic you change.

### 5. Run Tests

```bash
pytest tests/ -v
```

### 6. Open a Pull Request

Fill out the PR template completely. Link the relevant issue. PRs without a description or failing tests will not be reviewed.

## Areas Where Help is Welcome

- **Vision model** — improving mAP on the 4 waste classes, handling edge cases (wet trash, partial occlusion, night conditions).
- **RL navigation** — faster convergence, better reward shaping, sim-to-real transfer.
- **Dashboard** — real-time map updates, bin fill-level alerts, route optimization visualization.
- **Hardware** — motor control reliability, power management, chassis documentation.
- **Docs** — setup guides, architecture diagrams, deployment walkthroughs.

## Reporting Bugs

Open a [bug report](.github/ISSUE_TEMPLATE/bug_report.md) issue and include:
- Steps to reproduce
- Expected vs. actual behavior
- Environment (OS, Python version, hardware if relevant)
- Relevant logs or screenshots

## Commit Style

```
type(scope): short description

Optional longer explanation if needed.
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

Example: `fix(vision): reduce false positives on wet pavement`
