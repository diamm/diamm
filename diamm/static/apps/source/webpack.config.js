var path = require('path');
var webpack = require('webpack');
var sharedJQueryPath = require.resolve('jquery');

module.exports = {
    entry: [
        'babel-polyfill',
        'whatwg-fetch',
        './src/index.js'
    ],
    output: {
        filename: "./dist/bundle.js",
    },
    devtool: (process.env.NODE_ENV === "production") ? "cheap-module-source-map" : "eval-source-map",
    resolve: {
        extensions: [".js", ".jsx"],
        alias: {
            // We need all usages of jQuery to resolve to the same library
            // not only becuase bundling duplicates would be bad (that could
            // be optimized later), but because Diva injects its public code
            // in one of them
            jquery: sharedJQueryPath
        }
    },
    module: {
        loaders: [
            {
                test: /\.json$/,
                loaders: ['json-loader']
            },
            {
                loader: "babel-loader",
                include: [
                    path.resolve(__dirname, "src")
                ],
                query: {
                    presets: ["react", "es2015", "stage-1"],
                }
            }
        ]
    },
    plugins: (process.env.NODE_ENV === "production") ? productionPlugins() : developmentPlugins()
};


function productionPlugins()
{
    return [
        new webpack.DefinePlugin({
            'process.env': {
                NODE_ENV: JSON.stringify(process.env.NODE_ENV)
            }
        }),
        new webpack.optimize.UglifyJsPlugin(),
        new webpack.optimize.OccurrenceOrderPlugin(true),
        new webpack.ProvidePlugin({
            'diva': 'diva',
            '$': sharedJQueryPath,
            'jQuery': sharedJQueryPath,
            'window.jQuery': sharedJQueryPath,
            URLSearchParams: "url-search-params"
        })
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
            'diva': 'diva',
            '$': sharedJQueryPath,
            'jQuery': sharedJQueryPath,
            'window.jQuery': sharedJQueryPath,
            URLSearchParams: "url-search-params"
        })
    ]
}
