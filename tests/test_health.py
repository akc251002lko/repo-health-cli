import io
import json
import socket
import unittest
import urllib.error
from contextlib import redirect_stderr
from unittest.mock import Mock, patch

from health import (
    API_BASE,
    HealthCheckError,
    build_report,
    check_repository,
    fetch_repository_tree,
    github_get,
    main,
    validate_repo,
)


class TestRepositoryValidation(unittest.TestCase):

    def test_valid_repository(self):
        self.assertEqual(
            validate_repo("psf/requests"),
            ("psf", "requests"),
        )

    def test_valid_repository_with_dots_and_hyphens(self):
        self.assertEqual(
            validate_repo("owner-123/my.repo_name"),
            ("owner-123", "my.repo_name"),
        )

    def test_invalid_repository(self):
        with self.assertRaises(HealthCheckError):
            validate_repo("invalid-repository")

    def test_empty_repository(self):
        with self.assertRaises(HealthCheckError):
            validate_repo("owner/")

    def test_empty_owner(self):
        with self.assertRaises(HealthCheckError):
            validate_repo("/repository")

    def test_multiple_slashes(self):
        with self.assertRaises(HealthCheckError):
            validate_repo("owner/repo/extra")

    def test_non_string_repository(self):
        with self.assertRaises(HealthCheckError):
            validate_repo(None)

    def test_invalid_owner_characters(self):
        with self.assertRaises(HealthCheckError):
            validate_repo("invalid_owner/repository")

    def test_repository_ending_in_git(self):
        with self.assertRaises(HealthCheckError):
            validate_repo("owner/repository.git")


class TestHealthScoring(unittest.TestCase):

    def setUp(self):
        self.complete_tree = [
            {"path": "README.md", "type": "blob"},
            {"path": "LICENSE", "type": "blob"},
            {"path": "CONTRIBUTING.md", "type": "blob"},
            {"path": "CODE_OF_CONDUCT.md", "type": "blob"},
            {"path": ".gitignore", "type": "blob"},
            {
                "path": ".github/ISSUE_TEMPLATE",
                "type": "tree",
            },
            {
                "path": ".github/workflows",
                "type": "tree",
            },
        ]

    def test_all_requirements_present(self):
        score, results = check_repository(
            self.complete_tree
        )

        self.assertEqual(score, 100)
        self.assertEqual(len(results), 7)

    def test_empty_repository(self):
        score, results = check_repository([])

        self.assertEqual(score, 0)
        self.assertEqual(len(results), 7)

    def test_partial_score(self):
        tree = [
            {"path": "README.md", "type": "blob"},
            {"path": "LICENSE", "type": "blob"},
        ]

        score, results = check_repository(tree)

        self.assertEqual(score, 40)
        self.assertEqual(
            sum(item["exists"] for item in results),
            2,
        )

    def test_directory_with_descendant(self):
        tree = [
            {
                "path": ".github/ISSUE_TEMPLATE/bug.yml",
                "type": "blob",
            }
        ]

        score, results = check_repository(tree)

        self.assertTrue(results[5]["exists"])
        self.assertEqual(score, 10)

    def test_directory_without_descendant(self):
        tree = [
            {
                "path": ".github/ISSUE_TEMPLATE_EXTRA",
                "type": "tree",
            }
        ]

        score, results = check_repository(tree)

        self.assertFalse(results[5]["exists"])
        self.assertEqual(score, 0)

    def test_wrong_file_type_does_not_pass(self):
        tree = [
            {"path": "README.md", "type": "tree"},
        ]

        score, results = check_repository(tree)

        self.assertFalse(results[0]["exists"])
        self.assertEqual(score, 0)

    def test_malformed_tree_entries_are_ignored(self):
        tree = [
            None,
            {"invalid": "entry"},
            {"path": "README.md", "type": "blob"},
        ]

        score, results = check_repository(tree)

        self.assertEqual(score, 20)
        self.assertTrue(results[0]["exists"])


