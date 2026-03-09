import { createApp } from 'vue'
import App from '@/App.vue'
const utils = require('./utils')

console.log('@@@utils', utils)

const app = createApp(App)

app.mount('#app')

export default app