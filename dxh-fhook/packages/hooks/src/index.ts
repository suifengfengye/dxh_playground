export interface User {
  name: string
  age: number
}

import { Target, VERSION } from '@dxh-fhook/core'

import { add, heyi, multiply } from './math'

export default {
  add,
  multiply,
  heyi,
  VERSION,
  Target
}
