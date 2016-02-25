var path = require("path");
var webpack = require("webpack");

module.exports = {
    entry: [
        "babel-polyfill",
        "./src/main"
    ],
    output: {
        filename: "bundle.js",
        path: './dist'
    },
    devtool: "source-map",
    module: {
        loaders: [
            {
                loader: "babel-loader",
                include: [
                    path.resolve(__dirname, "src")
                ],
                test: /\.js?$/,
                query: {
                    plugins: ['transform-runtime'],
                    presets: ['es2015', 'stage-0']
                }
            }
        ]
    }
};
