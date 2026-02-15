import { useReducer } from "react";

export const UseReducerDemoV3 = () => {
    const [state, dispatch] = useReducer((state, action) => {
        switch (action.type) {
            case 'changeName':
                return { ...state, name: action.payload };
            case 'addAge':
                return { ...state, age: state.age + 1 };
            case 'subAge':
                return { ...state, age: state.age - 1 };
            default:
                return state;
        }
    }, { name: 'xx', age: 18 })

    return (
        <div>
            <div>Name: {state.name}</div>
            <input type="text" value={state.name} onChange={(e) => dispatch({ type: 'changeName', payload: e.target.value }) } />
            <div>Age: {state.age}</div>
            <button type="button" onClick={() => dispatch({ type: 'addAge' })}>+</button>
            <button type="button" onClick={() => dispatch({ type: 'subAge' })}>-</button>
        </div>
    )
}