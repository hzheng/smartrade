const resolve = require('path').resolve;
const env = process.env.NODE_ENV || 'development';
const isDev = env != 'production';

const config = {
  mode: env,
  devtool: isDev ? 'source-map' : false,
  entry: './jsx/index.js',
  output: {
    pathinfo: isDev,
    filename: 'bundle.js',
    path: resolve(__dirname, 'generated'),
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        include: [
          resolve(__dirname, 'jsx')
        ],
        use: ['babel-loader'],
      },
      {
        test: /\.s?css$/,
        use: [
          'style-loader',
          'css-loader',
          'sass-loader'
        ]
      },
      {
        test: /\.(jpe?g|svg|png|gif|ico|eot|ttf|woff2?)(\?v=\d+\.\d+\.\d+)?$/i,
        type: 'asset/resource',
      },
    ]
  }
};

module.exports = config;