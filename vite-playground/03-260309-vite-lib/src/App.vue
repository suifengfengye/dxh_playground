<script setup>
import { ref } from 'vue'

const count = ref(0)

</script>
<template>
<div>
Hello Vue
<div>
    count: {{ count }}
    <div>
        <button type="button" @click="count += 1">+</button>
        <button type="button" @click="count -= 1">-</button>
    </div>
</div>
</div>
</template>