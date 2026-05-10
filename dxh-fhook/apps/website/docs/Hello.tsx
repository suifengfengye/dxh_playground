import { useVersion } from '@dxh-fhook/hooks'
import React, { useState } from 'react'

export default function Hello() {
  const version = useVersion()
  const [count, setCount] = useState(0)
  return (
    <h1 style={{ color: 'red' }}>
      <div>Hello dxh-fhooks, version:{version}</div>
      <div>
        count: {count}
        <div>
          <button onClick={() => setCount(count + 1)}>+</button>
          <span style={{ display: 'inline-block', marginLeft: '4px' }}></span>
          <button onClick={() => setCount(count - 1)}>-</button>
        </div>
      </div>
    </h1>
  )
}
