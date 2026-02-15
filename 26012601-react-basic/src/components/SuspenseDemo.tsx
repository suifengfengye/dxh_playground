/**
 * Suspense:
 * 1. 按需/异步加载组件， + 结合 lazy()
 * 2. 缓存数据，+ 结合 use() hook
 * use()：让“异步数据获取”写在渲染期间，
 * （1）当异步数据未完成时，抛出suspend，此时Suspense捕获到就显示fallback
 * （2）当异步数据完成时，Suspense捕获到就显示子组件
 */

import React, { Suspense, use } from 'react';

// import { Child } from './Child';
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

const mockFetchData = async (url: string) => {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve(`Hello world ${url}`);
        }, 1000);
    })
}

const cached = new Map<string, Promise<string>>()

const fetchData = (url: string) => {
    if (cached.has(url)) {
        return cached.get(url)!;
    }
    const promise = mockFetchData(url).then((res) => res as string);
    cached.set(url, promise);
    console.log('cached', cached);
    return promise;
}

export const SuspenseCacheDemo = () => {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <SuspenseData />
        </Suspense>
    )
}

const SuspenseData = () => {
    const data = use(fetchData('https://api.github.com/users/jianfehuang'))
    return <h1>{data}</h1>
}
