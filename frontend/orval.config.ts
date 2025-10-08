import { defineConfig } from 'orval';

export default defineConfig({
  caja: {
    input: './openapi.json',
    output: {
      target: './src/api/generated.ts',
      client: 'react-query',
      mock: true,
      httpClient: 'fetch',
      baseUrl: 'http://localhost:8000'
    },
  }
});
