import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export const counterSlice = createSlice({
    name: 'counter',
    initialState: {
        counter: 1,
    },
    reducers: {
        ADD: (state) => {
            // return {
            //     ...(state || {}),
            //     counter: state?.counter + 1,
            // }
            state.counter += 1
        },
        SUB: (state) => {
            // return {
            //     ...(state || {}),
            //     counter: state?.counter - 1,
            // }
            state.counter -= 1
        },
        incrementByAmount: (state, action: PayloadAction<number>) => {
            state.counter += action.payload
        }
    },
})

export const { ADD, SUB, incrementByAmount } = counterSlice.actions

// export const counterStore = configureStore({
//     reducer: counterSlice.reducer,
// })
