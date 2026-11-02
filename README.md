
# repo-health-cli

**A zero-dependency CLI tool for evaluating GitHub repository health.**

repo-health-cli analyzes public GitHub repositories against
seven essential open-source best-practice requirements.

It generates a Health Score out of 100, identifies missing
requirements, and provides actionable recommendations.

## Features

- Zero third-party dependencies.
- GitHub REST API integration.
- Recursive repository tree inspection.
- Seven weighted health checks.
- Terminal progress bar and colored output.
- Machine-readable JSON reports.
- Repository validation and error handling.
- Configurable API timeout.
- Automated unit tests.
- GitHub Actions CI integration.

## Requirements

- Python 3.9+
- Internet connection
- Public GitHub repository

No package installation is required.

## Installation

Clone the repository:

```bash
git clone https://github.com/akc251002lko/repo-health-cli.git
```

Enter the project directory:

```bash
cd repo-health-cli
```

## Usage

Analyze a repository:

```bash
python health.py --repo psf/requests
```

Display help:

```bash
python health.py --help
```

Set a custom API timeout:

```bash
python health.py --repo psf/requests --timeout 30
```

Generate JSON output:

```bash
python health.py --repo psf/requests --json
```

## Scoring System

| Requirement | Points |
|---|---:|
| README.md | 20 |
| LICENSE | 20 |
| CONTRIBUTING.md | 15 |
| CODE_OF_CONDUCT.md | 15 |
| .gitignore | 10 |
| .github/ISSUE_TEMPLATE/ | 10 |
| .github/workflows/ | 10 |
| **Total** | **100** |

## Score Interpretation

| Score | Assessment |
|---|---|
| 80–100 | Excellent |
| 50–79 | Needs Improvement |
| 0–49 | Poor |

The assessment measures file and directory presence,
not the quality or completeness of their contents.

## Project Structure

```text
repo-health-cli/
├── health.py
├── README.md
├── LICENSE
├── .gitignore
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── tests/
│   └── test_health.py
└── .github/
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report.yml
    │   └── feature_request.yml
    └── workflows/
        └── test.yml
```

## Testing

Run the automated test suite:

```bash
python -m unittest discover -s tests -v
```

Validate syntax:

```bash
python -m py_compile health.py
```

## GitHub Actions

GitHub Actions automatically runs the unit tests and
repository health analysis when code is pushed or
a pull request is opened.

## API

This project uses the GitHub REST API:

https://api.github.com

Unauthenticated API rate limits apply.

Only publicly accessible repositories are supported.

## Limitations

The tool evaluates structural repository conventions.
It does not verify license validity, documentation quality,
workflow correctness, application security, or code quality.

A high score is not a security certification.

## License

Distributed under the MIT License.
See [LICENSE](LICENSE) for details.
