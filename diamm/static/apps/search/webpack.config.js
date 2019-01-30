var path = require('path');
var webpack = require('webpack');
const buildMode = process.env.NODE_ENV ? process.env.NODE_ENV : "development";

module.exports = {
    mode: buildMode,
    entry: [
        '@babel/polyfill',
        "@ungap/url-search-params",
        'whatwg-fetch',
        './src/index.js'
    ],
    output: {
        path: path.join(__dirname, 'dist'),
        filename: 'bundle.js'
    },
    devtool: (buildMode === "production") ? 'cheap-source-map' : 'cheap-module-eval-source-map',
    resolve: {
        extensions: [".js", ".jsx"],
    },
    optimization: {
        minimize: (buildMode === "production"),
    },
    module: {
        rules: [{
            test: /\.js$/,
            exclude: /node_modules/,
            use: {
                loader: "babel-loader",
                options: {
                    presets: ['@babel/react'],
                    plugins: [
                        "@babel/plugin-proposal-class-properties"
                    ]
                },
            }
        }]
    },
    plugins: (buildMode === "production") ? productionPlugins() : developmentPlugins()
};


function productionPlugins()
{
    return [
        new webpack.DefinePlugin({
            'process.env': {
                NODE_ENV: JSON.stringify(process.env.NODE_ENV)
            }
        }),
        new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
        new webpack.optimize.OccurrenceOrderPlugin(true)
    ]
}

function developmentPlugins()
{
    return [
        new webpack.DefinePlugin({
            'process.env': {
                NODE_ENV: JSON.stringify(process.env.NODE_ENV)
            }
        })
    ]
}
