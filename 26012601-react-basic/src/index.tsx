import React from 'react';
import { createRoot } from 'react-dom/client';

import './main.css';

const root = createRoot(document.getElementById('app')!);
root.render(
    <h1>Hello World!</h1>
);
