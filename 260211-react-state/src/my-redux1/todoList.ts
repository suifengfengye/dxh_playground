
type Todo = {
    id: number
    name: string
}

type State = {
    todos: Todo[]
    nextId: number
}

type Action = { type: 'todo/add' }

const initialState: State = {
    todos: [
        {
            id: 1,
            name: 'Todo item 1.'
        },
    ],
    nextId: 2,
}

type Listener = () => void

let listeners: Listener[] = []
let state: State = initialState

const reducer = (currentState: State, action: Action): State => {
    switch (action.type) {
        case 'todo/add': {
            const id = currentState.nextId
            return {
                nextId: id + 1,
                todos: [
                    ...currentState.todos,
                    {
                        id,
                        name: `Todo item ${id}.`
                    },
                ],
            }
        }
        default:
            return currentState
    }
}

export const subscribe = (listener: Listener) => {
    listeners.push(listener)
    return () => {
        listeners = listeners.filter((item) => item != listener)
    }
}

export const dispatch = (action: Action) => {
    state = reducer(state, action)
    listeners.forEach((listener) => {
        listener()
    })
}

export const getSnapshot = () => {
    return state
}

export const addTodo = (): Action => ({ type: 'todo/add' })
