import React, { useEffect, useRef, useState } from 'react';

export function UseRefDemo() {
    // 获取 input 元素的引用
    const inputRef = useRef<HTMLInputElement>(null);

    return (
        <div>
            <input ref={inputRef} type="text" />
            <button onClick={() => inputRef.current?.focus()}>Focus Input</button>
        </div>
    );
}

export const UseRefDemo2 = () => {
    const inputRef = useRef<boolean>(false);
    const [count, setCount] = useState(0);


    useEffect(() => {
        inputRef.current = true;
        return () => {
            inputRef.current = false;
        }
    }, []);

    useEffect(() => {
        console.log('UseRefDemo2 useEffect')
        if (inputRef.current) {
            setCount(count + 1);
        }
    }, []);

    return (
        <div>
            <p>Count: {count}</p>
        </div>
    );
}

let strictModeEffectRuns = 0;

export const StrictModeEffectDemo = () => {
    const [runs, setRuns] = useState(0);

    useEffect(() => {
        strictModeEffectRuns += 1;
        setRuns(strictModeEffectRuns);
        return () => {};
    }, []);

    return (
        <div>
            <p>StrictMode effect runs: {runs}</p>
        </div>
    );
}
