<script setup>
import { ref } from 'vue'
const count = ref(0)
</script>

<template>
<div>
    <h1>Hello Vue2</h1>
    count: {{ count }}
    <div>
        <button @click="count += 1">+</button>
        <button @click="count -= 1">-</button>
    </div>
</div>
</template>