import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { VERSION } from '@dxh-monorepo/core'
import { genRandomNum } from '@dxh-monorepo/utils'

const app = document.getElementById('app')

if (!app) {
    throw new Error('App root not found')
}

createRoot(app).render(
    <StrictMode>
        {`my monorepo app, version:${VERSION},random:${genRandomNum()}`}
    </StrictMode>
)
