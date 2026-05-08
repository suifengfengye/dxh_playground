import { createApp } from 'vue';

import App from './App.vue';

const verion = 1.0;

const app = createApp(App);

console.log('@@@app')

app.mount('#app');