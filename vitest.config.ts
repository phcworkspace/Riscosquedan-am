import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node', // engine/ é TypeScript puro, sem DOM
    include: ['src/**/*.test.ts'],
  },
});
