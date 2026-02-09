import React from 'react';
import { UseRefCacheDemo } from './components/UseRefDemoV3';
// import { UseRefInstDemo } from './components/UseRefDemoV3';
// import { UseMultiRefDemo } from './components/UseRefDemoV3';
// import { UseRefDemo } from './components/UseRefDemoV3';

export default function App() {
    return (
        <div>
            <h1>Hello World!</h1>
            {/* <UseRefDemo /> */}
            {/* <UseMultiRefDemo /> */}
            {/* <UseRefInstDemo /> */}
            <UseRefCacheDemo />
        </div>
    );
}
