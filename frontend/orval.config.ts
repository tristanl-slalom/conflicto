import { defineConfig } from 'orval';

export default defineConfig({
  caja: {
    input: './openapi.json',
    output: {
      target: './src/api/generated.ts',
      client: 'react-query',
      mock: true,
      httpClient: 'fetch',
      override: {
        mutator: {
          path: './src/api/mutator.ts',
          name: 'customFetcher'
        }
      }
    },
  }
});
