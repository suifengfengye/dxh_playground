import { configureStore } from '@reduxjs/toolkit'

import { counterSlice } from './counter'
import { infoSlice } from './info'

export const appStore = configureStore({
    reducer: {
        counter: counterSlice.reducer,
        info: infoSlice.reducer,
    },
})

export type RootState = ReturnType<typeof appStore.getState>
export type AppDispatch = typeof appStore.dispatch
export type AppStore = typeof appStore