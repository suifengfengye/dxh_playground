const http = require('http')

const server = http.createServer((req, res) => {
    res.writeHead(200, {"Content-Type": "application/json; charset=utf-8"});
    res.end(JSON.stringify({"success": true}))
})

const PORT = 3000;
server.listen(PORT, () => {
    console.log(`Server running at http://127.0.0.1:${PORT}`)
})