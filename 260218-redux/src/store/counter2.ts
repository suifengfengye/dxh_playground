import { createStore } from 'redux'

const counterReducer = (state = { counter: 0 }, action: ({ type: string })) => {
    switch (action.type) {
        case 'ADD':
            return {
                ...state,
                counter: state.counter +  1,
            }
        case 'SUB':
            return {
                ...state,
                counter: state.counter - 1,
            }
        default:
            return state
    }
}

export const counterStore = createStore(counterReducer)