class TestReport(unittest.TestCase):

    def setUp(self):
        self.metadata = {
            "full_name": "psf/requests",
            "default_branch": "main",
        }

    def test_report_generation(self):
        score, results = check_repository([
            {"path": "README.md", "type": "blob"},
        ])

        report = build_report(
            "psf/requests",
            self.metadata,
            score,
            results,
        )

        self.assertEqual(report["health_score"], 20)
        self.assertEqual(report["status"], "Poor")
        self.assertEqual(report["checks_total"], 7)
        self.assertEqual(len(report["missing"]), 6)

    def test_perfect_report(self):
        tree = [
            {"path": "README.md", "type": "blob"},
            {"path": "LICENSE", "type": "blob"},
            {"path": "CONTRIBUTING.md", "type": "blob"},
            {"path": "CODE_OF_CONDUCT.md", "type": "blob"},
            {"path": ".gitignore", "type": "blob"},
            {
                "path": ".github/ISSUE_TEMPLATE",
                "type": "tree",
            },
            {
                "path": ".github/workflows",
                "type": "tree",
            },
        ]

        score, results = check_repository(tree)

        report = build_report(
            "psf/requests",
            self.metadata,
            score,
            results,
        )

        self.assertEqual(report["health_score"], 100)
        self.assertEqual(report["status"], "Excellent")
        self.assertEqual(report["checks_passed"], 7)
        self.assertEqual(report["missing"], [])

    def test_report_is_json_serializable(self):
        score, results = check_repository([])

        report = build_report(
            "psf/requests",
            self.metadata,
            score,
            results,
        )

        encoded = json.dumps(report)
        decoded = json.loads(encoded)

        self.assertEqual(
            decoded["repository"],
            "psf/requests",
        )


class TestGitHubAPI(unittest.TestCase):

    @patch("health.urllib.request.urlopen")
    def test_successful_api_request(self, mock_urlopen):
        response = Mock()
        response.read.return_value = (
            b'{"full_name": "psf/requests"}'
        )

        mock_urlopen.return_value.__enter__.return_value = (
            response
        )

        result = github_get(
            f"{API_BASE}/repos/psf/requests",
            15,
        )

        self.assertEqual(
            result["full_name"],
            "psf/requests",
        )

    @patch("health.urllib.request.urlopen")
    def test_invalid_json_response(self, mock_urlopen):
        response = Mock()
        response.read.return_value = b"invalid json"

        mock_urlopen.return_value.__enter__.return_value = (
            response
        )

        with self.assertRaises(HealthCheckError):
            github_get(
                f"{API_BASE}/repos/psf/requests",
                15,
            )

    @patch("health.urllib.request.urlopen")
    def test_non_dictionary_response(self, mock_urlopen):
        response = Mock()
        response.read.return_value = b'["unexpected"]'

        mock_urlopen.return_value.__enter__.return_value = (
            response
        )

        with self.assertRaises(HealthCheckError):
            github_get(
                f"{API_BASE}/repos/psf/requests",
                15,
            )

    @patch("health.urllib.request.urlopen")
    def test_http_404_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "https://api.github.com/repos/owner/repo",
            404,
            "Not Found",
            {},
            None,
        )

        with self.assertRaisesRegex(
            HealthCheckError,
            "Repository not found",
        ):
            github_get(
                f"{API_BASE}/repos/owner/repo",
                15,
            )

    @patch("health.urllib.request.urlopen")
    def test_http_403_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "https://api.github.com/repos/owner/repo",
            403,
            "Forbidden",
            {},
            None,
        )

        with self.assertRaisesRegex(
            HealthCheckError,
            "rate limit",
        ):
            github_get(
                f"{API_BASE}/repos/owner/repo",
                15,
            )

    @patch("health.urllib.request.urlopen")
    def test_rate_limit_exceeded(self, mock_urlopen):
        headers = {
            "X-RateLimit-Remaining": "0"
        }

        mock_urlopen.side_effect = urllib.error.HTTPError(
            "https://api.github.com/repos/owner/repo",
            403,
            "Forbidden",
            headers,
            None,
        )

        with self.assertRaisesRegex(
            HealthCheckError,
            "rate limit exceeded",
        ):
            github_get(
                f"{API_BASE}/repos/owner/repo",
                15,
            )

    @patch("health.urllib.request.urlopen")
    def test_http_401_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "https://api.github.com/repos/owner/repo",
            401,
            "Unauthorized",
            {},
            None,
        )

        with self.assertRaisesRegex(
            HealthCheckError,
            "authentication failed",
        ):
            github_get(
                f"{API_BASE}/repos/owner/repo",
                15,
            )

    @patch("health.urllib.request.urlopen")
    def test_http_451_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "https://api.github.com/repos/owner/repo",
            451,
            "Unavailable",
            {},
            None,
        )

        with self.assertRaisesRegex(
            HealthCheckError,
            "legal reasons",
        ):
            github_get(
                f"{API_BASE}/repos/owner/repo",
                15,
            )

    @patch("health.urllib.request.urlopen")
    def test_network_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError(
            "Connection failed"
        )

        with self.assertRaisesRegex(
            HealthCheckError,
            "Network error",
        ):
            github_get(
                f"{API_BASE}/repos/owner/repo",
                15,
            )

    @patch("health.urllib.request.urlopen")
    def test_socket_timeout(self, mock_urlopen):
        mock_urlopen.side_effect = socket.timeout()

        with self.assertRaisesRegex(
            HealthCheckError,
            "timed out",
        ):
            github_get(
                f"{API_BASE}/repos/owner/repo",
                15,
            )


