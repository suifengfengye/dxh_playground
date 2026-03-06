import React from 'react'
import { createRoot } from 'react-dom/client'

import App from './App'

const rootEle = document.getElementById('root')

createRoot(rootEle!).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
)