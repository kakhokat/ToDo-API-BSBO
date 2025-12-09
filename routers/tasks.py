from fastapi import APIRouter, HTTPException, Query

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Task not found"}},
)

# Временное хранилище (4 задачи)
tasks_db = [
    {
        "id": 1,
        "title": "Сдать проект по FastAPI",
        "description": "Завершить разработку API и написать документацию",
        "quadrant": "Q1",
        "status": "pending",
    },
    {
        "id": 2,
        "title": "Изучить SQLAlchemy",
        "description": "Прочитать документацию и попробовать примеры",
        "quadrant": "Q2",
        "status": "pending",
    },
    {
        "id": 3,
        "title": "Сходить на лекцию",
        "description": "Сходить на лекцию",
        "quadrant": "Q3",
        "status": "pending",
    },
    {
        "id": 4,
        "title": "Посмотреть сериал",
        "description": "Новый сезон любимого сериала",
        "quadrant": "Q4",
        "status": "completed",
    },
]


@router.get("")
async def get_all_tasks() -> dict:
    return {"count": len(tasks_db), "tasks": tasks_db}


@router.get("/quadrant/{quadrant}")
async def get_tasks_by_quadrant(quadrant: str) -> dict:
    if quadrant not in ("Q1", "Q2", "Q3", "Q4"):
        raise HTTPException(status_code=400, detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4")

    filtered = [t for t in tasks_db if t["quadrant"] == quadrant]
    return {"quadrant": quadrant, "count": len(filtered), "tasks": filtered}


@router.get("/status/{status}")
async def get_tasks_by_status(status: str) -> dict:
    if status not in ("completed", "pending"):
        raise HTTPException(status_code=404, detail='Статус не найден. Используйте "completed" или "pending"')

    filtered = [t for t in tasks_db if t["status"] == status]
    return {"status": status, "count": len(filtered), "tasks": filtered}


@router.get("/search")
async def search_tasks(q: str = Query(..., min_length=2)) -> dict:
    q_lower = q.strip().lower()
    filtered = [
        t
        for t in tasks_db
        if q_lower in t["title"].lower()
        or (t["description"] and q_lower in t["description"].lower())
    ]

    if not filtered:
        raise HTTPException(status_code=404, detail="Задачи по запросу не найдены")

    return {"query": q, "count": len(filtered), "tasks": filtered}


@router.get("/{task_id}")
async def get_task_by_id(task_id: int) -> dict:
    for t in tasks_db:
        if t["id"] == task_id:
            return t
    raise HTTPException(status_code=404, detail="Задача не найдена")
