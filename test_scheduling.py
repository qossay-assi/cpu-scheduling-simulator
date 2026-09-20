import unittest
from scheduling import *


class SchedulingTests(unittest.TestCase):
    def test_priority_preemption(self):
        ps = [Process(1, 0, 4, 0, 3), Process(2, 1, 1, 0, 0)]
        self.assertEqual(
            [p for _, p in simulate(ps, "nonpreemptive", 10, False)[0]], [1, 1, 1, 1, 2]
        )
        self.assertEqual(
            [p for _, p in simulate(ps, "preemptive", 10, False)[0]], [1, 2, 1, 1, 1]
        )

    def test_round_robin(self):
        ps = [Process(1, 0, 3, 0, 1), Process(2, 0, 3, 0, 1)]
        self.assertEqual(
            [p for _, p in simulate(ps, "nonpreemptive", 10, False)[0]],
            [1, 1, 2, 2, 1, 2],
        )

    def test_io_and_metrics(self):
        chart, wait, turn = simulate([Process(1, 0, 2, 3, 0)], horizon=12)
        self.assertEqual([t for t, _ in chart], [0, 1, 5, 6, 10, 11])
        self.assertEqual((wait, turn), (0, 2))

    def test_mlfq_quanta(self):
        ps = [Process(1, 0, 30, 0, 0), Process(2, 0, 1, 0, 0)]
        chart, _, _ = simulate(ps, "mlfq", 100, False)
        self.assertEqual([pid for _, pid in chart[:9]], [1] * 8 + [2])
        self.assertEqual(len(chart), 31)

    def test_idle_horizon_and_validation(self):
        self.assertEqual(simulate([Process(1, 100, 10, 0, 0)], horizon=20), ([], 0, 0))
        self.assertEqual(len(simulate([Process(1, 0, 400, 0, 0)], horizon=300)[0]), 300)
        with self.assertRaises(ValueError):
            simulate([Process(1, 0, 0, 0, 0)])

    def test_aging_changes_order(self):
        ps = [Process(1, 0, 30, 0, 1), Process(2, 0, 1, 0, 2)]
        chart, _, _ = simulate(ps, "preemptive", 40, False)
        self.assertLess(next(t for t, p in chart if p == 2), 30)


if __name__ == "__main__":
    unittest.main()
