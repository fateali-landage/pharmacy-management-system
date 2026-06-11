"""
Firebase Admin SDK initialization.

Supports multiple credential sources (in priority order):
  1. FIREBASE_CREDENTIALS_JSON      — raw JSON string env var
  2. FIREBASE_CREDENTIALS_JSON_BASE64 — base64-encoded JSON env var
  3. FIREBASE_CREDENTIALS / GOOGLE_APPLICATION_CREDENTIALS — file path env vars
  4. Local service-account JSON files in project root or ./credentials/

Returns (db, bucket) tuple.  Both values are None when no credentials are found,
allowing the app to run in a degraded / mock mode for local development.
"""

import os
import json
import base64
from typing import Optional, Tuple
from firebase_admin import credentials, firestore, initialize_app, storage, _apps


def _build_credential() -> Optional[credentials.Certificate]:
    """Try every known credential source and return the first that works."""

    # 1) Raw JSON string
    raw_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    if raw_json:
        try:
            return credentials.Certificate(json.loads(raw_json))
        except Exception:
            pass

    # 2) Base64-encoded JSON
    b64_json = (
        os.environ.get("FIREBASE_CREDENTIALS_JSON_BASE64")
        or os.environ.get("FIREBASE_CREDENTIALS_B64")
    )
    if b64_json:
        try:
            decoded = base64.b64decode(b64_json).decode("utf-8")
            return credentials.Certificate(json.loads(decoded))
        except Exception:
            pass

    # 3) Explicit file-path env vars
    for env_var in ("FIREBASE_CREDENTIALS", "GOOGLE_APPLICATION_CREDENTIALS"):
        path = os.environ.get(env_var)
        if path and os.path.exists(path):
            try:
                return credentials.Certificate(path)
            except Exception:
                pass

    # 4) Well-known local filenames (root dir and ./credentials/ sub-dir)
    here = os.path.dirname(os.path.abspath(__file__))
    # Walk up one level to reach the project root
    project_root = os.path.dirname(here)
    for base_dir in [project_root, os.path.join(project_root, "credentials")]:
        for fname in (
            "serviceAccount.json",
            "serviceAccountKey.json",
            "firebase_credentials.json",
            "firebase-key.json",
        ):
            candidate = os.path.join(base_dir, fname)
            if os.path.exists(candidate):
                try:
                    return credentials.Certificate(candidate)
                except Exception:
                    pass

    return None


def initialize_firebase() -> Tuple[Optional[object], Optional[object]]:
    """
    Initialize the Firebase Admin SDK (idempotent — safe to call multiple times).

    Returns:
        (db, bucket): Firestore client and Storage bucket, or (None, None) on failure.
    """
    try:
        bucket_name = (
            os.environ.get("FIREBASE_STORAGE_BUCKET")
            or os.environ.get("GOOGLE_CLOUD_STORAGE_BUCKET")
            or os.environ.get("GCS_BUCKET")
        )
        app_options = {"storageBucket": bucket_name} if bucket_name else None

        if not _apps:
            cred = _build_credential()
            if cred is not None:
                initialize_app(cred, app_options)
            else:
                try:
                    # Fallback to Application Default Credentials (ADC)
                    initialize_app(options=app_options)
                    print("[firebase_config] Initialized Firebase Admin SDK via Application Default Credentials (ADC).")
                except Exception as adc_exc:
                    print(
                        f"[firebase_config] No credentials found and ADC fallback failed: {adc_exc}. "
                        "Set FIREBASE_CREDENTIALS_JSON or GOOGLE_APPLICATION_CREDENTIALS. "
                        "App will run without database access."
                    )
                    return None, None

        try:
            db = firestore.client()
            # Only attempt to get a Storage bucket if the name is explicitly configured
            if bucket_name:
                try:
                    bucket = storage.bucket(bucket_name)
                except Exception as bucket_exc:
                    print(f"[firebase_config] Storage bucket initialization failed (non-fatal): {bucket_exc}")
                    bucket = None
            else:
                bucket = None
            return db, bucket
        except Exception as client_exc:
            print(f"[firebase_config] Firestore/Storage client initialization failed: {client_exc}")
            # Clean up the app registration to keep _apps consistent
            from firebase_admin import delete_app, get_app
            try:
                delete_app(get_app())
            except Exception:
                pass
            return None, None

    except Exception as exc:
        print(f"[firebase_config] Initialization error: {exc}")
        return None, None
