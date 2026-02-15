import { useReducer } from "react";

const reducer = (state: ({ name: string, age: number }), action: ({ type: 'changeName' | 'addAge' | 'subAge', payload: string | number })) => {
    switch (action.type) {
        case 'changeName':
            return {
                ...state,
                name: action.payload as string,
            }
        case 'addAge':
            return {
                ...state,
                age: state.age + (action.payload as number),
            }
        case 'subAge':
            return {
                ...state,
                age: state.age - (action.payload as number),
            }
        default:
            return state;
    }
}

const NameComp = ({ state, dispatch }: { state: { name: string }, dispatch: React.Dispatch<{ type: 'changeName', payload: string }> }) => {
    return (
        <div>
                <label>Name:{state.name}</label>
                <div></div>
                <input type="text" value={state.name}
                    onChange={(e) => dispatch({
                        type: 'changeName',
                        payload: e.target.value,
                    })} />
            </div>
    )
}

export const UseReducerDemo = () => {
    // const [name, setName] = React.useState('');
    // const [age, setAge] = React.useState(0);
    const [state, dispatch] = useReducer(reducer, {}, (initState) => ({
        ...initState,
        name: 'default name',
        age: 100,
    }));
    return (
        <div>
            <h2>UseReducerDemo</h2>
            <NameComp state={state} dispatch={dispatch} />
            <div>
                <label>Age:{state.age}</label>
                <div></div>
                {/* <input type="number" value={state.age} onChange={(e) => dispatch({
                    type: 'changeAge',
                    payload: Number(e.target.value),
                })} /> */}
                <button onClick={() => dispatch({
                    type: 'addAge',
                    payload: 1,
                })}>Add Age</button>
                <button onClick={() => dispatch({
                    type: 'subAge',
                    payload: 1,
                })}>Sub Age</button>
            </div>
        </div>
    );
}