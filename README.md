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