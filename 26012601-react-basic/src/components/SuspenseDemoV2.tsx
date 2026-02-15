/**
 * Suspense的作用：
 * 1. 按需/异步加载组件 + lazy
 * 2. 缓存数据 + use() hook
 */

import React, { use } from "react";
import { Suspense } from "react"
// import { Child } from "./Child"
const Child = React.lazy(() => import('./Child'));

export const SuspenseDemo = () => {
    return (
        <div>
            <Suspense fallback={<div>Loading...</div>}>
                <Child />
            </Suspense>
        </div>
    )
}

const fetchMock = (url: string) => {
    return new Promise((resolve) => {
        resolve(`Hello world ${url}`);
    })
}

const cached = new Map<string, Promise<string>>()

const fetchData = (url: string) => {
    if (cached.has(url)) {
        return cached.get(url)!;
    }
    const promise  = fetchMock(url) as Promise<string>;
    cached.set(url, promise);
    return promise;
}

const SuspenseData = () => {
    const data = use(fetchData('https://api.github.com/users/jianfehuang'))

    return (
        <h1>{data}</h1>
    )
}

export const SuspenseCacheDemo = () => {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <SuspenseData />
        </Suspense>
    )
}