class TestRepositoryTree(unittest.TestCase):

    @patch("health.github_get")
    def test_successful_tree_retrieval(self, mock_get):
        mock_get.side_effect = [
            {
                "default_branch": "main",
                "full_name": "psf/requests",
            },
            {
                "truncated": False,
                "tree": [
                    {
                        "path": "README.md",
                        "type": "blob",
                    }
                ],
            },
        ]

        metadata, tree = fetch_repository_tree(
            "psf",
            "requests",
            15,
        )

        self.assertEqual(
            metadata["full_name"],
            "psf/requests",
        )
        self.assertEqual(len(tree), 1)
        self.assertEqual(mock_get.call_count, 2)

    @patch("health.github_get")
    def test_missing_default_branch(self, mock_get):
        mock_get.return_value = {}

        with self.assertRaisesRegex(
            HealthCheckError,
            "default branch",
        ):
            fetch_repository_tree(
                "psf",
                "requests",
                15,
            )

    @patch("health.github_get")
    def test_truncated_tree(self, mock_get):
        mock_get.side_effect = [
            {"default_branch": "main"},
            {
                "truncated": True,
                "tree": [],
            },
        ]

        with self.assertRaisesRegex(
            HealthCheckError,
            "truncated",
        ):
            fetch_repository_tree(
                "psf",
                "requests",
                15,
            )

    @patch("health.github_get")
    def test_invalid_tree_response(self, mock_get):
        mock_get.side_effect = [
            {"default_branch": "main"},
            {"tree": "invalid"},
        ]

        with self.assertRaisesRegex(
            HealthCheckError,
            "invalid repository tree",
        ):
            fetch_repository_tree(
                "psf",
                "requests",
                15,
            )


class TestCommandLine(unittest.TestCase):

    @patch("health.sys.argv", [
        "health.py",
        "--repo",
        "psf/requests",
        "--timeout",
        "0",
    ])
    def test_zero_timeout_is_rejected(self):
        with self.assertRaises(SystemExit) as context:
            main()

        self.assertEqual(context.exception.code, 2)


class TestTimeoutValidation(unittest.TestCase):

    @patch("health.sys.argv", [
        "health.py",
        "--repo",
        "psf/requests",
        "--timeout",
        "nan",
    ])
    def test_nan_timeout_is_rejected(self):
        with self.assertRaises(SystemExit) as context:
            main()

        self.assertEqual(context.exception.code, 2)

    @patch("health.sys.argv", [
        "health.py",
        "--repo",
        "psf/requests",
        "--timeout",
        "inf",
    ])
    def test_infinite_timeout_is_rejected(self):
        with self.assertRaises(SystemExit) as context:
            main()

        self.assertEqual(context.exception.code, 2)

    @patch("health.sys.argv", [
        "health.py",
        "--repo",
        "psf/requests",
        "--timeout",
        "-inf",
    ])
    def test_negative_infinity_timeout_is_rejected(self):
        with self.assertRaises(SystemExit) as context:
            main()

        self.assertEqual(context.exception.code, 2)


if __name__ == "__main__":
    unittest.main()