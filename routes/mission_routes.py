from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from database.mission_db import missions_manager
from database.agent_db import agents_manager
from utils.services_validations import validation_difficulty_importance, calculate_risk_level, check_assign_rules, check_status_rules
from logs.logger_config import logger


class NewMission(BaseModel):
    title : str
    description : str
    location : str
    difficulty : int
    importance : int


mission_router = APIRouter()


@mission_router.post("/missions", status_code=status.HTTP_201_CREATED)
def create_new_mission(new_mission: NewMission):
    mission = new_mission.model_dump()
    if not validation_difficulty_importance(new_mission):
       logger.error("Mission not create: invalid value in 'difficulty' or 'importance' fields")
       raise HTTPException(
           status_code=status.HTTP_400_BAD_REQUEST,
           detail="The 'difficulty' and 'importance' fields must be in the range of 1-10"
           )
    risk_level = calculate_risk_level(new_mission["difficulty"], new_mission["importance"])
    values = [
        mission["title"],
        mission["description"],
        mission["location"],
        mission["difficulty"],
        mission["importance"],
        risk_level
        ]
    is_create = missions_manager.create_mission(values)
    if not is_create:
        logger.error("Creating a new mission failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Creating a new mission failed..."
            )
    logger.info("New mission created successfully")
    return mission

@mission_router.get("/missions")
def get_all_missions():
    all_missions = missions_manager.get_all_missions()
    logger.info("Getting list of all missions")
    return all_missions

@mission_router.get("/missions/{id}")
def get_mission_by_id(id: int):
    mission = missions_manager.get_mission_by_id(id)
    if not mission:
        logger.error(f"Mission ID {id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission ID {id} not found"
            )
    logger.info(f"Getting details of mission ID: {id}")
    return mission

@mission_router.put("/missions/{id}/start")
def start_mission(id: int, m_status: str):
    if m_status.upper()  != "IN_PROGRESS":
        logger.error("Mission start status must be: 'IN_PROGRESS'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mission start status must be: 'IN_PROGRESS'"
            )
    mission = missions_manager.get_mission_by_id(id)
    if not mission:
        logger.error(f"Mission ID: {id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission ID: {id} not found"
            )
    check_rules = check_status_rules(m_status, mission, id)
    if check_rules != "OK":
        logger.error(f"error: {check_rules}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{check_rules}"
            )
    start_update = missions_manager.update_mission_status(id, m_status)
    if not start_update:
        logger.error(f"Change mission Status ID: {id} failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Change mission Status ID: {id} failed"
            )
    logger.info(f"Mission Status ID: {id} Updated 'IN_PROGRESS'")
    return {"message": f"Mission Status ID: {id} Updated 'IN_PROGRESS' Successfully"}

@mission_router.put("/missions/{id}/complete")
def complete_mission(agent_id:int, id: int, m_status: str):
    if m_status.upper() != "COMPLETED":
        logger.error("Mission complete status must be: 'COMPLETED'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mission complete status must be: 'COMPLETED'"
            )
    mission = missions_manager.get_mission_by_id(id)
    if not mission:
        logger.error(f"Mission ID: {id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission ID: {id} not found"
            )
    check_rules = check_status_rules(m_status, mission, id)
    if not check_rules == "OK":
        logger.error(f"error: {check_rules}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{check_rules}"
            )
    agent = agents_manager.get_agent_by_id(agent_id)
    if not agent:
        logger.error(f"Agent ID: {agent_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= f"Agent ID: {agent_id} not found"
            )
    complete_agent_missions = agents_manager.increment_completed(agent_id)
    complete_update = missions_manager.update_mission_status(id, m_status)
    if not complete_update or not complete_agent_missions:
        logger.error(f"Change mission Status ID: {id} failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Change mission Status ID: {id} failed"
            )
    logger.info(f"Mission Status ID: {id} Updated 'COMPLETED'")
    return {"message": f"Mission Status ID: {id} Updated 'COMPLETED' Successfully"}

@mission_router.put("/missions/{id}/fail")
def fail_mission(agent_id:int, id: int, m_status: str):
    if m_status.upper() != "FAILED":
        logger.error(f"Mission fail status must be: 'FAILED'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mission fail status must be: 'FAILED'"
            )
    mission = missions_manager.get_mission_by_id(id)
    if not mission:
        logger.error(f"Mission ID: {id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission ID: {id} not found"
            )
    check_rules = check_status_rules(m_status, mission, id)
    if not check_rules == "OK":
        logger.error(f"error: {check_rules}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{check_rules}"
            )
    agent = agents_manager.get_agent_by_id(agent_id)
    if not agent:
        logger.error(f"Agent ID: {agent_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= f"Agent ID: {agent_id} not found"
            )
    fail_agent_missions = agents_manager.increment_failed(agent_id)
    fail_update = missions_manager.update_mission_status(id, m_status)
    if not fail_update or not fail_agent_missions:
        logger.error(f"Change mission Status ID: {id} failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Change mission Status ID: {id} failed"
            )
    logger.info(f"Mission Status ID: {id} Updated 'FAILED'")
    return {"message": f"Mission Status ID: {id} Updated 'FAILED' Successfully"}

@mission_router.put("/missions/{id}/cancel")
def cancel_mission(id: int, m_status: str):
    if m_status.upper()  != "CANCELLED":
        logger.error("Mission cancel status must be: 'CANCELLED'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mission cancel status must be: 'CANCELLED'"
            )
    mission = missions_manager.get_mission_by_id(id)
    if not mission:
        logger.error(f"Mission ID: {id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission ID: {id} not found"
            )
    check_rules = check_status_rules(m_status, mission, id)
    if not check_rules == "OK":
        logger.error(f"Canceled mission failed: {check_rules}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=check_rules
            )
    cancel_update = missions_manager.update_mission_status(id, m_status)
    if not cancel_update:
        logger.error(f"Change mission Status ID: {id} failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Change mission Status ID: {id} failed"
            )
    logger.info(f"Mission Status ID: {id} Updated 'CANCELLED'")
    return {"message": f"Mission Status ID: {id} Updated 'CANCELLED' Successfully"}

@mission_router.put("/missions/{id}/assign/{agent_id}")
def assign_mission_to_agent(id: int, agent_id: int):
    agent = agents_manager.get_agent_by_id(agent_id)
    if not agent:
        logger.error(f"Agent ID: {agent_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent ID: {agent_id} not found"
            )
    mission = missions_manager.get_mission_by_id(id)
    if not mission:
        logger.error(f"Mission ID: {id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission ID: {id} not found"
            )
    open_missions = missions_manager.get_open_missions_by_agent(agent_id)
    check_rules = check_assign_rules(mission, agent, open_missions)
    if check_rules != "OK":
        logger.error(f"Assign rules failed: {check_rules}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=check_rules
            )
    is_assign = missions_manager.assign_mission(id, agent_id)
    if not is_assign:
        logger.error(f"Assignment failed: mission {id}, agent {agent_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Assignment of mission ID: {id} to agent ID: {agent_id} failed"
            )
    logger.info(f"Mission ID: {id} successfully assigned to Agent ID: {agent_id}")
    return {"message": f"Mission ID: {id} successfully assigned to Agent ID: {agent_id}"}