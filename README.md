# Repo Health CLI

A lightweight, zero-dependency Python command-line tool that evaluates public GitHub repositories against a predefined set of open-source repository best practices.

Repo Health CLI analyzes repository structure, checks for essential project files and directories, calculates a health score, and generates human-readable or JSON reports.

## Features

- Analyze publicly accessible GitHub repositories.
- Check essential documentation and configuration files.
- Detect missing repository directories.
- Calculate a weighted repository health score.
- Generate readable terminal reports.
- Export machine-readable JSON reports.
- Provide clear error messages for API and network failures.
- Detect incomplete GitHub repository tree responses.
- Support configurable API request timeouts.
- Run without third-party Python dependencies.

## Requirements

- Python 3.9 or newer.
- Internet connection.
- Access to the GitHub REST API.
- A publicly accessible GitHub repository.

## Installation

Clone the repository:

```bash
git clone https://github.com/akc251002lko/repo-health-cli.git
```

Navigate into the project directory:

```bash
cd repo-health-cli
```

No additional package installation is required.

## Usage

Analyze a repository:

```bash
python health.py --repo psf/requests
```

The tool retrieves repository metadata and its recursive file tree, evaluates the configured checks, and displays a health report.

### JSON Output

Generate a machine-readable JSON report:

```bash
python health.py --repo psf/requests --json
```

JSON output is useful for scripts, automation, and other tools that consume structured data.

### Custom Timeout

Set the API request timeout in seconds:

```bash
python health.py --repo psf/requests --timeout 30
```

The default timeout is 15 seconds.

The timeout must be a finite number greater than zero.

## Command-Line Arguments

| Argument | Required | Description |
|---|---|---|
| `--repo` | Yes | GitHub repository in `owner/name` format |
| `--timeout` | No | API request timeout in seconds; default is 15 |
| `--json` | No | Output the report as JSON |
| `--help` | No | Display command-line help |

## Health Scoring Methodology

Repo Health CLI uses a weighted scoring system with a maximum score of 100 points.

Each check contributes its assigned points when the required file or directory is detected in the repository tree.

| Requirement | Points |
|---|---:|
| README.md | 20 |
| LICENSE | 20 |
| CONTRIBUTING.md | 15 |
| CODE_OF_CONDUCT.md | 15 |
| .gitignore | 10 |
| .github/ISSUE_TEMPLATE | 10 |
| .github/workflows | 10 |
| **Total** | **100** |

### Score Interpretation

| Score | Status |
|---|---|
| 80–100 | Excellent |
| 50–79 | Needs Improvement |
| 0–49 | Poor |

### How Checks Work

The application retrieves the repository's recursive Git tree through the GitHub REST API.

It evaluates:

- Files by their exact repository paths and file types.
- Directories by their presence in the returned tree or by the presence of descendants.

A directory is considered present when its directory entry or at least one descendant is detected.

## Important Scoring Limitations

The health score measures the presence of predefined repository files and directories.

It does not evaluate:

- Documentation quality or completeness.
- Whether a license is legally appropriate.
- Whether contribution guidelines are followed.
- The quality of source code.
- Test coverage or test effectiveness.
- Workflow correctness or security.
- Repository maintenance activity.
- The overall security or reliability of a project.

A score of 100/100 therefore means that all seven structural checks passed. It does not guarantee that a repository is fully healthy, secure, or professionally maintained.

## Error Handling

The application handles common operational failures, including:

- Invalid repository identifiers.
- Repositories that cannot be accessed.
- GitHub API authentication errors.
- GitHub API rate limits and access restrictions.
- Network failures.
- Request timeouts.
- Invalid API JSON responses.
- Missing default branches.
- Invalid repository tree responses.
- Truncated recursive tree responses.

Errors are reported without exposing unnecessary Python tracebacks.

## Project Structure

```text
repo-health-cli/
│
├── health.py
├── tests/
│   └── test_health.py
│
├── .github/
│   └── workflows/
│       └── test.yml
│
├── .gitignore
├── README.md
├── LICENSE
├── CONTRIBUTING.md
└── CODE_OF_CONDUCT.md
```

## Testing

The project uses Python's built-in `unittest` framework.

Run the complete test suite:

```bash
python -m unittest discover -s tests -v
```

Check Python syntax:

```bash
python -m py_compile health.py tests/test_health.py
```

The automated GitHub Actions workflow tests compatibility across:

- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

API requests are mocked in the unit tests, so the test suite does not require live GitHub API access.

## Technology Stack

- **Language:** Python
- **API:** GitHub REST API
- **HTTP Client:** urllib
- **Data Format:** JSON
- **Testing:** unittest
- **Automation:** GitHub Actions

The application uses only Python's standard library and has no third-party runtime dependencies.

## API and Access

The application currently supports publicly accessible repositories without requiring a personal access token.

GitHub API rate limits may restrict repeated requests. If a rate limit is reached, wait before trying again.

Private repository analysis and authenticated API access are not currently supported.

## Contributing

Contributions, bug reports, and feature suggestions are welcome.

Please review [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes.

For community participation guidelines, see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

This project is distributed under the MIT License.

See the [LICENSE](LICENSE) file for details.

---

**Repo Health CLI**

A simple structural health assessment tool for GitHub repositories.