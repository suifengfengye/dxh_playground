import { createApp, ref } from 'vue'

const app = createApp({
    setup() {
        const message = ref('Hello Vue')
        return {
            message,
        }
    },
    template: `<div>message: {{ message }}</div>`,
})

app.mount('#app')
