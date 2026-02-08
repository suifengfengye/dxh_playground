import React from 'react';
import { StrictModeEffectDemo, UseRefDemo, UseRefDemo2 } from './components/UseRefDemo';

export default function App() {
    return (
        <div>
            <h1>Hello World!</h1>
            <UseRefDemo />
            <UseRefDemo2 />
            <StrictModeEffectDemo />
        </div>
    );
}
