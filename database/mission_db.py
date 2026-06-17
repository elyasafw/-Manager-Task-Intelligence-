from .db_connection import db
from pydantic import BaseModel


class NewMission(BaseModel):
    title : str
    description : str
    location : str
    difficulty : int
    importance : int


# Temporary utility functions
def validation_rank(data: dict):
    if data["agent_rank"].lower() not in ["junior, senior, commander"]:
        return "The 'agent_rank' field must only be: Junior / Senior / Commander"

def new_objects_decomposition(data: NewAgent):
    """פונקציית ולידציה וקבלת ערכי המילון מתוך האובייקט והעברה לפונקציית יצירת המשימה"""
    new_agent = data.model_dump()
    validation_rank(new_agent)
    values = [new_agent["name"], new_agent["specialty"], new_agent["agent_rank"]]

def up_objects_decomposition(data: UpdateAgent):
    """פונקציית ולידציה וקבלת ערכי המילון מתוך האובייקט והעברה לפונקציית עדכון המשימה"""
    update_agent = data.model_dump(exclude_none=True)
    if "agent_rank" in update_agent:
        validation_rank(update_agent)
    columns = [f"{column} = %s" for column in list(update_agent.keys())]
    values = list(update_agent.values())


class MissionDB:

    def create_mission(self, data):