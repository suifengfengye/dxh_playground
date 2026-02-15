import React from 'react';
import { SuspenseCacheDemo, SuspenseDemo } from './components/SuspenseDemoV3';

export default function App() {
    return (
        <div>
            <SuspenseDemo />
            <SuspenseCacheDemo />
        </div>
    );
}
