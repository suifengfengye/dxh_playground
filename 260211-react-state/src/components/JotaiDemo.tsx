
/**
 * Jotai 自底向上的设计状态库
 * 1. 每个状态都是一个 atom，每个 atom 都有一个唯一的 id
 * 2. 每个组件都可以订阅一个或多个 atom
 * 3. 当 atom 的值发生变化时，所有订阅该 atom 的组件都会重新渲染
 */

import { useAtom, useAtomValue, useSetAtom } from 'jotai'
import { countAtom, nameAtom, userValueAtom } from '../store/jotai'

export const CountComp = () => {
    const [count, setCount] = useAtom(countAtom)
    return (
        <div>
            <div>Count: {count}</div>
            <button onClick={() => setCount(count + 1)}>Add</button>
            <button onClick={() => setCount(count - 1)}>Subtract</button>
        </div>
    )
}

export const NameComp = () => {
    const [name, setName] = useAtom(nameAtom)
    return (
        <div>
            <div>Name: {name}</div>
            <input value={name} onChange={(e) => setName(e.target.value)} />
        </div>
    )
}

export const UserComp = () => {
    const user = useAtomValue(userValueAtom)
    const setUser = useSetAtom(userValueAtom)
    return (
        <div>
            <div>User: {user.name}</div>
            <input value={user.name} onChange={(e) => setUser({ name: e.target.value })} />
            <div>Count: {user.count}</div>
            <button onClick={() => setUser({ count: user.count + 1 })}>Add Count</button>
            <button onClick={() => setUser({ count: user.count - 1 })}>Subtract Count</button>
        </div>
    )
}

export const JotaiDemo = () => {
    return (
        <div>
            <CountComp />
            <NameComp />
            <UserComp />
        </div>
    )
}
