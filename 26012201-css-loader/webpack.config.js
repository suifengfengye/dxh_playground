module.exports = {
    entry: './src/index.js',
    output: {
        path: __dirname + '/dist',
        filename: 'main.[contenthash].js',
        clean: true,
    },
    mode: "production",
    module: {
        rules: [
            {
                test: /\.css$/,
                use: ['css-loader']
            }
        ]
    }
}