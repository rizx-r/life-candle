from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict

class Gender(str, Enum):
    MALE = 'Male'
    FEMALE = 'Female'

class UserInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: Optional[str] = None
    gender: Gender
    birthYear: Union[str, int]
    yearPillar: str
    monthPillar: str
    dayPillar: str
    hourPillar: str
    startAge: Union[str, int]
    firstSuperLuck: str = Field(alias='firstDaYun')
    modelName: Optional[str] = None
    apiBaseUrl: Optional[str] = None
    apiKey: Optional[str] = None

class KLinePoint(BaseModel):
    age: int
    year: int
    ganZhi: str
    superLuck: Optional[str] = None
    open: float
    close: float
    high: float
    low: float
    score: float
    reason: str

class AnalysisData(BaseModel):
    bazi: List[str]
    summary: str
    summaryScore: float
    personality: str
    personalityScore: float
    industry: str
    industryScore: float
    geomancy: str
    geomancyScore: float
    wealth: str
    wealthScore: float
    marriage: str
    marriageScore: float
    health: str
    healthScore: float
    family: str
    familyScore: float
    crypto: str
    cryptoScore: float
    cryptoYear: str
    cryptoStyle: str

class LifeDestinyResult(BaseModel):
    chartData: List[KLinePoint]
    analysis: AnalysisData
