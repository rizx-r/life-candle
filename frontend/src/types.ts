export type Gender = 'Male' | 'Female';
export const Gender = {
  MALE: 'Male' as Gender,
  FEMALE: 'Female' as Gender,
};

export interface UserInput {
  name?: string;
  gender: Gender;
  birthYear: string | number;
  yearPillar: string;
  monthPillar: string;
  dayPillar: string;
  hourPillar: string;
  startAge: string | number;
  firstSuperLuck: string;
  
  // API Configuration (Optional)
  modelName?: string;
  apiBaseUrl?: string;
  apiKey?: string;
}

export interface KLinePoint {
  age: number;
  year: number;
  ganZhi: string;
  superLuck?: string;
  open: number;
  close: number;
  high: number;
  low: number;
  score: number;
  reason: string;
}

export interface AnalysisData {
  bazi: string[];
  summary: string;
  summaryScore: number;
  
  personality: string;
  personalityScore: number;
  
  industry: string;
  industryScore: number;

  geomancy: string;
  geomancyScore: number;
  
  wealth: string;
  wealthScore: number;
  
  marriage: string;
  marriageScore: number;
  
  health: string;
  healthScore: number;
  
  family: string;
  familyScore: number;

  crypto: string;
  cryptoScore: number;
  cryptoYear: string;
  cryptoStyle: string;
}

export interface LifeDestinyResult {
  chartData: KLinePoint[];
  analysis: AnalysisData;
}
