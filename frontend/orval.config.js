module.exports = {
  caja: {
    input: '../openapi.json',
    output: {
      target: './src/api/generated.ts',
      client: 'react-query',
      mock: true
    },
  }
};