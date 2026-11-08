import sys
import unittest
from base64 import b64encode
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    import boto3  # noqa: F401
except ModuleNotFoundError:
    sys.modules["boto3"] = Mock()

import common.s3 as s3


class GetLatestFileTests(unittest.TestCase):
    @patch("common.s3.boto3.client")
    def test_scans_all_pages_and_selects_latest_jpg(self, mock_boto_client):
        s3_client = mock_boto_client.return_value
        paginator = Mock()
        s3_client.get_paginator.return_value = paginator

        first_page_time = datetime(2026, 7, 31, 13, 1, 47, tzinfo=timezone.utc)
        first_page = {
            "Contents": [
                {
                    "Key": f"old-{index:04d}.jpg",
                    "LastModified": first_page_time + timedelta(seconds=index),
                }
                for index in range(1000)
            ]
        }
        latest_key = "20260801-130126.jpg"
        second_page = {
            "Contents": [
                {
                    "Key": "manifest.json",
                    "LastModified": datetime(2026, 8, 1, 13, 1, 30, tzinfo=timezone.utc),
                },
                {
                    "Key": latest_key,
                    "LastModified": datetime(2026, 8, 1, 13, 1, 29, tzinfo=timezone.utc),
                },
            ]
        }
        paginator.paginate.return_value = [first_page, second_page]
        expected_object = {"Body": b"image", "Metadata": {"prompt": "latest"}}
        s3_client.get_object.return_value = expected_object

        result = s3.get_latest_file("bear-of-the-day")

        self.assertEqual(result, (expected_object, {"prompt": "latest"}, latest_key))
        s3_client.get_paginator.assert_called_once_with("list_objects_v2")
        paginator.paginate.assert_called_once_with(Bucket="bear-of-the-day")
        s3_client.get_object.assert_called_once_with(
            Bucket="bear-of-the-day",
            Key=latest_key,
        )

    @patch("common.s3.boto3.client")
    def test_decodes_latest_images_metadata(self, mock_boto_client):
        client = mock_boto_client.return_value
        key = "20261101-130000.jpg"
        scene = "Leading a St. Martin\u2019s lantern procession"
        client.get_paginator.return_value.paginate.return_value = [{
            "Contents": [{"Key": key, "LastModified": datetime(2026, 11, 1, tzinfo=timezone.utc)}]
        }]
        client.get_object.return_value = {
            "Metadata": {
                "scene": b64encode(scene.encode("utf-8")).decode("ascii"),
                "subject": "Brown Bear",
                "bear-utf8-fields": "scene",
            }
        }

        _, metadata, image_key = s3.get_latest_file("bear-of-the-day")

        self.assertEqual(image_key, key)
        self.assertEqual(metadata, {"scene": scene, "subject": "Brown Bear"})


if __name__ == "__main__":
    unittest.main()
