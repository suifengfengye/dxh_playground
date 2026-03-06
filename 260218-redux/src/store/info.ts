import { createSlice } from '@reduxjs/toolkit'

export const infoSlice = createSlice({
    name: 'info',
    initialState: {
        userName: 'DXH',
        age: -1,
    },
    reducers: {
        changeInfo: (state) => {
            state.age = Math.floor(Math.random() * 100)
            state.userName = `大小寒学AI_${new Date().getTime()}`
        }
    }
})

export const { changeInfo } = infoSlice.actions