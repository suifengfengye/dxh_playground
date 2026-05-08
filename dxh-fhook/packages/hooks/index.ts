export interface User {
  name: string
  age: number
}

import path from 'path-browserify'

import { add } from './math'
import { multiply } from './math'

const href = window.location.href

const a = href

console.log('hooks')
