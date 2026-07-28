#!/usr/bin/env python3
"""Regression tests for JM105 metadata normalization."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).with_name("jm105_metadata_preflight.py")
SPEC = importlib.util.spec_from_file_location("jm105_metadata_preflight", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load {MODULE_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TestJM105MetadataPreflight(unittest.TestCase):
    def test_nmd_intact_spellings(self) -> None:
        for raw in ("WT_UPF1", "WT-UPF1", "UPF1", "UPF1+", "upf1 plus"):
            with self.subTest(raw=raw):
                self.assertEqual(MODULE.normalize_nmd(raw), "UPF1+")

    def test_nmd_deletion_spellings(self) -> None:
        for raw in (
            "upf1Δ",
            "upf1δ",
            "upf1∆",
            "upf1D",
            "upf1delta",
            "UPF1 deletion",
            "upf1 knockout",
        ):
            with self.subTest(raw=raw):
                self.assertEqual(MODULE.normalize_nmd(raw), "upf1Δ")

    def test_mud1_spellings(self) -> None:
        intact = ("WT_MUD1", "MUD1", "MUD1+")
        deletion = ("mud1Δ", "mud1δ", "mud1∆", "mud1D", "mud1delta")
        for raw in intact:
            with self.subTest(raw=raw):
                self.assertEqual(MODULE.normalize_mud1(raw), "WT")
        for raw in deletion:
            with self.subTest(raw=raw):
                self.assertEqual(MODULE.normalize_mud1(raw), "mud1Δ")

    def test_age_spellings(self) -> None:
        self.assertEqual(MODULE.normalize_age("Young"), "young")
        self.assertEqual(MODULE.normalize_age("Old"), "old")

    def test_glucose_spellings(self) -> None:
        for raw in ("2pct", "2%", "2.0"):
            with self.subTest(raw=raw):
                self.assertEqual(MODULE.normalize_glucose(raw), "2%")
        for raw in ("0.1%", "0.1", "0p1", "CR"):
            with self.subTest(raw=raw):
                self.assertEqual(MODULE.normalize_glucose(raw), "0.1%")

    def test_unknown_label_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            MODULE.normalize_nmd("mystery")
        with self.assertRaises(ValueError):
            MODULE.normalize_mud1("mystery")
        with self.assertRaises(ValueError):
            MODULE.normalize_age("mystery")
        with self.assertRaises(ValueError):
            MODULE.normalize_glucose("mystery")

    def test_sample_id_is_not_an_input(self) -> None:
        self.assertEqual(MODULE.normalize_nmd("upf1Δ"), "upf1Δ")
        self.assertEqual(MODULE.normalize_nmd("UPF1"), "UPF1+")


if __name__ == "__main__":
    unittest.main(verbosity=2)
