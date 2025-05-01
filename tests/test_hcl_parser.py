#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the HCL parser implementation in UnitAPI DSL.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.unitapi.dsl.parsers.hcl_parser import HCLParser
from src.unitapi.dsl.base import Extension, Device, Pipeline, PipelineStep


class TestHCLParser(unittest.TestCase):
    """Test cases for the HCL parser"""

    def setUp(self):
        """Set up test fixtures"""
        self.parser = HCLParser()
        self.examples_dir = Path(__file__).parent.parent / "examples" / "dsl"
        self.microphone_config_path = self.examples_dir / "microphone_config.hcl"

        # Sample HCL content for testing
        self.sample_hcl = """
        version = "1.0"

        extension "test_extension" {
          version = ">=1.0.0"
          config {
            key1 = "value1"
            key2 = 123
          }
        }

        device "test_device" {
          type = "test_type"
          capabilities = ["cap1", "cap2"]
          metadata = {
            location = "test_location"
            model = "test_model"
          }
        }

        pipeline "test_pipeline" {
          source = "test_device"
          
          step "test_step" {
            param1 = "value1"
            param2 = 123
            param3 = ["item1", "item2"]
          }
        }
        """

    def test_parse_sample(self):
        """Test parsing a sample HCL string"""
        config = self.parser.parse(self.sample_hcl)

        # Check basic structure
        self.assertEqual(config["version"], "1.0")
        self.assertEqual(len(config["extensions"]), 1)
        self.assertEqual(len(config["devices"]), 1)
        self.assertEqual(len(config["pipelines"]), 1)

        # Check extension
        extension = config["extensions"][0]
        self.assertIsInstance(extension, Extension)
        self.assertEqual(extension.name, "test_extension")
        self.assertEqual(extension.version, ">=1.0.0")
        self.assertEqual(extension.config["key1"], "value1")
        self.assertEqual(extension.config["key2"], 123)

        # Check device
        device = config["devices"][0]
        self.assertIsInstance(device, Device)
        self.assertEqual(device.id, "test_device")
        self.assertEqual(device.device_type, "test_type")
        self.assertEqual(device.capabilities, ["cap1", "cap2"])
        self.assertEqual(device.metadata["location"], "test_location")
        self.assertEqual(device.metadata["model"], "test_model")

        # Check pipeline
        pipeline = config["pipelines"][0]
        self.assertIsInstance(pipeline, Pipeline)
        self.assertEqual(pipeline.name, "test_pipeline")
        self.assertEqual(pipeline.source, "test_device")
        self.assertEqual(len(pipeline.steps), 1)

        # Check step
        step = pipeline.steps[0]
        self.assertIsInstance(step, PipelineStep)
        self.assertEqual(step.action, "test_step")
        self.assertEqual(step.params["param1"], "value1")
        self.assertEqual(step.params["param2"], 123)
        self.assertEqual(step.params["param3"], ["item1", "item2"])

    def test_parse_microphone_config(self):
        """Test parsing the microphone_config.hcl example file"""
        if not self.microphone_config_path.exists():
            self.skipTest(f"Example file not found: {self.microphone_config_path}")

        with open(self.microphone_config_path, "r") as f:
            content = f.read()

        config = self.parser.parse(content)

        # Check basic structure
        self.assertEqual(config["version"], "1.0")
        self.assertEqual(len(config["extensions"]), 2)
        self.assertEqual(len(config["devices"]), 2)
        self.assertEqual(len(config["pipelines"]), 2)

        # Check extensions
        extensions = {ext.name: ext for ext in config["extensions"]}
        self.assertIn("microphone", extensions)
        self.assertIn("audio_processing", extensions)

        mic_ext = extensions["microphone"]
        self.assertEqual(mic_ext.config["sample_rate"], 44100)
        self.assertEqual(mic_ext.config["channels"], 2)
        self.assertEqual(mic_ext.config["format"], "wav")

        # Check devices
        devices = {dev.id: dev for dev in config["devices"]}
        self.assertIn("desktop-mic", devices)
        self.assertIn("rpi-mic", devices)

        desktop_mic = devices["desktop-mic"]
        self.assertEqual(desktop_mic.device_type, "microphone")
        self.assertEqual(desktop_mic.capabilities, ["recording", "streaming"])
        self.assertEqual(desktop_mic.metadata["location"], "office")

        # Check pipelines
        pipelines = {p.name: p for p in config["pipelines"]}
        self.assertIn("voice-recorder", pipelines)
        self.assertIn("voice-assistant", pipelines)

        recorder = pipelines["voice-recorder"]
        self.assertEqual(recorder.source, "desktop-mic")
        self.assertEqual(len(recorder.steps), 3)

        # Check steps
        steps = {s.action: s for s in recorder.steps}
        self.assertIn("record", steps)
        self.assertIn("process", steps)
        self.assertIn("save", steps)

        record_step = steps["record"]
        self.assertEqual(record_step.params["duration"], 60)
        self.assertEqual(record_step.params["sample_rate"], 44100)

    def test_validate(self):
        """Test the validate method"""
        # Valid config
        valid_config = {
            "version": "1.0",
            "extensions": [],
            "devices": [],
            "pipelines": [],
        }
        self.assertTrue(self.parser.validate(valid_config))

        # Invalid configs
        invalid_configs = [
            None,  # Not a dict
            {},  # Missing version
        ]

        for config in invalid_configs:
            self.assertFalse(self.parser.validate(config))

    def test_to_string(self):
        """Test converting a config back to HCL string"""
        # Parse the sample, then convert back to string
        config = self.parser.parse(self.sample_hcl)
        hcl_string = self.parser.to_string(config)

        # Check that the string contains expected elements
        self.assertIn('version = "1.0"', hcl_string)
        self.assertIn('extension "test_extension"', hcl_string)
        self.assertIn('device "test_device"', hcl_string)
        self.assertIn('pipeline "test_pipeline"', hcl_string)
        self.assertIn('step "test_step"', hcl_string)

        # Parse the generated string to ensure it's valid
        config2 = self.parser.parse(hcl_string)
        self.assertEqual(config2["version"], config["version"])
        self.assertEqual(len(config2["extensions"]), len(config["extensions"]))
        self.assertEqual(len(config2["devices"]), len(config["devices"]))
        self.assertEqual(len(config2["pipelines"]), len(config["pipelines"]))


if __name__ == "__main__":
    unittest.main()
