from fastapi import APIRouter, HTTPException, status
from database.mission_db import missions_manager
from database.agent_db import agents_manager
from logs.logger_config import logger


report_router = APIRouter()


@report_router.get("/reports/summary")
def summary_report():
    report = {
            "active_agents_count": agents_manager.count_active_agents(),
            "total_missions": missions_manager.count_all_missions(),
            "open_missions": missions_manager.count_open_missions(),
            "completed_missions": missions_manager.count_by_status("COMPLETED"),
            "failed_missions": missions_manager.count_by_status("FAILED"),
            "critical_missions": missions_manager.count_critical_missions()
            }
    logger.info("Getting summary report successfully")
    return report

@report_router.get("/reports/missions-by-status")
def status_missions_report():
    report = {
            "open": missions_manager.count_open_missions(),
            "in_progress": missions_manager.count_by_status("IN_PROGRESS"),
            "completed": missions_manager.count_by_status("COMPLETED"),
            "failed": missions_manager.count_by_status("FAILED"),
            "critical": missions_manager.count_critical_missions()
            }
    logger.info("Getting status missions report successfully")
    return report

@report_router.get("/reports/top-agent")
def get_top_agent():
    top_agent = missions_manager.get_top_agent()
    logger.info("Getting details of top agent successfully")
    return top_agent