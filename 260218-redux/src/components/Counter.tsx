import React, { useReducer, useSyncExternalStore } from 'react'
// import { counterStore, ADD, SUB } from '../store/counter'
import { counterStore } from '../store/counter2'

const Counter = () => {
    // const [counter, setCounter] = useState(0)
    // const [state, dispatch] = useReducer((prevState, action) => {
    //     switch(action.type) {
    //         case 'ADD':
    //             return {
    //                 ...prevState,
    //                 counter: prevState.counter + 1,
    //             }
    //         case 'SUB':
    //             return {
    //                 ...prevState,
    //                 counter: prevState.counter - 1,
    //             }
    //         default:
    //             return prevState
    //     }
    // }, { counter: 0 })
    // const state = counterStore.getState()
    const state = useSyncExternalStore(counterStore.subscribe, () => {
        return counterStore.getState()
    })
    return (
        <div>
            Counter: {state?.counter}
            {/* <div>
                <button onClick={() => counterStore.dispatch(ADD())}>+</button>
                <button onClick={() => counterStore.dispatch(SUB())}>-</button>
            </div> */}
            <div>
                <button onClick={() => counterStore.dispatch({ type: 'ADD' })}>+</button>
                <button onClick={() => counterStore.dispatch({ type: 'SUB' })}>-</button>
            </div>
            <div>
                <button onClick={() => { state.counter += 10 }}>add</button>
            </div>
        </div>
    )
}
export default Counter