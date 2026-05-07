
// 1. 防抖
const debounce = (fn, delay = 500) => {
    let timer = null
    return function (...args) {
        if (timer) {
            clearTimeout(timer)
        }
        timer = setTimeout(() => {
            // fn(...args)
            fn.apply(this, args)
            timer = null
        }, delay)
    }
}
// 只执行一次
const d = debounce((i) => console.log('debounce', i, Date.now()), 200)
// 2. 截流
const throttle = (fn, delay = 50) => {
    let timer = null
    return function (...args) {
        if (timer) {
            return
        }
        timer = setTimeout(() => {
            // fn(...args)
            fn.call(this, ...args)
            timer = null
        }, delay)
    }
}
// 输出多次
const t = throttle((i) => console.log('throttle', i, Date.now()), 200)