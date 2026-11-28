import { useEffect, useState, type FormEvent } from 'react'
import { HugeiconsIcon } from '@hugeicons/react'
import { AlertCircleIcon, Download04Icon, FileMusicIcon, Loading03Icon } from '@hugeicons/core-free-icons'

type Options = { models: string[]; model: string; language: string }

type Status =
  | { kind: 'idle' }
  | { kind: 'working' }
  | { kind: 'done'; url: string; name: string }
  | { kind: 'error'; message: string }

function pdfName(audio: File) {
  const dot = audio.name.lastIndexOf('.')
  return `${dot > 0 ? audio.name.slice(0, dot) : audio.name}.pdf`
}

async function errorMessage(response: Response): Promise<string> {
  const body = await response.json().catch(() => null)
  return typeof body?.detail === 'string' ? body.detail : `Error ${response.status}`
}

function App() {
  const [options, setOptions] = useState<Options | null>(null)
  const [audio, setAudio] = useState<File | null>(null)
  const [model, setModel] = useState('')
  const [language, setLanguage] = useState('')
  const [title, setTitle] = useState('')
  const [status, setStatus] = useState<Status>({ kind: 'idle' })

  useEffect(() => {
    fetch('/api/options')
      .then((response) => response.json())
      .then((data: Options) => {
        setOptions(data)
        setModel(data.model)
        setLanguage(data.language)
      })
      .catch(() => setStatus({ kind: 'error', message: 'No se puede conectar con el servidor. ¿Está en marcha decameron-web?' }))
  }, [])

  useEffect(() => {
    return () => {
      if (status.kind === 'done') URL.revokeObjectURL(status.url)
    }
  }, [status])

  async function submit(event: FormEvent) {
    event.preventDefault()
    if (!audio) return
    const form = new FormData()
    form.append('audio', audio)
    form.append('model', model)
    form.append('language', language)
    form.append('title', title)
    form.append('last_modified', String(audio.lastModified))
    setStatus({ kind: 'working' })
    try {
      const response = await fetch('/api/transcribe', { method: 'POST', body: form })
      if (!response.ok) {
        setStatus({ kind: 'error', message: await errorMessage(response) })
        return
      }
      const url = URL.createObjectURL(await response.blob())
      setStatus({ kind: 'done', url, name: pdfName(audio) })
    } catch {
      setStatus({ kind: 'error', message: 'Se ha perdido la conexión con el servidor.' })
    }
  }

  const working = status.kind === 'working'

  return (
    <main>
      <h1>Decameron</h1>
      <p>Transcribe un audio con Whisper en tu ordenador y descárgalo como PDF en párrafos.</p>

      <form onSubmit={submit}>
        <label className="file">
          <HugeiconsIcon icon={FileMusicIcon} size={20} />
          <span>{audio ? audio.name : 'Elige un archivo de audio'}</span>
          <input
            type="file"
            accept="audio/*,video/*"
            disabled={working}
            onChange={(event) => {
              setAudio(event.target.files?.[0] ?? null)
              setStatus({ kind: 'idle' })
            }}
          />
        </label>

        <label>
          Modelo
          <select value={model} disabled={working || !options} onChange={(event) => setModel(event.target.value)}>
            {options?.models.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Idioma
          <input
            value={language}
            disabled={working}
            placeholder="es, en o auto"
            onChange={(event) => setLanguage(event.target.value)}
          />
        </label>

        <label>
          Título
          <input
            value={title}
            disabled={working}
            placeholder={audio ? pdfName(audio).slice(0, -4) : 'El nombre del audio'}
            onChange={(event) => setTitle(event.target.value)}
          />
        </label>

        <button type="submit" disabled={!audio || !options || working}>
          Transcribir
        </button>
      </form>

      <section className="status" aria-live="polite">
        {status.kind === 'working' && (
          <p>
            <HugeiconsIcon icon={Loading03Icon} size={20} className="spin" />
            <span>Transcribiendo... Con audios largos o modelos grandes puede tardar varios minutos.</span>
          </p>
        )}
        {status.kind === 'done' && (
          <a href={status.url} download={status.name}>
            <HugeiconsIcon icon={Download04Icon} size={20} />
            <span>Descargar {status.name}</span>
          </a>
        )}
        {status.kind === 'error' && (
          <p>
            <HugeiconsIcon icon={AlertCircleIcon} size={20} />
            <span>{status.message}</span>
          </p>
        )}
      </section>

      <footer>Decameron 0.2.0</footer>
    </main>
  )
}

export default App
