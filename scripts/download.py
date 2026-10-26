#!/usr/bin/env python3
"""Download Quran API text, translations and optional tafsir/audio."""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

BASE = "https://quranapi.pages.dev/api"
OUT = Path("data")
TRANSLATIONS = ["arabic1", "arabic2", "bengali", "english", "urdu", "turkish", "uzbek"]
DOWNLOAD_AUDIO = os.getenv("DOWNLOAD_AUDIO", "false").lower() == "true"
DOWNLOAD_TAFSIR = os.getenv("DOWNLOAD_TAFSIR", "false").lower() == "true"
RECITER_ID = int(os.getenv("RECITER_ID", "1"))
if RECITER_ID not in range(1, 6):
    raise SystemExit("RECITER_ID must be between 1 and 5.")

manifest = {
    "source": "https://quranapi.pages.dev/",
    "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "files": [],
    "options": {"audio": DOWNLOAD_AUDIO, "reciter_id": RECITER_ID if DOWNLOAD_AUDIO else None,
                "tafsir": DOWNLOAD_TAFSIR},
}

def request_bytes(url: str, attempts: int = 4) -> bytes:
    last_error = None
    for attempt in range(attempts):
        try:
            req = Request(url, headers={"User-Agent": "QuranDataSync/1.0 (GitHub Actions)"})
            with urlopen(req, timeout=90) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}: {url}")
                return response.read()
        except (URLError, HTTPError, TimeoutError, RuntimeError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Failed after {attempts} attempts: {url}: {last_error}")

def save_bytes(url: str, path: Path, expected_json: bool = False) -> None:
    raw = request_bytes(url)
    if expected_json:
        # Parse before writing so HTML/error responses cannot masquerade as data.
        parsed = json.loads(raw.decode("utf-8-sig"))
        raw = (json.dumps(parsed, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    manifest["files"].append({
        "path": path.as_posix(),
        "size_bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "source_url": url,
    })
    print(f"Saved {path} ({len(raw):,} bytes)")

def main() -> None:
    OUT.mkdir(exist_ok=True)
    # All per-surah JSON files.
    for surah in range(1, 115):
        save_bytes(f"{BASE}/{surah}.json", OUT / "surahs" / f"{surah}.json", True)

    # Whole-Quran translation dumps. These include surah metadata and audio URLs.
    for language in TRANSLATIONS:
        save_bytes(f"{BASE}/{language}.json", OUT / "translations" / f"{language}.json", True)

    # Optional tafsir: one request per surah; sources may have separate reuse terms.
    if DOWNLOAD_TAFSIR:
        for surah in range(1, 115):
            save_bytes(f"{BASE}/tafsir/{surah}.json", OUT / "tafsir" / f"{surah}.json", True)

    # Optional full-surah audio, one reciter. Download directly from the URL
    # returned by the API, not from a guessed URL.
    if DOWNLOAD_AUDIO:
        for surah in range(1, 115):
            metadata_url = f"{BASE}/audio/{surah}.json"
            metadata = json.loads(request_bytes(metadata_url).decode("utf-8-sig"))
            reciter = metadata.get(str(RECITER_ID))
            if not reciter or not reciter.get("url"):
                raise RuntimeError(f"No audio URL for reciter {RECITER_ID}, surah {surah}")
            audio_url = reciter["url"]
            path = OUT / "audio" / f"reciter-{RECITER_ID}" / f"{surah:03d}.mp3"
            save_bytes(audio_url, path, False)
            time.sleep(0.15)

    manifest_path = OUT / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "README_DATA.md").write_text(
        "# Downloaded Quran data\n\n"
        f"- Surah JSON files: `surahs/1.json` through `surahs/114.json`\n"
        f"- Translation dumps: {', '.join('translations/' + x + '.json' for x in TRANSLATIONS)}\n"
        f"- Tafsir downloaded: `{DOWNLOAD_TAFSIR}`\n"
        f"- Audio downloaded: `{DOWNLOAD_AUDIO}`\n"
        + (f"- Audio reciter ID: `{RECITER_ID}`\n" if DOWNLOAD_AUDIO else "")
        + "\nFile sizes and SHA-256 hashes are recorded in `manifest.json`.\n"
        "Check source attribution and redistribution terms before publishing an app.\n",
        encoding="utf-8",
    )
    print(f"Finished. {len(manifest['files'])} files recorded in manifest.")

if __name__ == "__main__":
    main()
