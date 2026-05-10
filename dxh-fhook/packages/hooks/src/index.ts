export interface User {
  name: string
  age: number
}

import { VERSION } from '@dxh-fhook/core'

import { add, heyi, multiply } from './math'

export default {
  add,
  multiply,
  heyi,
  VERSION
}
