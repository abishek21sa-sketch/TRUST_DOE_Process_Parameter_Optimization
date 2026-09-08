import unittest

from trustdoe.signature_algorithm import ablation, select_recipe, sensitivity


class SignatureAlgorithmTests(unittest.TestCase):
    def setUp(self):
        self.candidates = [
            {"recipe": [0.0, 0.0], "objective": 1.0, "information": 0.1, "safety": 0.9},
            {"recipe": [0.1, 0.0], "objective": 0.6, "information": 0.4, "safety": 0.8},
        ]

    def test_safe_recipe_is_selected(self):
        self.assertEqual(select_recipe(self.candidates, [0.0, 0.0], 0.15, 0.85)["recipe"], [0.0, 0.0])

    def test_negative_radius_raises(self):
        with self.assertRaises(ValueError):
            select_recipe(self.candidates, [0.0, 0.0], -1, 0.0)

    def test_trust_ablation_is_executable(self):
        self.assertEqual(ablation(self.candidates, [0.0, 0.0], 0.01, 0.75)["recipe"], [0.1, 0.0])

    def test_safety_sensitivity_can_hold(self):
        self.assertIsNone(sensitivity(self.candidates, [0.0, 0.0], 0.15, 0.85, 0.1))


if __name__ == "__main__":
    unittest.main()
