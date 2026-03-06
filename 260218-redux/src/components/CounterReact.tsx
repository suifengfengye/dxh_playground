import React, { useReducer, useSyncExternalStore } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { ADD, SUB, incrementByAmount } from '../store/counter'
import { RootState } from '../store'

const Counter = () => {
    const dispatch = useDispatch()
    const counterState = useSelector((state: RootState) => {
        return state?.counter
    })

    return (
        <div>
            Counter: {counterState?.counter}
            {/* <div>
                <button onClick={() => counterStore.dispatch(ADD())}>+</button>
                <button onClick={() => counterStore.dispatch(SUB())}>-</button>
            </div> */}
            <div>
                <button onClick={() => dispatch(ADD())}>+</button>
                <button onClick={() => dispatch(SUB())}>-</button>
                <button onClick={() => dispatch(incrementByAmount(10))}>+10</button>
            </div>
        </div>
    )
}
export default Counter