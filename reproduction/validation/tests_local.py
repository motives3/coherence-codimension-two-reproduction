"""Synthetic independent-arithmetic checks; never read historical records."""
import random
import unittest
from fractions import Fraction as F
from local_arithmetic import Bound, UNIT, sqrt_down, sqrt_up, finite_normal, stress_gap


class Context:
    def require(self, condition, label):
        if not condition:
            raise ValueError(label)


class RationalArithmeticTests(unittest.TestCase):
    def test_all_corner_products_are_enclosed(self):
        rng = random.Random(182)
        for _ in range(250):
            a, b, c, d = [F(rng.randint(-30, 30), rng.randint(1, 31))
                          for _ in range(4)]
            x, y = Bound(min(a, b), max(a, b)), Bound(min(c, d), max(c, d))
            z = x*y
            for u in (x.low, x.high):
                for v in (y.low, y.high):
                    self.assertLessEqual(z.low, u*v)
                    self.assertGreaterEqual(z.high, u*v)

    def test_division_signs_and_zero_guard(self):
        for denominator in (Bound(2, 3), Bound(-3, -2)):
            numerator = Bound(F(-1, 7), F(11, 13))
            quotient = numerator/denominator
            for a in (numerator.low, numerator.high):
                for b in (denominator.low, denominator.high):
                    self.assertLessEqual(quotient.low, a/b)
                    self.assertGreaterEqual(quotient.high, a/b)
        with self.assertRaises(ValueError):
            Bound(1)/Bound(-1, 1)

    def test_directed_square_roots_are_integer_witnesses(self):
        for value in (F(0), F(1), F(3), F(17, 31), F(1, UNIT**2), F(7, UNIT**2)):
            lo, hi = sqrt_down(value), sqrt_up(value)
            self.assertLessEqual(lo*lo, value)
            self.assertGreaterEqual(hi*hi, value)
            self.assertLessEqual(hi-lo, F(1, UNIT))
        with self.assertRaises(ValueError):
            sqrt_down(F(-1, 100))

    def test_normal_interior_exact_value(self):
        result = finite_normal(Context(), F(2), F(1), F(1), F(1, 2), F(1, 10))
        self.assertEqual(result["branch"], "interior")
        self.assertEqual(result["gap"], F(3, 4))

    def test_normal_boundary_and_zero_radius(self):
        result = finite_normal(Context(), F(1), F(2), F(1), F(1, 2), F(0))
        self.assertEqual(result["branch"], "boundary")
        self.assertEqual(result["gap"], F(1))
        # A smaller mean gap must not be replaced by the residual gap.
        self.assertLess(result["gap"], F(2))

    def test_normal_invalid_radius_is_rejected(self):
        with self.assertRaises(ValueError):
            finite_normal(Context(), F(1), F(1), F(1), F(1), F(3, 4))

    def test_stress_change_keeps_phase_defect_and_physical_metric(self):
        value = stress_gap(Context(), F(1), 1000, F(1), F(1, 1000),
                           F(1, 2000), F(1, 2), F(1, 1000), F(1, 10**6))
        self.assertGreater(value["phase_defect"], 0)
        self.assertGreater(value["phase_reference"], value["eta_v"])
        self.assertEqual(value["metric_lower"], value["mass"]*F(999, 1000))
        self.assertEqual(value["cm"], value["metric_lower"]*value["gm"]/2)

    def test_stress_reference_floor_domain_is_explicit(self):
        with self.assertRaises(ValueError):
            stress_gap(Context(), F(1), 1000, F(1), F(1, 1000),
                       F(1, 2000), F(0), F(1, 1000), F(1, 10**6))


if __name__ == "__main__":
    unittest.main()
