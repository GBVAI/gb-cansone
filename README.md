# gb-cansone 🎵

Generatore di canzone folk calabrese per GB Viaggi.

Usa **Google Lyria 3 Pro Preview** via OpenRouter per creare una ballata folk calabrese su **Mari** — la guardiana di GB Viaggi che protegge il suo gregge di viaggiatori dal temibile **DLT**.

---

## La Storia

**Mari** e' la leggendaria responsabile di GB Viaggi — lupa del Sud, madre e guerriera.
Il suo gregge sono i clienti e i colleghi di GB Viaggi, che lei difende con ferocia.
Il **DLT** e' il mostro burocratico che minaccia la liberta' di viaggiare e i sussidi viaggi.
Mari lo combatte, e vince.

---

## Requisiti

- Python 3.8+
- `requests` library

```bash
pip install requests
```

---

## Utilizzo

```bash
# Genera la canzone completa (audio WAV + testo)
python generate_song.py

# Modalita' test (nessuna chiamata API)
python generate_song.py --dry-run

# Con chiave API custom
OPENROUTER_API_KEY=sk-or-... python generate_song.py
```

L'audio viene salvato in `output/la_lupa_del_sud.wav`.
Il testo viene salvato in `output/la_lupa_del_sud.txt`.

---

## Modello

- **Google Lyria 3 Pro Preview** (`google/lyria-3-pro-preview`)
- Provider: Google AI Studio via OpenRouter
- Output: audio WAV 48kHz, canzone completa (~3 minuti)
- Costo: $0.08 per canzone

---

## Stile Musicale

- **Genere**: Folk calabrese / pizzica / tarantella fusion
- **Strumenti**: chitarra acustica, tamburello, organetto, violino, coro maschile
- **Voce**: soprano femminile potente in stile Sud Italia
- **BPM**: 126
- **Tonalita'**: Re minore (malinconico ma trionfante)

---

## Output di Esempio

```
--- INTRO ---
(riff di tarantella drammatica)

--- VERSO 1 ---
Ndavi a terra mia, tra 'u mare e a muntagna,
C'e' una donna forte, Mari, la compagna...

--- RITORNELLO ---
Mari, Mari, lupa del Sud!
GB Viaggi non si arrende mai!
Il DLT non ci ferma piu',
Mari, Mari, porta i tuoi figli via!
```

---

## Struttura Repository

```
gb-cansone/
  generate_song.py    # Script principale
  README.md           # Questo file
  output/             # Audio e testi generati (gitignored)
    la_lupa_del_sud.wav
    la_lupa_del_sud.txt
```

---

## Note Tecniche

L'API OpenRouter per Lyria richiede:
- `modalities: ["text", "audio"]`
- `audio: { format: "wav" }`
- `stream: true` (obbligatorio per output audio)

La risposta arriva in streaming SSE. L'audio e' base64-encoded in un chunk `delta.audio.data`,
il testo/lirica in `delta.content`.

---

*GB Viaggi vive! La lupa del Sud non dorme mai.*
