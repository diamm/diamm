var path = require('path');
var webpack = require('webpack');
const buildMode = process.env.NODE_ENV;

module.exports = {
    mode: buildMode,
    entry: [
        'babel-polyfill',
        'whatwg-fetch',
        './src/index.js'
    ],
    output: {
        path: path.join(__dirname, 'dist'),
        filename: 'bundle.js'
    },
    devtool: (buildMode === "production") ? "source-map" : "eval-source-map",
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
                    presets: ['react', 'stage-1']
                }
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
        new webpack.optimize.OccurrenceOrderPlugin(true),
        new webpack.ProvidePlugin({
            URLSearchParams: "url-search-params"
        }),
    ]
}

function developmentPlugins()
{
    return [
        new webpack.DefinePlugin({
            'process.env': {
                NODE_ENV: JSON.stringify(process.env.NODE_ENV)
            }
        }),
        new webpack.ProvidePlugin({
            URLSearchParams: "url-search-params"
        })
    ]
}
