import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@fontsource/inter/400.css'
import '@fontsource/inter/400-italic.css'
import '@fontsource/inter/700.css'
import '@fontsource/inter/700-italic.css'
import '@fontsource/vt323'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
