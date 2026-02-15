/**
 * zustand按照细粒度的订阅方式，可以减少不必要的渲染
 */

// import { create } from 'zustand'
import { shallow } from 'zustand/shallow';
import { createWithEqualityFn } from 'zustand/traditional'

interface InfoStoreType {
    count: number;
    increment: () => void;
    decrement: () => void;
    name: string;
    changeName: (name: string) => void;
}

const useInfoStore = createWithEqualityFn<InfoStoreType>((set) => {
    return {
        count: 0,
        increment: () => set((state) => ({ count: (state?.count ?? 0) + 1 })),
        decrement: () => {
            return set((state) => {
                return {
                    count: (state?.count ?? 0) - 1
                }
            })
        },
        name: 'dxh',
        changeName: (name: string) => set({ name }),
    }
})

const CountComp = () => {
    // const count = useInfoStore((state) => state.count);
    // const increment = useInfoStore((state) => state.increment);
    // const decrement = useInfoStore((state) => state.decrement);
    const { count, increment, decrement } = useInfoStore((state) => ({
        count: state.count,
        increment: state.increment,
        decrement: state.decrement,
    }), shallow)
    return (
        <div>
            <div>Count: {count}</div>
            <button onClick={increment}>+</button>
            <button onClick={decrement}>-</button>
        </div>
    )
}

const NameComp = () => {
    // const name = useInfoStore((state) => state.name)
    // const changeName = useInfoStore((state) => state.changeName)
    const { name, changeName } = useInfoStore((state) => ({
        name: state.name,
        changeName: state.changeName,
    }), shallow)
    return (
        <div>
            <div>Name: {name}</div>
            <input value={name} onChange={(e) => changeName(e.target.value)} />
        </div>
    )
}

export const ZustandDemoV2 = () => {
    return (
        <div>
            <CountComp />
            <NameComp />
        </div>
    )
}