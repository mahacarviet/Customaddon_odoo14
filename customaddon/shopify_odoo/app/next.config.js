require("dotenv").config();
const withCSS = require('@zeit/next-css');
const webpack = require('webpack');

module.exports = withCSS({
    webpack: (config, {isServer}) => {
        if (!isServer) {
            config.node = {
                fs: 'empty'
            }
        }
        config.module.rules.push({
            test: /\.(eot|woff|woff2|ttf|svg|png|jpg|gif)$/,
            use: {
                loader: 'url-loader',
                options: {
                    limit: 100000,
                    name: '[name].[ext]'
                }
            }
        })
        config.module.rules.push({
            test: /\.txt$/,
            use: 'raw-loader'
        })
        return config;
    },
});

