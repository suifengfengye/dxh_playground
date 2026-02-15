import { createWithEqualityFn } from 'zustand/traditional'
import { shallow } from 'zustand/shallow'
// 需要安装 use-sync-external-store 库
type InfoStoreType = {
    count: number,
    increment: () => void
    decrement: () => void
    name: string,
    changeName: (name: string) => void
}

const useInfoStore = createWithEqualityFn<InfoStoreType>((set) => ({
    count: 0,
    increment: () => set((state) => ({ count: (state?.count ?? 0) + 1 })),
    decrement: () => set((state) => ({ count: (state?.count ?? 0) - 1 })),
    name: '',
    changeName: (name: string) => set({ name }),
}))

const CountComp = () => {
    const { count, increment, decrement } = useInfoStore((state) => ({
        count: state.count,
        increment: state.increment,
        decrement: state.decrement,
    }), shallow);
    return (
        <div>
            <div>Count: {count}</div>
            <button onClick={increment}>+</button>
            <button onClick={decrement}>-</button>
        </div>
    )
}

const NameComp = () => {
    const { name, changeName } = useInfoStore((state) => ({
        name: state.name,
        changeName: state.changeName,
    }), shallow);
    return (
        <div>
            <div>Name: {name}</div>
            <input type="text" value={name} onChange={(e) => changeName(e.target.value)} />
        </div>
    )
}

export const ZustandDemo = () => {
    return (
        <div>
            <CountComp />
            <NameComp />
        </div>
    )
}
