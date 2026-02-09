/**
 * useRef: 用于缓存不需要渲染的变量
 * 1. 存储DOM实例/多个DOM实例
 * 2. 存储子组件实例
 * 3. 缓存数据
 */

import { useEffect, useImperativeHandle, useRef } from "react"

export const UseRefDemo = () => {
    const inputRef = useRef<HTMLInputElement>(null);
    console.log('inputRef', inputRef);
    return (
        <div>
            <input ref={inputRef} type="text" />
        </div>
    )
}

export const UseMultiRefDemo = () => {
    const listRef = useRef<Record<string, HTMLInputElement | null>>({});
    console.log('listRef', listRef);
    return (
        <div>
            {
                ['input1', 'input2'].map((key) => (
                    <input key={key} ref={(el) => { listRef.current[key] = el }} type="text" />
                ))
            }
            {/* <input ref={(el) => { listRef.current.input1 = el }} type="text" />
            <input ref={(el) => { listRef.current.input2 = el }} type="text" /> */}
        </div>
    )
}

const Child = ({ ref }: { ref: React.Ref<{ focus: () => void }> }) => {
    useImperativeHandle(ref, () => ({
        focus: () => {
            console.log('focus in child');
        }
    }))
    return (
        <div>
            <h1>Child</h1>
        </div>
    )
}

export const UseRefInstDemo = () => {
    const childRef = useRef<({ focus: () => void })>(null);
    console.log('childRef', childRef);
    return (
        <div>
            <Child ref={childRef} />
        </div>
    )
}

export const UseRefCacheDemo = () => {
    const cacheRef = useRef<Record<string, any>>({});
    console.log('cacheRef', cacheRef);

    useEffect(() => {
        cacheRef.current = {
            mount: true,
        };
        console.log('@@@@cacheRef.current', cacheRef);
        return () => {
            cacheRef.current = {};
        }
    }, []);

    return (
        <div>
            <h1>UseRefCacheDemo</h1>
        </div>
    )
}