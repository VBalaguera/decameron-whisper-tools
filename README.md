# decameron-whisper-tools

**[English](#english) · [Español](#español)**

---

## English

decameron-whisper-tools transcribes audio with OpenAI's **Whisper** on your own computer. Recordings never leave your machine.

It includes a terminal command, `decameron-transcribe`, which turns audio into a PDF, and a web page that does the same from the browser.

### Requirements

- Python 3.10 or later.
- `ffmpeg`, which Whisper uses to read audio files:
  - macOS: `brew install ffmpeg`
  - Linux (Debian or Ubuntu): `sudo apt install ffmpeg`
  - Windows: `winget install ffmpeg`
- For the web page only: Node.js 20.19 or later.

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

When it finishes, the transcript is saved as a PDF next to the audio, with the same name (`interview.pdf`), arranged in readable paragraphs without changing a single word. With `--output`, it is saved in that folder instead.

If the PDF already exists, the command asks whether to overwrite it before transcribing. If you answer no, or if it is not run from an interactive terminal, that audio is skipped.

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
| `--output` | next to the audio | Folder where the PDFs are saved. It is created if it does not exist. |

The first time you use a model it is downloaded automatically (75 MB to 3 GB depending on the model). After that it is read from disk.

Supported audio formats: mp3, m4a, wav, flac, ogg, opus, aac, wma, aiff, webm, mp4, mkv, mov, avi, mpeg, amr.

### Web page

The web page transcribes one audio at a time and gives you the PDF to download. It has two parts that run on your computer: a server, `decameron-web`, which runs Whisper, and the page itself, in the `web` folder.

Install them once:

```bash
pip install -e ".[web]"
cd web
npm install
```

Then, every time you want to use it, start the server in one terminal:

```bash
decameron-web
```

And the page in another one, from the `web` folder:

```bash
npm run dev
```

Open http://localhost:5173, choose an audio file, the model, the language and, if you want, a title, and press **Transcribir**. The page shows that it is working until the PDF is ready, and then a link to download it. Each segment is printed in the server's terminal as Whisper recognises it, just like with the command.

The PDF is the same as the one the command makes, with the same header and the audio file's own date. The server keeps nothing: it saves the audio and the PDF in a temporary folder and deletes them as soon as it has sent the PDF.

The server only accepts connections from your own computer (`127.0.0.1`, port 8000), and it transcribes one audio at a time.

### Tests

```bash
pip install -e ".[dev]"
pytest -q
```

To check the web page, from the `web` folder:

```bash
npm run lint
npm run build
```

---

## Español

decameron-whisper-tools transcribe audio con **Whisper**, de OpenAI, en tu propio ordenador. Las grabaciones nunca salen de él.

Incluye un comando de terminal, `decameron-transcribe`, que convierte un audio en un PDF, y una página web que hace lo mismo desde el navegador.

### Requisitos

- Python 3.10 o posterior.
- `ffmpeg`, que Whisper usa para leer los archivos de audio:
  - macOS: `brew install ffmpeg`
  - Linux (Debian o Ubuntu): `sudo apt install ffmpeg`
  - Windows: `winget install ffmpeg`
- Solo para la página web: Node.js 20.19 o posterior.

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

Al terminar, la transcripción se guarda en un PDF junto al audio, con el mismo nombre (`entrevista.pdf`), organizada en párrafos legibles sin cambiar ninguna palabra. Con `--output`, se guarda en esa carpeta.

Si el PDF ya existe, el comando pregunta si quieres sobrescribirlo antes de transcribir. Si respondes que no, o si no se ejecuta desde una terminal interactiva, se salta ese audio.

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
| `--output` | junto al audio | Carpeta donde se guardan los PDF. Se crea si no existe. |

La primera vez que usas un modelo se descarga solo (entre 75 MB y 3 GB según el modelo). Después se lee del disco.

Formatos de audio admitidos: mp3, m4a, wav, flac, ogg, opus, aac, wma, aiff, webm, mp4, mkv, mov, avi, mpeg, amr.

### Página web

La página web transcribe un audio cada vez y te da el PDF para descargarlo. Tiene dos partes que se ejecutan en tu ordenador: un servidor, `decameron-web`, que ejecuta Whisper, y la página, en la carpeta `web`.

Se instalan una sola vez:

```bash
pip install -e ".[web]"
cd web
npm install
```

Después, cada vez que quieras usarla, arranca el servidor en una terminal:

```bash
decameron-web
```

Y la página en otra, desde la carpeta `web`:

```bash
npm run dev
```

Abre http://localhost:5173, elige un archivo de audio, el modelo, el idioma y, si quieres, un título, y pulsa **Transcribir**. La página indica que está trabajando hasta que el PDF está listo y después muestra un enlace para descargarlo. Cada segmento aparece en la terminal del servidor en cuanto Whisper lo reconoce, igual que con el comando.

El PDF es el mismo que crea el comando, con la misma cabecera y la fecha propia del audio. El servidor no conserva nada: guarda el audio y el PDF en una carpeta temporal y los borra en cuanto ha enviado el PDF.

El servidor solo acepta conexiones desde tu propio ordenador (`127.0.0.1`, puerto 8000) y transcribe un audio cada vez.

### Pruebas

```bash
pip install -e ".[dev]"
pytest -q
```

Para comprobar la página web, desde la carpeta `web`:

```bash
npm run lint
npm run build
```
