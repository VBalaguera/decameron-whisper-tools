# decameron-whisper-tools

**[English](#english) · [Español](#español)**

---

## English

decameron-whisper-tools transcribes audio with OpenAI's **Whisper** on your own computer. Recordings never leave your machine.

It includes a terminal command, `decameron-transcribe`, which turns audio into a PDF.

### Requirements

- Python 3.10 or later.
- `ffmpeg`, which Whisper uses to read audio files:
  - macOS: `brew install ffmpeg`
  - Linux (Debian or Ubuntu): `sudo apt install ffmpeg`
  - Windows: `winget install ffmpeg`

### Install

```bash
git clone https://github.com/VBalaguera/decameron-whisper-tools.git
cd decameron-whisper-tools
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

On Windows, the fourth command is `.venv\Scripts\activate`.

Installing pulls in PyTorch, which takes over 1 GB.

### Usage

```bash
decameron-transcribe interview.m4a
```

Each segment is printed as soon as Whisper recognises it, with its start and end times, so you can follow the progress:

```text
[00:02.000 --> 00:05.000]  Hello, good morning.
[00:05.000 --> 00:08.000]  Today we are going to try the tool.
```

When it finishes, the transcript is saved as a PDF next to the audio, with the same name (`interview.pdf`), arranged in readable paragraphs without changing a single word. If that file already exists, it is overwritten.

The PDF opens with a header: the title (the audio file name without its extension, unless you pass `--title`) and a short record with the audio file name, the audio file's date, the date of the transcription, the model and the language.

Several files at once:

```bash
decameron-transcribe class.mp3 note.m4a
```

### Options

| Option | Default | Description |
|---|---|---|
| `--model` | `medium` | Whisper model: `tiny`, `base`, `small`, `medium`, `large-v3` or `turbo`. Larger models are more accurate but slower. |
| `--language` | `es` | Language code such as `es` or `en`, or `auto` to let Whisper detect it. |
| `--title` | file name | Title at the top of the PDF. With several files, all of them get the same title. |

The first time you use a model it is downloaded automatically (75 MB to 3 GB depending on the model). After that it is read from disk.

Supported audio formats: mp3, m4a, wav, flac, ogg, opus, aac, wma, aiff, webm, mp4, mkv, mov, avi, mpeg, amr.

### Tests

```bash
pip install -e ".[dev]"
pytest -q
```

---

## Español

decameron-whisper-tools transcribe audio con **Whisper**, de OpenAI, en tu propio ordenador. Las grabaciones nunca salen de él.

Incluye un comando de terminal, `decameron-transcribe`, que convierte un audio en un PDF.

### Requisitos

- Python 3.10 o posterior.
- `ffmpeg`, que Whisper usa para leer los archivos de audio:
  - macOS: `brew install ffmpeg`
  - Linux (Debian o Ubuntu): `sudo apt install ffmpeg`
  - Windows: `winget install ffmpeg`

### Instalación

```bash
git clone https://github.com/VBalaguera/decameron-whisper-tools.git
cd decameron-whisper-tools
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

En Windows, el cuarto comando es `.venv\Scripts\activate`.

La instalación descarga PyTorch, que ocupa más de 1 GB.

### Uso

```bash
decameron-transcribe entrevista.m4a
```

Cada segmento aparece en cuanto Whisper lo reconoce, con su inicio y su fin, para que puedas seguir el progreso:

```text
[00:02.000 --> 00:05.000]  Hola, buenos días.
[00:05.000 --> 00:08.000]  Hoy vamos a probar la herramienta.
```

Al terminar, la transcripción se guarda en un PDF junto al audio, con el mismo nombre (`entrevista.pdf`), organizada en párrafos legibles sin cambiar ninguna palabra. Si ese archivo ya existe, se sobrescribe.

El PDF empieza con una cabecera: el título (el nombre del audio sin la extensión, salvo que pases `--title`) y una ficha con el nombre del archivo, la fecha del audio, la fecha de la transcripción, el modelo y el idioma.

Varios archivos a la vez:

```bash
decameron-transcribe clase.mp3 nota.m4a
```

### Opciones

| Opción | Por defecto | Descripción |
|---|---|---|
| `--model` | `medium` | Modelo de Whisper: `tiny`, `base`, `small`, `medium`, `large-v3` o `turbo`. Los más grandes aciertan más pero tardan más. |
| `--language` | `es` | Código de idioma, como `es` o `en`, o `auto` para que Whisper lo detecte. |
| `--title` | nombre del archivo | Título al principio del PDF. Con varios archivos, todos reciben el mismo título. |

La primera vez que usas un modelo se descarga solo (entre 75 MB y 3 GB según el modelo). Después se lee del disco.

Formatos de audio admitidos: mp3, m4a, wav, flac, ogg, opus, aac, wma, aiff, webm, mp4, mkv, mov, avi, mpeg, amr.

### Pruebas

```bash
pip install -e ".[dev]"
pytest -q
```
