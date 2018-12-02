const path = require('path');

module.exports = {
    entry: './src/example.js',
    output: {
        filename: 'example.js',
        path: path.resolve(__dirname, 'dist')
    },
    mode: 'development'
};
