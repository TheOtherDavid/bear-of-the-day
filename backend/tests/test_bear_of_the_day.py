import json
import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import mock_open, patch

from botocore.handlers import validate_ascii_metadata

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

import bear_of_the_day as generator


class BearPromptTests(unittest.TestCase):
    def test_seasonal_scene_preserves_text_in_prompt_and_metadata(self):
        self.check_prompt(
            month=7,
            rolls=(0.24, 0.49),
            scene="Joining a village Sch\u00fctzenfest",
            general_spirit="Playful",
            seasonal_spirit="Patriotic",
            expected_subject="Brown Bears",
        )

    def test_general_scene_still_gets_a_distinct_monthly_spirit(self):
        self.check_prompt(
            month=10,
            rolls=(0.25, 0.5),
            scene="Catching salmon",
            general_spirit="Harvest",
            seasonal_spirit="Spooky",
            expected_subject="Brown Bear",
        )

    def check_prompt(self, *, month, rolls, scene, general_spirit, seasonal_spirit, expected_subject):
        choices = iter(["Brown Bear", scene, general_spirit, seasonal_spirit])

        def choose(pool):
            selection = next(choices)
            self.assertIn(selection, pool)
            if selection == seasonal_spirit:
                self.assertNotIn(general_spirit.casefold(), {word.casefold() for word in pool})
            return selection

        now = datetime(2026, month, 1, 13, tzinfo=timezone.utc)
        environment = {
            "DEBUG_MODE": "True",
            "AWS_BUCKET_NAME": "bear-of-the-day",
            "AWS_DEFAULT_REGION": "us-east-2",
        }
        with (
            patch.dict(os.environ, environment, clear=True),
            patch.object(generator.config, "verify_environment"),
            patch.object(generator.boto3, "client") as boto_client,
            patch.object(generator.datetime, "datetime") as clock,
            patch.object(generator.random, "random", side_effect=rolls),
            patch.object(generator.random, "choice", side_effect=choose),
            patch.object(generator.dalle, "get_gpt_base64_image", return_value="aW1hZ2U=") as generate,
            patch.object(generator.manifest, "append_entry") as append_entry,
        ):
            clock.now.return_value = now
            generator.lambda_handler({}, None)

        prompt = f"{expected_subject} {scene}, {general_spirit}, {seasonal_spirit}"
        generate.assert_called_once_with("gpt-image-2", prompt)
        clock.now.assert_any_call(timezone.utc)
        put_object = boto_client.return_value.put_object
        put_object.assert_called_once()
        params = put_object.call_args.kwargs
        validate_ascii_metadata(params)
        self.assertEqual(params["Body"], b"image")
        self.assertEqual(generator.s3.decode_image_metadata(params["Metadata"]), {
            "prompt": prompt,
            "subject": expected_subject,
            "scene": scene,
            "spirits": f"{general_spirit}, {seasonal_spirit}",
            "model": "gpt-image-2",
        })
        append_entry.assert_called_once()
        bucket, entry = append_entry.call_args.args
        self.assertEqual(bucket, "bear-of-the-day")
        self.assertEqual(entry["prompt"], prompt)
        self.assertEqual(entry["scene"], scene)
        self.assertEqual(entry["spirits"], [general_spirit, seasonal_spirit])


class SeasonalContentTests(unittest.TestCase):
    def setUp(self):
        self.path = BACKEND_DIR / "seasonal_content.json"
        self.content = json.loads(self.path.read_text(encoding="utf-8"))

    def load_content(self):
        with patch("builtins.open", mock_open(read_data=json.dumps(self.content))):
            return generator.load_seasonal_content(self.path)

    def test_rejects_missing_month(self):
        del self.content["months"]["12"]
        with self.assertRaisesRegex(ValueError, "month keys"):
            self.load_content()

    def test_accepts_a_shorter_scene_list(self):
        self.content["months"]["01"]["scenes"] = ["Taking down Christmas lights"]

        loaded = self.load_content()

        self.assertEqual(loaded["months"]["01"]["scenes"], ["Taking down Christmas lights"])

    def test_rejects_an_empty_scene_list(self):
        self.content["months"]["01"]["scenes"] = []
        with self.assertRaisesRegex(ValueError, "Month 01 must have at least one scene"):
            self.load_content()

    def test_rejects_invalid_spirits(self):
        october = self.content["months"]["10"]
        spirits = october["spirits"]
        invalid_lists = (
            ("wrong count", spirits[:-1]),
            ("multiple words", [*spirits[:-1], "Deep Dark"]),
            ("duplicate", [*spirits[:-1], spirits[0].lower()]),
        )
        for reason, values in invalid_lists:
            with self.subTest(reason=reason):
                october["spirits"] = values
                with self.assertRaisesRegex(ValueError, "Month 10 must have exactly 8 distinct"):
                    self.load_content()
