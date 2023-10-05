const webpack = require('webpack');
const path = require('path');
const NodePolyfillPlugin = require('node-polyfill-webpack-plugin');

const config = {
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js'
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        use: 'babel-loader',
        exclude: /node_modules/
      },
      {
        test: /\.scss$/,
        use: [
          'style-loader',
          'css-loader',
          'sass-loader'
        ]
      }
    ]
  },
//  resolve: {
//    fallback: {
//      stream: false,
//    },
//  },
  plugins: [
    //new NodePolyfillPlugin({ excludeAliases: ['stream'] })
    new NodePolyfillPlugin()
  ]
};

module.exports = config;
