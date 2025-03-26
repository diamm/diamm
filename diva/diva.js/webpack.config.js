const path = require('path');
const buildMode = (process.env.NODE_ENV === "production") ? 'production' : 'development';
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CopyPlugin = require("copy-webpack-plugin");


module.exports = [{
    entry: [
        // 'babel-polyfill',
        "array.prototype.fill",
        './source/js/diva.js',
        './source/css/diva.scss'
    ],
    module: {
        rules: [
            {
                test: /\.scss$/,
                use: [MiniCssExtractPlugin.loader, 'css-loader', 'sass-loader']
            }
        ]
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: path.join('diva.css')
        })
    ],
    output: {
        publicPath: '/build/',
        path: path.join(__dirname, 'build'),
        filename: 'diva.js',
        clean: true
    },
    mode: buildMode,
    devtool: (buildMode === "production") ? 'cheap-source-map' : 'cheap-module-source-map',
    devServer: {
        static: __dirname,
        compress: true,
        port: 9001
    }
}, {
    entry: {
        'download': './source/js/plugins/download.js',
        'manipulation': './source/js/plugins/manipulation.js',
        'metadata': './source/js/plugins/metadata.js',
        'simple-auth': './source/js/plugins/simple-auth.js',
        'service-worker': "./source/js/plugins/service-worker.js"
    },
    output: {
        publicPath: '/build/plugins/',
        path: path.join(__dirname, 'build', 'plugins'),
        filename: '[name].js',
        clean: true
    },
    plugins: [],
    mode: buildMode,
    devtool: (buildMode === "production") ? 'cheap-source-map' : 'cheap-module-source-map'
}];
