import { useAtom, useSetAtom, useAtomValue } from 'jotai'
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
    const name = useAtomValue(nameAtom)
    const setName = useSetAtom(nameAtom)
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

export const JotaiDemoV3 = () => {
    return (
        <div>
            <CountComp />
            <NameComp />
            <UserComp />
        </div>
    )
}