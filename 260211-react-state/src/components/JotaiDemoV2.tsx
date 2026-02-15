/**
 * jotail
 * 1. 每个组件都可以订阅一个或多个 atom
 * 2. 当 atom 的值发生变化时，所有订阅该 atom 的组件都会重新渲染
 * 常用函数：
 * useAtom: 用于订阅一个 atom，并返回 atom 的当前值和一个用于更新 atom 值的函数
 * useAtomValue: 用于订阅一个 atom，并返回 atom 的当前值
 * useSetAtom: 用于订阅一个 atom，并返回一个用于更新 atom 值的函数
 */
import {  useAtom } from 'jotai'
import { countAtom, nameAtom, userAtom } from '../store/jotaiV2'

export const CountComp = () => {
    const [count, setCount] = useAtom(countAtom)
    return (
        <div>
            <div>Count: {count}</div>
            <button onClick={() => setCount(count + 1)}>Add</button>
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
    const [userInfo, setUserInfo] = useAtom(userAtom)
    return (
        <div>
            <div>----------</div>
            <div>User Info: {JSON.stringify(userInfo)}</div>
            <button onClick={() => { setUserInfo({ count: userInfo.count + 1 }) }}>+1</button>
            <input value={userInfo.name} onChange={(e) => setUserInfo({ name: e.target.value })} />
        </div>
    )
}

export const JotaiDemoV2 = () => {
    return (
        <div>
            <CountComp />
            <NameComp />
            <UserComp />
        </div>
    )
}