import { createWithEqualityFn } from "zustand/traditional"
import { shallow } from "zustand/shallow"

type InfoStore = {
    count: number
    name: string
    increment: () => void
    decrement: () => void
    changeName: (name: string) => void
}

const useInfoStore = createWithEqualityFn<InfoStore>((set) => {
    return {
        count: 0,
        name: 'dxh',
        increment: () => set((state) => ({ count: state.count + 1 })),
        decrement: () => set((state) => ({ count: state.count - 1 })),
        changeName: (name: string) => set({ name }),
    }
})
export const CountComp = () => {
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

export const NameComp = () => {
    const { name, changeName } = useInfoStore((state) => ({
        name: state.name,
        changeName: state.changeName,
    }), shallow)
    return (
        <div>
            <div>name: {name}</div>
            <input value={name} onChange={(e) => changeName(e.target.value)} />
        </div>
    )
}


export const ZustandDemoV3 = () => {
    return (
        <div>
            <CountComp />
            <NameComp />
        </div>
    )
}