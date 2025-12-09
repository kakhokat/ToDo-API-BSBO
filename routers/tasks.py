from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Response, status

from database import calc_quadrant, tasks_db
from schemas import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=dict)
async def get_all_tasks() -> dict:
    return {"count": len(tasks_db), "tasks": tasks_db}


@router.get("/quadrant/{quadrant}", response_model=dict)
async def get_tasks_by_quadrant(quadrant: str) -> dict:
    if quadrant not in ("Q1", "Q2", "Q3", "Q4"):
        raise HTTPException(status_code=400, detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4")

    filtered = [t for t in tasks_db if t["quadrant"] == quadrant]
    return {"quadrant": quadrant, "count": len(filtered), "tasks": filtered}


@router.get("/status/{status_name}", response_model=dict)
async def get_tasks_by_status(status_name: str) -> dict:
    if status_name not in ("completed", "pending"):
        raise HTTPException(status_code=404, detail='Статус не найден. Используйте "completed" или "pending"')

    need_completed = status_name == "completed"
    filtered = [t for t in tasks_db if t.get("completed") is need_completed]
    return {"status": status_name, "count": len(filtered), "tasks": filtered}


@router.get("/search", response_model=dict)
async def search_tasks(q: str = Query(..., min_length=2)) -> dict:
    q_lower = q.strip().lower()

    filtered = [
        t
        for t in tasks_db
        if q_lower in t["title"].lower()
        or (t.get("description") and q_lower in str(t["description"]).lower())
    ]

    if not filtered:
        raise HTTPException(status_code=404, detail="Задачи по запросу не найдены")

    return {"query": q, "count": len(filtered), "tasks": filtered}


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(task_id: int) -> TaskResponse:
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate) -> TaskResponse:
    quadrant = calc_quadrant(task.is_important, task.is_urgent)
    new_id = max([t["id"] for t in tasks_db], default=0) + 1

    new_task = {
        "id": new_id,
        "title": task.title,
        "description": task.description,
        "is_important": task.is_important,
        "is_urgent": task.is_urgent,
        "quadrant": quadrant,
        "completed": False,
        "created_at": datetime.now(),
    }

    tasks_db.append(new_task)
    return new_task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate) -> TaskResponse:
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        task[field] = value

    if "is_important" in update_data or "is_urgent" in update_data:
        task["quadrant"] = calc_quadrant(task["is_important"], task["is_urgent"])

    return task


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(task_id: int) -> TaskResponse:
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    task["completed"] = True
    task["completed_at"] = datetime.now()  # поля нет в Pydantic-схеме — это нормально по методичке
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int):
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    tasks_db.remove(task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
