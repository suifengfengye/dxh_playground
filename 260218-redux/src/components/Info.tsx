import React from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { changeInfo } from '../store/info'
import { RootState } from '../store'

const Info = () => {
    const infoState = useSelector((state: RootState) => state?.info)
    const dispatch = useDispatch()
    return (
        <div>
            Info
            <div>
                userName: {infoState?.userName}
            </div>
            <div>
                age: {infoState?.age}
            </div>
            <button onClick={() => dispatch(changeInfo())}>Change</button>
        </div>
    )
}

export default Info