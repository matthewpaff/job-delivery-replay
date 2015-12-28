from pathlib import Path
import unittest

from jobs_lab.core import replay_jobs
from jobs_lab.fixture_check import check


class JobTests(unittest.TestCase):
    def test_duplicate_deliveries_do_not_add_attempts(self):
        result = replay_jobs({"events": [{"event": "enqueue", "job_id": "a"}, {"event": "deliver", "job_id": "a"}, {"event": "deliver", "job_id": "a"}]})
        self.assertEqual(result["jobs"], [{"job_id": "a", "status": "done", "attempts": 1}])
        self.assertEqual(result["results"][-1]["outcome"], "duplicate")

    def test_dead_letter_state_and_isolated_jobs(self):
        result = replay_jobs({"max_attempts": 1, "events": [{"event": "enqueue", "job_id": "b"}, {"event": "enqueue", "job_id": "a"}, {"event": "fail", "job_id": "a"}, {"event": "deliver", "job_id": "a"}]})
        self.assertEqual(result["jobs"], [{"job_id": "a", "status": "dead", "attempts": 1}, {"job_id": "b", "status": "pending", "attempts": 0}])

    def test_unknown_jobs_and_completed_failures_are_rejected(self):
        for events in ([{"event": "deliver", "job_id": "a"}], [{"event": "enqueue", "job_id": "a"}, {"event": "deliver", "job_id": "a"}, {"event": "fail", "job_id": "a"}]):
            with self.assertRaises(ValueError):
                replay_jobs({"events": events})

    def test_complete_fixture_corpus(self):
        self.assertGreaterEqual(check(Path(__file__).resolve().parents[1] / "fixtures/cases.jsonl", replay_jobs), 350)


if __name__ == "__main__":
    unittest.main()
