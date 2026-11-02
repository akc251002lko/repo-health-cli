
import unittest

from health import (
    HealthCheckError,
    validate_repo,
    check_repository,
    build_report,
)


class TestRepositoryValidation(unittest.TestCase):

    def test_valid_repository(self):
        self.assertEqual(
            validate_repo("psf/requests"),
            ("psf", "requests"),
        )

    def test_invalid_repository(self):
        with self.assertRaises(HealthCheckError):
            validate_repo("invalid-repository")

    def test_empty_repository(self):
        with self.assertRaises(HealthCheckError):
            validate_repo("owner/")

    def test_multiple_slashes(self):
        with self.assertRaises(HealthCheckError):
            validate_repo("owner/repo/extra")


class TestHealthScoring(unittest.TestCase):

    def test_all_requirements_present(self):
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

        issue_check = results[5]

        self.assertTrue(issue_check["exists"])
        self.assertEqual(score, 10)


class TestReport(unittest.TestCase):

    def test_report_generation(self):
        metadata = {
            "full_name": "psf/requests",
            "default_branch": "main",
        }

        score, results = check_repository([
            {"path": "README.md", "type": "blob"},
        ])

        report = build_report(
            "psf/requests",
            metadata,
            score,
            results,
        )

        self.assertEqual(report["health_score"], 20)
        self.assertEqual(report["status"], "Poor")
        self.assertEqual(report["checks_total"], 7)
        self.assertEqual(len(report["missing"]), 6)


if __name__ == "__main__":
    unittest.main()
