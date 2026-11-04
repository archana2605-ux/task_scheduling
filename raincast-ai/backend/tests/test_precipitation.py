"""
Unit tests for precipitation accumulation-to-incremental conversion.

These tests verify the core meteorological calculation:
  Incremental rainfall = Accumulated[step N] - Accumulated[step N-1]

ECMWF total precipitation is cumulative from forecast init time.
We must never sum cumulative values directly — only differences.
"""

import pytest
import numpy as np
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.precipitation import (
    accumulated_to_incremental,
    accumulated_grid_to_incremental,
    compute_period_accumulation,
    metres_to_mm,
    classify_rainfall_intensity,
    classify_grid,
)


class TestMetresToMM:
    def test_basic_conversion(self):
        assert metres_to_mm(0.001) == pytest.approx(1.0)
        assert metres_to_mm(0.025) == pytest.approx(25.0)
        assert metres_to_mm(0.0) == 0.0

    def test_array_conversion(self):
        arr = np.array([0.001, 0.010, 0.100])
        result = metres_to_mm(arr)
        np.testing.assert_allclose(result, [1.0, 10.0, 100.0])

    def test_zero_stays_zero(self):
        assert metres_to_mm(0.0) == 0.0


class TestAccumulatedToIncremental:
    def test_simple_accumulation(self):
        """Standard case: each step increments equally."""
        steps = [0, 3, 6, 9]
        accumulated = [0.0, 3.0, 6.0, 9.0]  # 3mm per step
        result = accumulated_to_incremental(steps, accumulated)

        assert len(result) == 4
        assert result[0]["accumulated_mm"] == 0.0
        assert result[0]["incremental_mm"] == 0.0

        # Steps 1-3: each should be 3mm
        for r in result[1:]:
            assert r["incremental_mm"] == pytest.approx(3.0)
            assert r["accumulation_period_h"] == 3

    def test_step_zero_is_zero(self):
        """Step 0 should always have ~0 incremental rainfall."""
        steps = [0, 6, 12]
        accumulated = [0.0, 10.0, 25.0]
        result = accumulated_to_incremental(steps, accumulated)

        assert result[0]["step_hours"] == 0
        assert result[0]["incremental_mm"] == pytest.approx(0.0)

    def test_first_nonzero_step(self):
        """When forecast starts at step > 0, treat as incremental from 0."""
        steps = [6, 12, 24]
        accumulated = [5.0, 12.0, 20.0]
        result = accumulated_to_incremental(steps, accumulated)

        # Step 6: increment = 5.0 (from 0)
        assert result[0]["incremental_mm"] == pytest.approx(5.0)
        assert result[0]["accumulation_period_h"] == 6

        # Step 12: 12 - 5 = 7
        assert result[1]["incremental_mm"] == pytest.approx(7.0)

        # Step 24: 20 - 12 = 8
        assert result[2]["incremental_mm"] == pytest.approx(8.0)

    def test_negative_small_clamped(self):
        """Very small negatives from float rounding are clamped to 0."""
        steps = [0, 3, 6]
        accumulated = [0.0, 5.0, 4.9999]  # floating-point noise
        result = accumulated_to_incremental(steps, accumulated)
        # The difference 4.9999 - 5.0 = -0.0001 should be clamped to 0
        assert result[2]["incremental_mm"] == pytest.approx(0.0)

    def test_large_negative_flagged(self):
        """Large negative differences are clamped but warned."""
        steps = [0, 3, 6]
        accumulated = [0.0, 20.0, 10.0]  # -10mm diff — real anomaly
        result = accumulated_to_incremental(steps, accumulated)
        # Should be clamped to 0 with a warning
        assert result[2]["incremental_mm"] == pytest.approx(0.0)
        assert result[2]["warning"] is not None
        assert "Negative" in result[2]["warning"]

    def test_unsorted_steps_sorted_correctly(self):
        """Input steps out of order should be sorted before processing."""
        steps = [6, 0, 3]
        accumulated = [6.0, 0.0, 3.0]  # paired: step=6→6mm, step=0→0, step=3→3
        result = accumulated_to_incremental(steps, accumulated)

        # Should be sorted: 0, 3, 6
        assert result[0]["step_hours"] == 0
        assert result[1]["step_hours"] == 3
        assert result[2]["step_hours"] == 6
        assert result[1]["incremental_mm"] == pytest.approx(3.0)
        assert result[2]["incremental_mm"] == pytest.approx(3.0)

    def test_empty_input(self):
        """Empty inputs return empty list without error."""
        result = accumulated_to_incremental([], [])
        assert result == []

    def test_single_step(self):
        """A single step returns one entry."""
        result = accumulated_to_incremental([6], [10.0])
        assert len(result) == 1
        assert result[0]["incremental_mm"] == pytest.approx(10.0)

    def test_mismatched_lengths_raises(self):
        """Mismatched input lengths raise ValueError."""
        with pytest.raises(ValueError, match="same length"):
            accumulated_to_incremental([0, 3], [0.0])

    def test_accumulation_periods(self):
        """Accumulation period hours correctly computed."""
        steps = [0, 6, 12, 24]
        accumulated = [0.0, 6.0, 10.0, 18.0]
        result = accumulated_to_incremental(steps, accumulated)

        assert result[1]["accumulation_period_h"] == 6   # 6-0
        assert result[2]["accumulation_period_h"] == 6   # 12-6
        assert result[3]["accumulation_period_h"] == 12  # 24-12


