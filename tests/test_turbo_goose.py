```python
import unittest

from turbo_goose import (
    TurboGoose,
    CrazyVehicleError,
    TurboGooseError,
    GooseNoEnergy,
    GooseCannotTravelThere,
)


class TestTurboGooseConstructor(unittest.TestCase):
    def test_create_with_valid_parameters(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 80)

        self.assertEqual(goose.name, "Готурбо")
        self.assertEqual(goose.mass_kg, 12)
        self.assertEqual(goose.wing_span_m, 1.8)
        self.assertEqual(goose.max_speed_kmh, 60)
        self.assertEqual(goose.energy, 80)
        self.assertEqual(goose.position_km, 0.0)
        self.assertFalse(goose.is_flying)

    def test_default_energy_is_100(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60)
        self.assertEqual(goose.energy, 100.0)

    def test_empty_name_is_invalid(self):
        with self.assertRaises(ValueError):
            TurboGoose("", 12, 1.8, 60)

    def test_name_with_only_spaces_is_invalid(self):
        with self.assertRaises(ValueError):
            TurboGoose("   ", 12, 1.8, 60)

    def test_non_positive_mass_is_invalid(self):
        with self.assertRaises(ValueError):
            TurboGoose("Готурбо", 0, 1.8, 60)

    def test_negative_mass_is_invalid(self):
        with self.assertRaises(ValueError):
            TurboGoose("Готурбо", -1, 1.8, 60)

    def test_non_positive_wing_span_is_invalid(self):
        with self.assertRaises(ValueError):
            TurboGoose("Готурбо", 12, 0, 60)

    def test_negative_wing_span_is_invalid(self):
        with self.assertRaises(ValueError):
            TurboGoose("Готурбо", 12, -1, 60)

    def test_non_positive_speed_is_invalid(self):
        with self.assertRaises(ValueError):
            TurboGoose("Готурбо", 12, 1.8, 0)

    def test_negative_speed_is_invalid(self):
        with self.assertRaises(ValueError):
            TurboGoose("Готурбо", 12, 1.8, -1)

    def test_energy_boundaries_are_valid(self):
        goose_empty = TurboGoose("Гусь-1", 12, 1.8, 60, 0)
        goose_full = TurboGoose("Гусь-2", 12, 1.8, 60, 100)

        self.assertEqual(goose_empty.energy, 0)
        self.assertEqual(goose_full.energy, 100)

    def test_energy_outside_range_is_invalid(self):
        with self.assertRaises(ValueError):
            TurboGoose("Готурбо", 12, 1.8, 60, -0.1)

        with self.assertRaises(ValueError):
            TurboGoose("Готурбо", 12, 1.8, 60, 100.1)


class TestTurboGooseMovement(unittest.TestCase):
    def setUp(self):
        self.goose = TurboGoose("Готурбо", 12, 1.8, 60, 100)

    def test_successful_flight(self):
        time = self.goose.move(30, "air")

        self.assertAlmostEqual(time, 0.5)
        self.assertEqual(self.goose.position_km, 30)
        self.assertEqual(self.goose.energy, 40)
        self.assertTrue(self.goose.is_flying)

    def test_zero_distance_is_invalid(self):
        with self.assertRaises(ValueError):
            self.goose.move(0, "air")

        self.assertEqual(self.goose.position_km, 0.0)
        self.assertEqual(self.goose.energy, 100)
        self.assertFalse(self.goose.is_flying)

    def test_negative_distance_is_invalid(self):
        with self.assertRaises(ValueError):
            self.goose.move(-1, "air")

        self.assertEqual(self.goose.position_km, 0.0)
        self.assertEqual(self.goose.energy, 100)
        self.assertFalse(self.goose.is_flying)

    def test_ground_movement_is_not_supported(self):
        with self.assertRaises(GooseCannotTravelThere):
            self.goose.move(1, "ground")

        self.assertEqual(self.goose.position_km, 0.0)
        self.assertEqual(self.goose.energy, 100)
        self.assertFalse(self.goose.is_flying)

    def test_insufficient_energy_does_not_change_state(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 10)

        with self.assertRaises(GooseNoEnergy):
            goose.move(10, "air")

        self.assertEqual(goose.position_km, 0.0)
        self.assertEqual(goose.energy, 10)
        self.assertFalse(goose.is_flying)

    def test_flight_can_use_all_remaining_energy(self):
        self.goose.move(50, "air")

        self.assertEqual(self.goose.position_km, 50)
        self.assertEqual(self.goose.energy, 0)
        self.assertTrue(self.goose.is_flying)

    def test_energy_slightly_below_required_amount_is_insufficient(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 1.9)

        with self.assertRaises(GooseNoEnergy):
            goose.move(1, "air")

        self.assertEqual(goose.position_km, 0.0)
        self.assertEqual(goose.energy, 1.9)
        self.assertFalse(goose.is_flying)

    def test_no_energy_exception_message(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 0)

        with self.assertRaises(GooseNoEnergy) as context:
            goose.move(1, "air")

        self.assertEqual(
            str(context.exception),
            "Готурбо вымотался: сначала покорми гуся!",
        )

    def test_unsupported_medium_exception_message(self):
        with self.assertRaises(GooseCannotTravelThere) as context:
            self.goose.move(1, "ground")

        self.assertEqual(
            str(context.exception),
            "Готурбо умеет летать, а не ползать.",
        )


class TestTurboGooseObstacles(unittest.TestCase):
    def test_building_requires_flight_and_energy(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 20)
        goose.move(5, "air")

        self.assertTrue(goose.can_overcome("building"))

    def test_grounded_goose_cannot_overcome_building(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 100)

        self.assertFalse(goose.can_overcome("building"))

    def test_building_fails_when_energy_below_10(self): 
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 9) 
        goose.move(1, "air") 
        
        self.assertEqual(goose.energy, 7) 
        self.assertFalse(goose.can_overcome("building"))

    def test_storm_requires_wide_enough_wings(self):
        goose = TurboGoose("Готурбо", 12, 1.5, 60, 100)

        self.assertFalse(goose.can_overcome("storm"))

    def test_storm_boundary_at_25_energy(self):
        goose = TurboGoose("Готурбо", 12, 1.6, 60, 25)

        self.assertTrue(goose.can_overcome("storm"))

    def test_storm_fails_below_25_energy(self):
        goose = TurboGoose("Готурбо", 12, 1.6, 60, 24.9)

        self.assertFalse(goose.can_overcome("storm"))

    def test_power_line_cannot_be_overcome(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 100)
        goose.move(1, "air")

        self.assertFalse(goose.can_overcome("power_line"))

    def test_unknown_obstacle_is_invalid(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 100)

        with self.assertRaises(ValueError):
            goose.can_overcome("unknown_obstacle")


class TestTurboGooseEnergy(unittest.TestCase):
    def test_calculate_energy_does_not_change_state(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 80)

        result = goose.calculate_energy(12, "air")

        self.assertEqual(result, 24)
        self.assertEqual(goose.energy, 80)
        self.assertEqual(goose.position_km, 0.0)
        self.assertFalse(goose.is_flying)

    def test_calculate_energy_rejects_unsupported_medium(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 80)

        with self.assertRaises(GooseCannotTravelThere):
            goose.calculate_energy(1, "water")

        self.assertEqual(goose.energy, 80)
        self.assertEqual(goose.position_km, 0.0)
        self.assertFalse(goose.is_flying)

    def test_calculate_energy_rejects_zero_distance(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 80)

        with self.assertRaises(ValueError):
            goose.calculate_energy(0, "air")

        self.assertEqual(goose.energy, 80)
        self.assertEqual(goose.position_km, 0.0)
        self.assertFalse(goose.is_flying)

    def test_calculate_energy_rejects_negative_distance(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 80)

        with self.assertRaises(ValueError):
            goose.calculate_energy(-1, "air")

        self.assertEqual(goose.energy, 80)
        self.assertEqual(goose.position_km, 0.0)
        self.assertFalse(goose.is_flying)

    def test_refuel_caps_energy_at_100(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 90)
        goose.refuel(25)

        self.assertEqual(goose.energy, 100)

    def test_refuel_rejects_zero_amount(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 50)

        with self.assertRaises(ValueError):
            goose.refuel(0)

        self.assertEqual(goose.energy, 50)

    def test_refuel_rejects_negative_amount(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 50)

        with self.assertRaises(ValueError):
            goose.refuel(-1)

        self.assertEqual(goose.energy, 50)

    def test_refuel_with_large_amount_caps_at_100(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 50)
        goose.refuel(1000)

        self.assertEqual(goose.energy, 100)


class TestTurboGooseLandingAndStatus(unittest.TestCase):
    def test_land_stops_flight_without_changing_other_state(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 100)
        goose.move(10, "air")

        energy_before = goose.energy
        position_before = goose.position_km

        goose.land()

        self.assertFalse(goose.is_flying)
        self.assertEqual(goose.energy, energy_before)
        self.assertEqual(goose.position_km, position_before)

    def test_land_while_already_grounded(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 100)
        goose.land()

        self.assertFalse(goose.is_flying)
        self.assertEqual(goose.energy, 100)
        self.assertEqual(goose.position_km, 0.0)

    def test_get_status_returns_expected_fields(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 80)

        status = goose.get_status()

        self.assertEqual(
            set(status.keys()),
            {"name", "energy", "position_km", "is_flying", "wing_span_m"},
        )
        self.assertEqual(status["name"], "Готурбо")
        self.assertEqual(status["energy"], 80)
        self.assertEqual(status["position_km"], 0.0)
        self.assertFalse(status["is_flying"])
        self.assertEqual(status["wing_span_m"], 1.8)

    def test_changing_status_dict_does_not_change_object(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60, 80)

        status = goose.get_status()
        status["energy"] = 0
        status["name"] = "Другой гусь"

        self.assertEqual(goose.energy, 80)
        self.assertEqual(goose.name, "Готурбо")


class TestTurboGoosePublicAttributes(unittest.TestCase):
    def test_public_attributes_are_read_only(self):
        goose = TurboGoose("Готурбо", 12, 1.8, 60)
        attributes = {
            "name": "Другой гусь",
            "mass_kg": 20,
            "wing_span_m": 2.0,
            "max_speed_kmh": 80,
            "energy": 50,
            "position_km": 10,
            "is_flying": True,
        }

        for attribute, value in attributes.items():
            with self.subTest(attribute=attribute):
                with self.assertRaises(AttributeError):
                    setattr(goose, attribute, value)


class TestTurboGooseExceptionHierarchy(unittest.TestCase):
    def test_exception_inheritance(self):
        self.assertTrue(issubclass(TurboGooseError, CrazyVehicleError))
        self.assertTrue(issubclass(GooseNoEnergy, TurboGooseError))
        self.assertTrue(issubclass(GooseCannotTravelThere, TurboGooseError))


if __name__ == "__main__":
    unittest.main()
```
