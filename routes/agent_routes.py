from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from database.agent_db import agents_manager
from logs.logger_config import logger
from utils.services_validations import validation_rank


class NewAgent(BaseModel):
    name : str
    specialty : str
    agent_rank : str

class UpdateAgent(BaseModel):
    name : str | None = None
    specialty : str | None = None
    agent_rank : str | None = None


agent_router = APIRouter()


@agent_router.post("/agents", status_code=status.HTTP_201_CREATED)
def create_new_agent(new_agent: NewAgent):
    agent = new_agent.model_dump()
    if not validation_rank(agent):
       logger.error("Agent not create: invalid value in 'agent_rank' field")
       raise HTTPException(
           status_code=status.HTTP_400_BAD_REQUEST,
           detail="The 'agent_rank' field must only be: Junior / Senior / Commander"
           )
    values = [
        new_agent["name"],
        new_agent["specialty"],
        new_agent["agent_rank"]
        ]
    is_create = agents_manager.create_agent(values)
    if not is_create:
        logger.error("Creating a new agent failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Creating a new agent failed..."
            )
    logger.info("New agent created successfully")
    return agent

@agent_router.get("/agents")
def get_all_agents():
    all_agents = agents_manager.get_all_agents()
    logger.info("Getting list of all agents")
    return all_agents

@agent_router.get("/agents/{id}")
def get_agent_by_id(id: int):
    agent = agents_manager.get_agent_by_id(id)
    if not agent:
        logger.error(f"Agent ID {id} not found")
        return None
    logger.info(f"Getting details of agent ID: {id}")
    return agent

@agent_router.put("/agents/{id}")
def update_agent(id: int, update_data: UpdateAgent):
    update_agent = update_data.model_dump(exclude_none=True)
    if "agent_rank" in update_agent:
        if not validation_rank(update_agent):
            logger.error(f"Agent ID {id} not update: invalid value in 'agent_rank' field")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The 'agent_rank' field must only be: Junior / Senior / Commander"
                )
    is_update = agents_manager.update_agent(id, update_agent)
    if not is_update:
        logger.error(f"Agent ID: {id} update failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent ID: {id} update failed..."
            )
    logger.info(f"Agent ID: {id} update successfully")
    return {"message": f"Agent ID: {id} successfully updated"}

@agent_router.put("/agents/{id}/deactivate")
def deactivate_agent(id: int):
    if not agents_manager.get_agent_by_id(id):
        logger.error(f"Agent ID: {id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= f"Agent ID: {id} not found"
            )
    is_deactivate = agents_manager.deactivate_agent(id)
    if not is_deactivate:
        logger.error(f"Agent ID: {id} deactivate failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Agent ID: {id} deactivate failed..."
            )
    logger.info(f"Agent ID: {id} successfully deactivated")
    return {"message": f"Agent ID: {id} successfully deactivated"}

@agent_router.get("/agents/{id}/performance")
def get_performance_agent(id):
    performance_agent= agents_manager.get_agent_performance(id)
    if not performance_agent:
        logger.error(f"Agent ID: {id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= f"Agent ID: {id} not found"
            )
    logger.info(f"Getting performance report of agent ID: {id}")
    return performance_agent