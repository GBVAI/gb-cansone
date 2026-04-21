#!/usr/bin/env python3
"""
gb-cansone: Versione Zampogna - La Pastora del Sogno
Canzone folk calabrese di montagna con zampogna dominante.

Usage:
    OPENROUTER_API_KEY=sk-or-... python3 generate_zampogna.py
"""

import requests
import json
import base64
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
Generate a full-length Calabrian folk song in Italian and Calabrian dialect about a legendary woman named Mari,
guardian of the GB Viaggi travel agency, who protects her beloved flock of travelers from the dreaded DLT —
a faceless bureaucratic monster that devours travel subsidies and chokes the freedom to roam.

Style: Deep Calabrian mountain folk. The ZAMPOGNA (Southern Italian double-pipe bagpipe) is the
DOMINANT, LEAD instrument — it must be prominent, droning, and haunting throughout the entire song.
Think ancient, pastoral, sacred — like a shepherd's lament that turns into a battle hymn.

Instruments (in order of prominence):
1. ZAMPOGNA — the soul of the song, present in every section, loud droning bass + melody pipe
2. Ciaramella (shawm/oboe-like pipe) — piercing high calls, duet with zampogna
3. Tamburello (frame drum) — steady village-dance pulse
4. Deep male chorus (a cappella moments) — dark, resonant, ancient
5. Female lead voice — raw, gravelly, folk-priestess energy
6. Handclaps and foot stomps
7. NO accordion, NO modern instruments

Tempo: 112 BPM, heavy and hypnotic, with rubato passages for the zampogna solos.
Key: E Phrygian (ancient, dark, modal — like Calabrian sacred music).
Duration: full-length song (approximately 3-4 minutes).
Atmosphere: midnight shepherd fire, mountain fog, ancient magic, defiant grief turning to triumph.

Structure:
- Intro: Long zampogna drone solo, ciaramella enters, building slowly — no rush
- Verse 1: Female lead over zampogna drone, slow and mournful, Mari's origin
- Interlude: Zampogna solo instrumental break — pastoral and haunting
- Verse 2: The DLT descends — music intensifies, tamburello enters hard
- Chorus: Big, stomping, the whole village sings against the DLT — zampogna wails above all
- Bridge: Calabrian dialect — spoken/sung over just zampogna drone
- Final Chorus: Maximum intensity, zampogna screaming, drums pounding, voices unleashed
- Outro: Zampogna drone fades slowly back into the mountain fog

Lyrics must include:
- References to the Aspromonte mountains, the Ionian sea, shepherd fires at night
- Mari described as "vecchia lupa" (old she-wolf) and "pastora del sogno" (shepherd of dreams)
- "GB Viaggi" as the name of her flock
- "DLT" personified as a cold wind from the north that steals warmth
- At least 8 lines in Calabrian dialect
- The refrain: "Zampogna, suona! Mari non muore!" (Bagpipe, play! Mari does not die!)
- A moment of pure silence before the final chorus drop

Emotional arc: grief -> defiance -> ancient power -> total victory
"""


def generate():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("=" * 60)
    print("  GB CANSONE - Versione Zampogna")
    print("  La Pastora del Sogno")
    print("  Modello: Google Lyria 3 Pro Preview via OpenRouter")
    print("=" * 60)
    print()
    print("Generating full Calabrian mountain folk song...")
    print("(Zampogna dominant — 3-4 minutes — may take 60-90 seconds)")
    print()

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": SONG_PROMPT.strip()}],
        "modalities": ["text", "audio"],
        "audio": {"format": "wav"},
        "stream": True
    }

    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/GBVAI/gb-cansone",
            "X-Title": "GB Cansone - Zampogna Version"
        },
        json=payload,
        stream=True,
        timeout=300
    )

    if resp.status_code != 200:
        print(f"ERROR: API returned {resp.status_code}")
        try:
            print(resp.json())
        except Exception:
            print(resp.text[:500])
        sys.exit(1)

    audio_chunks = []
    lyrics_parts = []

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
                size_mb = len(audio["data"]) * 0.75 / 1024 / 1024
                print(f"\n[Audio received: ~{size_mb:.1f} MB]")
        except json.JSONDecodeError:
            pass

    print("\nStream complete.")
    lyrics = "".join(lyrics_parts)

    # Save lyrics
    lp = OUTPUT_DIR / "zampogna_del_sud.txt"
    lp.write_text(lyrics, encoding="utf-8")
    print(f"Lyrics: {lp}")

    # Save audio
    if audio_chunks:
        full_b64 = "".join(audio_chunks)
        audio_bytes = base64.b64decode(full_b64)
        ap = OUTPUT_DIR / "zampogna_del_sud.wav"
        ap.write_bytes(audio_bytes)
        print(f"Audio:  {ap} ({len(audio_bytes) / 1024 / 1024:.1f} MB)")
    else:
        print("WARNING: No audio in response (lyrics only).")

    # Print clean lyrics
    print("\n" + "=" * 60)
    print("  TESTO - La Pastora del Sogno")
    print("=" * 60)
    lines = lyrics.split("\n")
    in_meta = False
    section_map = {
        "A0": "--- INTRO (Zampogna Solo) ---",
        "B1": "--- VERSO 1 ---",
        "C2": "--- INTERLUDIO (Zampogna) ---",
        "D3": "--- VERSO 2 (Il DLT arriva) ---",
        "E4": "--- RITORNELLO ---",
        "F5": "--- BRIDGE (Dialetto calabrese) ---",
        "G6": "--- RITORNELLO FINALE ---",
        "H7": "--- OUTRO (Zampogna nel vento) ---",
    }
    for line in lines:
        if line.startswith("mosic:") or line.startswith("bpm:") or line.startswith("duration_secs:"):
            in_meta = True
        if in_meta and line.startswith("[["):
            break
        if in_meta:
            continue
        if line.startswith("[[") and line.endswith("]]"):
            tag = line[2:-2]
            print(f"\n{section_map.get(tag, f'--- {tag} ---')}")
        elif line.startswith("[") and ":" in line and "]" in line:
            bracket_end = line.index("]") + 1
            text = line[bracket_end:].strip()
            if text:
                print(text)
        else:
            if line.strip():
                print(line)

    print("\nFatta! Zampogna, suona! GB Viaggi non muore!")


if __name__ == "__main__":
    generate()
