"""Helpers for the image metadata manifest.

The manifest is a single JSON object stored in the image bucket that lists every
image with its attributes, so the frontend can download it once and filter
client-side. boto3 is imported lazily inside the functions that need it, so the
pure parsing helpers below can be unit-tested without AWS.
"""
import json
import re
from datetime import datetime, timezone

MANIFEST_KEY = "manifest.json"

_TS_RE = re.compile(r"(\d{8})-(\d{6})")


def _now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _timestamp_from_key(key, fallback=None):
    """Derive an ISO timestamp from a key like '20260720-130144.jpg'."""
    m = _TS_RE.search(key)
    if m:
        try:
            dt = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
            return dt.isoformat().replace("+00:00", "Z")
        except ValueError:
            pass
    return fallback


def entry_from_metadata(key, metadata, last_modified=None):
    """Build one manifest entry from an object's key and S3 metadata dict."""
    spirits_raw = (metadata or {}).get("spirits", "") or ""
    spirits = [s.strip() for s in spirits_raw.split(",") if s.strip()]
    fallback_ts = None
    if last_modified is not None:
        fallback_ts = last_modified.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "key": key,
        "timestamp": _timestamp_from_key(key, fallback_ts),
        "subject": (metadata or {}).get("subject", ""),
        "scene": (metadata or {}).get("scene", ""),
        "spirits": spirits,
        "model": (metadata or {}).get("model", ""),
        "prompt": (metadata or {}).get("prompt", ""),
    }


def _empty_manifest():
    return {"version": 1, "updated": None, "count": 0, "images": []}


def _client(s3=None):
    if s3 is not None:
        return s3
    import boto3
    return boto3.client("s3")


def load_manifest(bucket, s3=None):
    from botocore.exceptions import ClientError
    s3 = _client(s3)
    try:
        obj = s3.get_object(Bucket=bucket, Key=MANIFEST_KEY)
        return json.loads(obj["Body"].read())
    except ClientError as e:
        if e.response["Error"]["Code"] in ("NoSuchKey", "404", "NotFound"):
            return _empty_manifest()
        raise


def save_manifest(bucket, manifest, s3=None):
    s3 = _client(s3)
    manifest["updated"] = _now_iso()
    manifest["count"] = len(manifest.get("images", []))
    body = json.dumps(manifest, ensure_ascii=False).encode("utf-8")
    s3.put_object(Bucket=bucket, Key=MANIFEST_KEY, Body=body, ContentType="application/json")
    return manifest["count"]


def append_entry(bucket, entry, s3=None):
    """Prepend a new entry (newest-first), de-duplicating by key. Single-writer safe."""
    s3 = _client(s3)
    manifest = load_manifest(bucket, s3)
    images = [e for e in manifest.get("images", []) if e.get("key") != entry["key"]]
    images.insert(0, entry)
    manifest["images"] = images
    return save_manifest(bucket, manifest, s3)
