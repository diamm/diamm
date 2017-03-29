var path = require('path');
var webpack = require('webpack');

module.exports = {
    entry: [
        'babel-polyfill',
        'whatwg-fetch',
        './src/index.js'
    ],
    output: {
        filename: "./dist/bundle.js",
    },
    devtool: (process.env.NODE_ENV === "production") ? "source-map" : "eval-source-map",
    resolve: {
        extensions: [".js", ".jsx"],
    },
    module: {
        loaders: [
            {
                test: /\.json$/,
                loaders: ['json']
            },
            {
                loader: "babel",
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
                NODE_ENV: JSON.stringify('production')
            }
        }),
        new webpack.ProvidePlugin({
            URLSearchParams: "url-search-params"
        }),
        new webpack.optimize.UglifyJsPlugin(),
        new webpack.optimize.OccurrenceOrderPlugin(true),
    ]
}

function developmentPlugins()
{
    return [
        new webpack.ProvidePlugin({
            URLSearchParams: "url-search-params"
        })
    ]
}
