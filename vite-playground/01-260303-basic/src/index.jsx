// import { createApp, ref } from 'vue'
// import App from './App.vue'

// // const app = createApp({
// //     setup() {
// //         const message = ref('Hello Vue')
// //         return {
// //             message,
// //         }
// //     },
// //     template: `<div>message: {{ message }}</div>`,
// // })
// const app = createApp(App)

// app.mount('#app')

import { createRoot } from 'react-dom/client'
import App from './App.jsx'

const root = createRoot(document.getElementById('app'))

root.render(<App />)