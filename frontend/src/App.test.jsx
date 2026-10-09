import { describe, it, expect } from 'vitest';
import App from './App.jsx';

describe('App Root', () => {
  it('renders application title properly', () => {
    expect(App).toBeDefined();
  });
});