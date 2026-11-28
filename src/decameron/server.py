import os
import shutil
import tempfile
import threading
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from decameron.engine import DEFAULT_LANGUAGE, DEFAULT_MODEL, MODELS, WhisperEngine
from decameron.transcribe import audio_problem, transcribe_to_pdf

HOST = "127.0.0.1"
PORT = 8000


def create_app(engine: WhisperEngine) -> FastAPI:
    app = FastAPI(title="Decameron")
    lock = threading.Lock()

    @app.get("/api/options")
    def options() -> dict:
        return {"models": list(MODELS), "model": DEFAULT_MODEL, "language": DEFAULT_LANGUAGE}

    @app.post("/api/transcribe")
    def transcribe(
        audio: Annotated[UploadFile, File()],
        model: Annotated[str, Form()] = DEFAULT_MODEL,
        language: Annotated[str, Form()] = DEFAULT_LANGUAGE,
        title: Annotated[str, Form()] = "",
        last_modified: Annotated[int | None, Form()] = None,
    ) -> Response:
        if model not in MODELS:
            raise HTTPException(400, f"Unknown model '{model}'.")
        name = Path(audio.filename or "").name
        if name in ("", ".."):
            raise HTTPException(400, "The audio file has no valid name.")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / name
            with path.open("wb") as target:
                shutil.copyfileobj(audio.file, target)
            problem = audio_problem(path)
            if problem:
                raise HTTPException(400, problem)
            if last_modified is not None:
                seconds = last_modified / 1000
                os.utime(path, (seconds, seconds))
            requested = None if language.strip().lower() == "auto" else language.strip()
            with lock:
                try:
                    saved = transcribe_to_pdf(
                        engine, path, path.with_suffix(".pdf"), model, requested, title.strip() or None
                    )
                except (OSError, RuntimeError, ValueError) as e:
                    raise HTTPException(500, f"Error transcribing '{name}': {e}") from e
            if saved is None:
                raise HTTPException(422, f"No speech found in '{name}'.")
            return Response(saved.read_bytes(), media_type="application/pdf")

    return app


def main() -> None:
    import uvicorn

    print(f"Decameron web server on http://{HOST}:{PORT}", flush=True)
    uvicorn.run(create_app(WhisperEngine()), host=HOST, port=PORT)


if __name__ == "__main__":
    main()
