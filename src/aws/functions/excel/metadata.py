from pydantic import BaseModel
from typing import Dict


class Cell(BaseModel):
    row: int
    col: int


class ColPosition(BaseModel):
    col: int


class Metadata(BaseModel):
    info: Dict[str, Cell]


cell_locations = {
    "observer": Cell(row=2, col=6),
    "city": Cell(row=3, col=6),
    "intersection": Cell(row=4, col=6),
    # "weather": Cell(row=5, col=6),
    "sunny": Cell(row=5, col=6),
    "dry": Cell(row=6, col=6),
    "cloudy": Cell(row=5, col=12),
    "humid": Cell(row=6, col=12),
    # "surface": Cell(row=6, col=6),
    "raining": Cell(row=5, col=20),
    "date": Cell(row=2, col=24),
    "time_start": Cell(row=3, col=24),
    "time_end": Cell(row=4, col=24),
    "id": Cell(row=-1, col=-1), # ignore id
}

header_metadata = Metadata(info=cell_locations)

entity_column_offset = {
    "user_id": 0,
    "sex_id": 1,
    "age": 2,
    "velocity": 3,
    "colission_point_distance": 4,
    "tc_value": 5,
    "evasion_id": 6,
    "evasion_possibility_id": 7  
}

event_details_offset = {
    "video_name": 1,
    "video_section": 2,
    "video_minute": 3,
    "event_hour": 4,
    "entity1": 5,
    "entity2": 13,
    "entity3": 21,
    "event_description": 25,
}

def validate_metadata(info: dict, metadata: Metadata):
    for key in info.keys():
        if info[key] is not None and key not in metadata.info:
            raise Exception(f"Metadata for {key} not found.")
        
def validate_offsets(info: dict, offsets: dict):
    for key in info.keys():
        if info[key] is not None and key not in offsets:
            raise Exception(f"Key {key} not found in offset.")