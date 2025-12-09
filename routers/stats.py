from fastapi import APIRouter
from routers.tasks import tasks_db

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)

@router.get("/stats")
async def get_tasks_stats() -> dict:
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    by_status = {"completed": 0, "pending": 0}

    for t in tasks_db:
        by_quadrant[t["quadrant"]] += 1
        by_status[t["status"]] += 1

    return {"total_tasks": len(tasks_db), "by_quadrant": by_quadrant, "by_status": by_status}
