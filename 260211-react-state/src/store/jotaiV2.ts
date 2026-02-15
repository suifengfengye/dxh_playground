import { atom } from 'jotai'

export const countAtom = atom(0)
export const nameAtom = atom('dxh')

type UserValue = {
    count: number
    name: string
}

export const userAtom = atom((get) => {
    return {
        count: get(countAtom),
        name: get(nameAtom),
    }
}, (get, set, next: Partial<UserValue>) => {
    if (typeof next.count === 'number') {
        set(countAtom, next.count)
    }
    if (typeof next.name === 'string') {
        set(nameAtom, next.name)
    }
})