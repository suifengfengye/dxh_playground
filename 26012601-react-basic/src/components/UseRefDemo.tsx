/**
 * useRef: 用于存储不需要渲染的变量
 * 1. 存储DOM实例/多个DOM实例/
 * 2. 子组件实例（forwardRef）
 * 2. 缓存数据
 * 3. 控制渲染次数
 */
import { useEffect, useImperativeHandle, useRef } from 'react'

interface ChildProps {
    ref: React.Ref<{ focus: () => void }>;
}

const Child = ({ ref }: ChildProps) => {
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

export const UseRefDemo = () => {
    // const childRef = useRef<Child>(null);
    // 1. 单个引用DOM实例
    // const inputRef = useRef<HTMLInputElement>(null);
    // const inputRef2 = useRef<HTMLInputElement>(null);
    // // const allRef = useRef<Record<string, HTMLInputElement | Child>>(null);
    // console.log(inputRef);
    // console.log(inputRef2);
    // 2. 多个引用
    const inputRef = useRef<Record<string, HTMLInputElement | null>>({});
    console.log('inputRef', inputRef);

    useEffect(() => {
        console.log('inputRef.current.input1', inputRef);
    }, []);

    return (
        <>
            <input ref={(el) => { inputRef.current.input1 = el }} type="text" />
            <input ref={(el) => { inputRef.current.input2 = el }} type="text" />
            {/* <Child ref={childRef} /> */}

        </>
    )
}

// 2. 引用子组件实例
export const UseRefInstDemo = () => {
    const childRef = useRef<({ focus: () => void })>(null);

    useEffect(() => {
        console.log('childRef.current', childRef);
        childRef.current?.focus();
    }, []);

    return (
        <div>
            <Child ref={childRef} />
        </div>
    )
}

// 3. 缓存数据
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