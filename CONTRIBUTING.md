
# Contributing to repo-health-cli

Thank you for your interest in contributing.

We welcome bug reports, feature suggestions, documentation
improvements, and code contributions.

## Development Requirements

- Python 3.9 or higher.
- Git.
- No third-party Python dependencies.

## Getting Started

Fork the repository and clone your fork:

```bash
git clone https://github.com/YOUR_USERNAME/repo-health-cli.git
cd repo-health-cli
```

## Making Changes

1. Create a separate branch for your changes.
2. Keep changes focused and maintainable.
3. Follow standard Python naming conventions.
4. Use only Python standard-library modules.
5. Add or update unit tests when necessary.
6. Update documentation when behavior changes.

## Running Tests

Run:

```bash
python -m unittest discover -s tests -v
```

Validate syntax:

```bash
python -m py_compile health.py
```

## Submitting Changes

1. Commit your changes with a clear message.
2. Push your branch.
3. Open a pull request.
4. Describe the problem and proposed solution.
5. Include relevant testing information.

## Code Quality

Contributions should prioritize:

- Correctness.
- Readability.
- Maintainability.
- Error handling.
- Backward compatibility.

All contributions are subject to project review.

Thank you for helping improve repo-health-cli.
