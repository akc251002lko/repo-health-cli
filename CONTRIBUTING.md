# Contributing to Repo Health CLI

Thank you for your interest in contributing to Repo Health CLI.

Contributions are welcome, including bug fixes, improvements, documentation updates, tests, and feature suggestions.

This document explains the standards and procedures for contributing to the project.

## Project Goals

Repo Health CLI aims to provide a lightweight and reliable tool for evaluating the structural health of public GitHub repositories.

Contributions should support the following principles:

- Keep the application lightweight.
- Maintain compatibility with Python 3.9 and newer.
- Use Python's standard library whenever possible.
- Keep the code readable, maintainable, and well-tested.
- Provide clear error messages.
- Preserve backward compatibility where practical.

## Types of Contributions

The following contributions are welcome:

- Bug fixes and error-handling improvements.
- Performance and reliability improvements.
- Additional automated tests.
- Documentation improvements.
- Command-line usability enhancements.
- Improvements to repository analysis.
- New features aligned with the project's goals.

## Reporting Bugs

Before reporting a bug:

1. Check whether the issue has already been reported.
2. Confirm that you are using a supported Python version.
3. Try to reproduce the problem.

When submitting a bug report, include:

- A clear description of the problem.
- Steps to reproduce the issue.
- Expected behaviour.
- Actual behaviour.
- Python version.
- Operating system.
- Relevant error messages or output.

Never include passwords, personal access tokens, or other sensitive credentials in an issue report.

## Suggesting Features

Feature suggestions should explain:

- The problem or limitation being addressed.
- The proposed solution.
- Expected benefits.
- Possible alternatives, if applicable.

New features should remain consistent with the project's lightweight design and primary purpose.

## Development Requirements

Contributions must follow these standards:

- Python 3.9 compatibility is required.
- Prefer standard-library modules.
- Avoid unnecessary third-party dependencies.
- Follow PEP 8 conventions where practical.
- Use descriptive variable and function names.
- Keep functions focused and maintainable.
- Handle expected errors explicitly.
- Avoid hardcoded credentials and sensitive information.
- Preserve existing command-line behaviour unless a change is intentional and documented.

## Testing Requirements

Automated tests are required for changes that affect application behaviour.

The project uses Python's built-in `unittest` framework.

Run the complete test suite:

```bash
python -m unittest discover -s tests -v
```

Check Python syntax:

```bash
python -m py_compile health.py tests/test_health.py
```

Before submitting a contribution:

- Ensure existing tests pass.
- Add tests for new functionality.
- Add regression tests for fixed bugs.
- Avoid tests that depend on live GitHub API availability.
- Verify that mocked API responses cover relevant error conditions.

GitHub Actions automatically checks compatibility across Python 3.9, 3.10, 3.11, 3.12, and 3.13.

All required CI checks should pass before a contribution is considered ready for review.

## Pull Request Guidelines

When submitting a pull request:

1. Keep changes focused on a specific improvement.
2. Explain the purpose of the changes.
3. Describe important implementation decisions.
4. Include relevant tests.
5. Update documentation when necessary.
6. Ensure automated checks pass.
7. Reference related issues when applicable.

Avoid combining unrelated changes in a single pull request.

## Commit Message Convention

Use clear and descriptive commit messages.

Suggested prefixes:

| Prefix | Purpose |
|---|---|
| `feat:` | New functionality |
| `fix:` | Bug fixes |
| `docs:` | Documentation changes |
| `test:` | Test-related changes |
| `refactor:` | Code restructuring |
| `chore:` | Maintenance and configuration |

Examples:

```text
feat: add repository metadata checks
fix: improve GitHub API error handling
docs: update usage instructions
test: expand API error coverage
refactor: simplify repository validation
```

## Security Guidelines

Security is important to this project.

Contributors must:

- Never commit passwords, API tokens, or private credentials.
- Avoid exposing sensitive information in logs or error messages.
- Report security vulnerabilities privately to the project maintainer.
- Avoid introducing unnecessary network access or dependencies.
- Preserve safe handling of external API responses.

Do not publish details of an unpatched security vulnerability in a public issue.

## Project Scope

Repo Health CLI currently focuses on structural repository assessment.

Its scoring system checks for the presence of predefined files and directories.

Contributions should not describe the score as a complete measurement of repository security, code quality, or maintenance activity.

Any expansion of the scoring methodology should include appropriate tests and documentation.

## Code Review

Contributions may be reviewed for:

- Correctness.
- Readability.
- Maintainability.
- Test coverage.
- Python version compatibility.
- Security implications.
- Alignment with project goals.

Changes may be requested before a contribution is accepted.

## License

By submitting a contribution, you agree that your contribution will be distributed under the project's existing MIT License.

See the `LICENSE` file for details.

---

Thank you for helping improve Repo Health CLI.