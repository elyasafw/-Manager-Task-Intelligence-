from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from database.mission_db import missions_manager
from utils.services_validations import validation_difficulty_importance, calculate_risk_level
from logs.logger_config import logger


class NewMission(BaseModel):
    title : str
    description : str
    location : str
    difficulty : int
    importance : int


mission_router = APIRouter()


@mission_router.post("/missions")
def create_new_mission(new_mission: NewMission)
    mission = new_mission.model_dump()
    if not validation_difficulty_importance(new_mission):
       raise HTTPException(
           status_code=status.HTTP_400_BAD_REQUEST,
           detail="The 'difficulty' and 'importance' fields must be in the range of 1-10"
           )
    risk_level = calculate_risk_level(new_mission["difficulty"], new_mission["importance"])
    values = [
        new_mission["title"],
        new_mission["description"],
        new_mission["location"],
        new_mission["difficulty"],
        new_mission["importance"],
        risk_level
        ]
    is_create = missions_manager.create_mission(values)
    if not is_create:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Creating a new mission failed..."
            )
    return mission

@mission_router.get("/missions")
def get_all_missions():
    all_missions = missions_manager.get_all_missions()
    return all_missions

@mission_router.get("/missions/{id}")
def get_mission_by_id(id: int):
    mission = missions_manager.get_mission_by_id(id)
    return mission