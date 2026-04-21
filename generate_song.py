#!/usr/bin/env python3
"""
gb-cansone: Generatore di canzone calabrese per GB Viaggi
Usa Google Lyria 3 Pro Preview via OpenRouter per creare una canzone
folk calabrese su Mari che protegge il suo gregge (i clienti GB) dal DLT.

Usage:
    python generate_song.py [--dry-run]
"""

import requests
import json
import base64
import argparse
import os
import sys
from pathlib import Path

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
if not OPENROUTER_API_KEY:
    print("ERROR: Set OPENROUTER_API_KEY environment variable.")
    sys.exit(1)
MODEL = "google/lyria-3-pro-preview"
OUTPUT_DIR = Path(__file__).parent / "output"

SONG_PROMPT = """
Generate a full-length Calabrian folk song in Italian dialect about a legendary woman named Mari,
guardian of the GB Viaggi travel agency flock (her beloved clients and colleagues), 
who protects them fiercely from the dreaded DLT — a monstrous bureaucratic beast that devours travel
subsidies and threatens the freedom to travel.

Style: Traditional Calabrian folk / pizzica / tarantella fusion.
Instruments: acoustic guitar, tamburello (frame drum), organetto (diatonic accordion), 
handclaps, violin, deep male chorus backing vocals.
Vocals: Strong, passionate female lead voice in Southern Italian style.
Tempo: 126 BPM, lively and rhythmic.
Key: D minor (melancholic but triumphant).
Duration: full-length song (approximately 3 minutes).

Structure:
- Intro: dramatic tarantella riff
- Verse 1: Mari's origin story, her love for her travelers
- Chorus: triumphant anthem against the DLT  
- Verse 2: the DLT attack — darkness, bureaucracy, fear
- Chorus
- Bridge: Mari's battle cry in Calabrian dialect
- Final Chorus: victory, the flock is safe, GB Viaggi lives on

Lyrics must include:
- References to Calabria, the sea, orange groves, and mountain winds
- The phrase "GB Viaggi" as a rallying cry
- "DLT" as the villain (can be personified as a faceless monster or dark wind)
- Mari described as a she-wolf / lupa protecting her cubs
- At least one verse in Calabrian dialect (e.g. "Ndavi a terra mia...")
- The refrain "Mari, Mari, lupa del Sud!" (Mari, Mari, she-wolf of the South!)

The song should be emotionally powerful, defiant, and ultimately victorious in tone.
"""


def generate_calabrian_song(dry_run: bool = False) -> dict:
    """
    Calls OpenRouter Lyria 3 Pro Preview to generate the GB Viaggi folk song.
    Returns dict with keys: lyrics (str), audio_path (Path or None).
    """
    OUTPUT_DIR.mkdir(exist_ok=True)

    if dry_run:
        print("[DRY RUN] Would call OpenRouter with model:", MODEL)
        print("[DRY RUN] Prompt length:", len(SONG_PROMPT), "chars")
        return {"lyrics": "[DRY RUN - no audio generated]", "audio_path": None}

    print(f"Calling OpenRouter API: {MODEL}")
    print("Generating full Calabrian folk song... (this may take 30-60 seconds)")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": SONG_PROMPT.strip()
            }
        ],
        "modalities": ["text", "audio"],
        "audio": {
            "format": "wav"
        },
        "stream": True
    }

    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/GBVAI/gb-cansone",
            "X-Title": "GB Cansone - Calabrian Folk Generator"
        },
        json=payload,
        stream=True,
        timeout=180
    )

    if resp.status_code != 200:
        print(f"ERROR: API returned {resp.status_code}")
        print(resp.text[:1000])
        sys.exit(1)

    audio_chunks = []
    lyrics_parts = []

    print("Streaming response...")
    for line in resp.iter_lines():
        if not line:
            continue
        decoded = line.decode("utf-8")
        if not decoded.startswith("data: "):
            continue
        data_str = decoded[6:]
        if data_str.strip() == "[DONE]":
            break
        try:
            chunk = json.loads(data_str)
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            content = delta.get("content") or ""
            if content:
                lyrics_parts.append(content)
                sys.stdout.write(".")
                sys.stdout.flush()
            audio = delta.get("audio", {})
            if audio.get("data"):
                audio_chunks.append(audio["data"])
                print(f"\n[Audio chunk received: {len(audio['data'])} b64 chars]")
        except json.JSONDecodeError:
            pass

    print("\nStream complete.")
    lyrics = "".join(lyrics_parts)

    # Save lyrics
    lyrics_path = OUTPUT_DIR / "la_lupa_del_sud.txt"
    lyrics_path.write_text(lyrics, encoding="utf-8")
    print(f"Lyrics saved: {lyrics_path}")

    # Save audio
    audio_path = None
    if audio_chunks:
        full_b64 = "".join(audio_chunks)
        audio_bytes = base64.b64decode(full_b64)
        audio_path = OUTPUT_DIR / "la_lupa_del_sud.wav"
        audio_path.write_bytes(audio_bytes)
        print(f"Audio saved: {audio_path} ({len(audio_bytes):,} bytes / {len(audio_bytes)/1024/1024:.1f} MB)")
    else:
        print("WARNING: No audio data in response (lyrics only).")

    return {"lyrics": lyrics, "audio_path": audio_path}


def print_lyrics(lyrics: str) -> None:
    """Pretty-print the song lyrics, stripping Lyria metadata tags."""
    lines = lyrics.split("\n")
    in_metadata = False
    for line in lines:
        # Lyria includes music metadata after lyrics — skip those blocks
        if line.startswith("mosic:") or line.startswith("bpm:") or line.startswith("duration_secs:"):
            in_metadata = True
        if in_metadata and line.startswith("[["):
            in_metadata = False
        if in_metadata:
            continue
        # Clean up timestamp markers like [12.0:] -> ""
        if line.startswith("[") and ":" in line and "]" in line[:line.index("]") + 1]:
            bracket_end = line.index("]") + 1
            text = line[bracket_end:].strip()
            if text:
                print(text)
        elif line.startswith("[[") and line.endswith("]]"):
            tag = line[2:-2]
            section_names = {"A0": "--- INTRO ---", "B1": "--- VERSO 1 ---",
                             "C2": "--- RITORNELLO ---", "D3": "--- VERSO 2 ---",
                             "E4": "--- BRIDGE ---", "F5": "--- RITORNELLO FINALE ---"}
            print(f"\n{section_names.get(tag, f'--- {tag} ---')}")
        else:
            if line.strip():
                print(line)


def main():
    parser = argparse.ArgumentParser(description="Genera La Lupa del Sud - canzone folk calabrese di GB Viaggi")
    parser.add_argument("--dry-run", action="store_true", help="Test mode - no API call")
    args = parser.parse_args()

    print("=" * 60)
    print("  GB CANSONE - La Lupa del Sud")
    print("  Canzone folk calabrese per GB Viaggi")
    print("  Modello: Google Lyria 3 Pro Preview via OpenRouter")
    print("=" * 60)
    print()

    result = generate_calabrian_song(dry_run=args.dry_run)

    if result["lyrics"] and not args.dry_run:
        print("\n" + "=" * 60)
        print("  TESTO DELLA CANZONE")
        print("=" * 60)
        print_lyrics(result["lyrics"])

    if result["audio_path"]:
        print(f"\nSong saved to: {result['audio_path']}")
    print("\nFatta! GB Viaggi vive!")


if __name__ == "__main__":
    main()
