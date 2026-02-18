import { useSyncExternalStore } from 'react'
import { subscribe, getSnapshot, addTodo, dispatch } from './todoList'

export const ReduxDemo1 = () => {
    const state = useSyncExternalStore(subscribe, getSnapshot)
    return (
        <div>
            <ul>
                {state.todos.map((todoItem) => {
                    return (
                        <li key={todoItem.id}>
                            <span>{todoItem.id}:</span>
                            <span>{todoItem.name}</span>
                        </li>
                    )
                })}
            </ul>
            <button onClick={() => dispatch(addTodo())}>添加</button>
        </div>
    )
}
export default ReduxDemo1
