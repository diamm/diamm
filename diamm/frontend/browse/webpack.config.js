module.exports =
{
    entry: './src/app.js',
    output:
    {
        path: '../../static/javascripts/dist',
        filename: 'browse.bundle.js'
    },
    module: {
        loaders: [
            {
                test: /\.jsx?$/,
                loader: 'babel',
                query: {
                    presets: ['react', 'es2015']
                }
            }
        ]
    }
}
