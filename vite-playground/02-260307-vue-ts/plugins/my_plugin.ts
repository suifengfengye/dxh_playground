
const my_plugin = () => {
    return {
        name: "my_plugin",
        transform: (src: string) => {
            // console.log('@@@@my_plugin----', src)
            if (!src || typeof src !== 'string') {
                return src
            }
            return src.replace(':smile:', '😊')
        }
    }
}

export default my_plugin