class TestPeriodAccumulation:
    def test_24h_accumulation(self):
        """Test 24-hour rainfall summation."""
        steps = [0, 6, 12, 18, 24, 30, 48]
        accumulated = [0.0, 2.0, 5.0, 8.0, 12.0, 14.0, 20.0]
        incremental = accumulated_to_incremental(steps, accumulated)

        total_24h = compute_period_accumulation(incremental, 24)
        assert total_24h == pytest.approx(12.0)  # sum of steps within 0-24h

    def test_48h_accumulation(self):
        """Test 48-hour rainfall summation."""
        steps = list(range(0, 49, 6))
        accumulated = [float(s) for s in steps]  # 1mm/hour constant rate
        incremental = accumulated_to_incremental(steps, accumulated)

        total_48h = compute_period_accumulation(incremental, 48)
        assert total_48h == pytest.approx(48.0)


class TestGridAccumulation:
    def test_grid_incremental(self):
        """Test 2D grid accumulation-to-incremental conversion."""
        step0 = np.array([[0.0, 0.0], [0.0, 0.0]])
        step6 = np.array([[3.0, 6.0], [1.0, 2.0]])
        step12 = np.array([[5.0, 9.0], [3.0, 4.0]])

        step_data = {0: step0, 6: step6, 12: step12}
        result = accumulated_grid_to_incremental(step_data)

        # Step 6: diff = step6 - step0
        np.testing.assert_allclose(result[6], [[3.0, 6.0], [1.0, 2.0]])
        # Step 12: diff = step12 - step6
        np.testing.assert_allclose(result[12], [[2.0, 3.0], [2.0, 2.0]])

    def test_negative_grid_values_become_nan(self):
        """Large negative grid differences become NaN (bad data)."""
        step0 = np.array([[10.0, 5.0]])
        step6 = np.array([[3.0, 7.0]])   # first cell has -7 decrease
        step_data = {0: step0, 6: step6}
        result = accumulated_grid_to_incremental(step_data)
        # -7.0 < -0.01 → NaN
        assert np.isnan(result[6][0, 0])
        # 7.0 - 5.0 = 2.0 → valid
        assert result[6][0, 1] == pytest.approx(2.0)


class TestRainfallClassification:
    def test_no_rain(self):
        assert classify_rainfall_intensity(0.0) == "No rainfall"
        assert classify_rainfall_intensity(-1.0) == "No rainfall"

    def test_very_light(self):
        assert classify_rainfall_intensity(0.5) == "Very light"
        assert classify_rainfall_intensity(2.4) == "Very light"

    def test_light(self):
        assert classify_rainfall_intensity(2.5) == "Light"
        assert classify_rainfall_intensity(14.9) == "Light"

    def test_moderate(self):
        assert classify_rainfall_intensity(15.0) == "Moderate"
        assert classify_rainfall_intensity(64.4) == "Moderate"

    def test_heavy(self):
        assert classify_rainfall_intensity(64.5) == "Heavy"
        assert classify_rainfall_intensity(115.4) == "Heavy"

    def test_very_heavy(self):
        assert classify_rainfall_intensity(115.5) == "Very heavy"
        assert classify_rainfall_intensity(204.4) == "Very heavy"

    def test_extremely_heavy(self):
        assert classify_rainfall_intensity(204.5) == "Extremely heavy"
        assert classify_rainfall_intensity(500.0) == "Extremely heavy"

    def test_grid_classification(self):
        arr = np.array([[0.0, 1.0, 10.0], [30.0, 100.0, 300.0]])
        result = classify_grid(arr)
        assert result[0, 0] == 0   # no rain
        assert result[0, 1] == 1   # very light
        assert result[0, 2] == 2   # light
        assert result[1, 0] == 3   # moderate
        assert result[1, 1] == 4   # heavy (100 >= 64.5 but < 115.5 → category 4)
        assert result[1, 2] == 6   # extremely heavy


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
