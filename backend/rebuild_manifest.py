"""Rebuild the manifest by scanning the whole bucket.

Serves as the one-time backfill and as an idempotent repair/reconciler: it
reflects the current bucket exactly, including legacy attribute values and any
deletions. Runs as a manual-invoke Lambda, or locally via `python rebuild_manifest.py`.
"""
import os
import boto3
from dotenv import load_dotenv
import common.manifest as manifest

s3 = boto3.client("s3")


def rebuild_manifest():
    bucket = os.environ["AWS_BUCKET_NAME"]
    entries = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key == manifest.MANIFEST_KEY or not key.lower().endswith(".jpg"):
                continue
            head = s3.head_object(Bucket=bucket, Key=key)
            entries.append(manifest.entry_from_metadata(key, head.get("Metadata", {}), obj["LastModified"]))

    entries.sort(key=lambda e: e["timestamp"] or "", reverse=True)
    doc = {"version": 1, "images": entries}
    count = manifest.save_manifest(bucket, doc, s3)
    print(f"Manifest rebuilt with {count} entries")
    return count


def lambda_handler(event, context):
    try:
        count = rebuild_manifest()
        return {"statusCode": 200, "count": count}
    except Exception as e:
        print(f"Error: {e}")
        raise e


if __name__ == "__main__":
    load_dotenv()
    rebuild_manifest()
