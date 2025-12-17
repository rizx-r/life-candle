import axios from 'axios';
import type { UserInput, LifeDestinyResult } from './types';

const api = axios.create({
  baseURL: 'http://localhost:8000/api', // Point to Python Backend
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeDestiny = async (input: UserInput): Promise<LifeDestinyResult> => {
  const response = await api.post<LifeDestinyResult>('/analyze', input);
  return response.data;
};
