import React from 'react'
import { Provider } from 'react-redux'
// import Counter from './components/Counter'
import CounterReact from './components/CounterReact'
import Info from './components/Info'

import { appStore } from './store'

const App = () => {
    return (
        <Provider store={appStore}>
            <div>
                <h1>APP</h1>
                {/* <Counter /> */}
                <CounterReact />
                <br />
                <Info />
            </div>
        </Provider>
    )
}

export default App