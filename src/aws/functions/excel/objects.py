from pydantic import BaseModel
from typing import Dict, Optional

class EntityDetails(BaseModel):
    user_id: int
    sex_id: Optional[int]
    age: Optional[int]
    velocity: float
    colission_point_distance: float
    tc_value: float
    evasion_id: int
    evasion_possibility_id: int


class SmallEntityDetails(BaseModel):
    user_id: int
    sex_id: int
    age: int
    speed: float
 
 
class Event(BaseModel):
    video_name: str
    video_section: str = ""
    video_minute: int
    event_hour: str
    event_description: str
    entity1: EntityDetails
    entity2: EntityDetails
    entity3: SmallEntityDetails = None
    
class HeaderData(BaseModel):
    id: str
    city: str
    intersection: str 
    date: str 
    time_start: str
    time_end: str
    observer: str = ""
    weather: str = None
    sunny: bool = False
    dry: bool = False
    cloudy: bool = False
    humid: bool = False
    surface: str = None
    raining: bool = False
    