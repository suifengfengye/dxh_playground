<script setup>
import { ref, onMounted } from 'vue'
const count = ref(0)

onMounted(() => {
    fetch("/api/hello").then(async (res) => {
        const data = await res.json()
        console.log(data)
        // const reader = res.body?.getReader()
        // if (!reader) return

        // const decoder = new TextDecoder('utf-8')
        // let result = ''

        // while (true) {
        //     const { value, done } = await reader.read()
        //     if (done) break
        //     result += decoder.decode(value, { stream: true })
        // }
        // result += decoder.decode()
        // console.log(result)
    })
})

</script>

<template>
<div>
    <h1>Hello Vue3-:smile:</h1>
    count: {{ count }}
    <div>
        <button @click="count += 1">+</button>
        <button @click="count -= 1">-</button>
    </div>
</div>
</template>