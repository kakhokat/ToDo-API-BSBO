from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами с использованием матрицы Эйзенхауэра",
    version="1.0.0",
    contact={"name": "Черномырдин Михаил Алексеевич"},
)

# Тестовое хранилище (4 задачи для проверки эндпоинтов)
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
        "description": "Посетить лекцию по предмету",
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


@app.get("/")
async def root() -> dict:
    # по заданию: выводим заполненные параметры FastAPI (пример в методичке)
    return {
        "title": app.title,
        "description": app.description,
        "version": app.version,
        "contact": app.contact,
    }


@app.get("/tasks")
async def get_all_tasks() -> dict:
    return {"count": len(tasks_db), "tasks": tasks_db}


@app.get("/tasks/quadrant/{quadrant}")
async def get_tasks_by_quadrant(quadrant: str) -> dict:
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException(status_code=400, detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4")

    filtered = [task for task in tasks_db if task["quadrant"] == quadrant]
    return {"quadrant": quadrant, "count": len(filtered), "tasks": filtered}


# ВАЖНО: эти роуты должны быть ДО /tasks/{task_id}
@app.get("/tasks/stats")
async def get_tasks_stats() -> dict:
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    by_status = {"completed": 0, "pending": 0}

    for task in tasks_db:
        by_quadrant[task["quadrant"]] += 1
        by_status[task["status"]] += 1

    return {"total_tasks": len(tasks_db), "by_quadrant": by_quadrant, "by_status": by_status}


@app.get("/tasks/status/{status}")
async def get_tasks_by_status(status: str) -> dict:
    if status not in ["completed", "pending"]:
        raise HTTPException(status_code=404, detail='Статус не найден. Используйте "completed" или "pending"')

    filtered = [task for task in tasks_db if task["status"] == status]
    return {"status": status, "count": len(filtered), "tasks": filtered}


@app.get("/tasks/search")
async def search_tasks(q: str) -> dict:
    q = q.strip()
    if len(q) < 2:
        raise HTTPException(status_code=400, detail="Ключевое слово должно быть минимум 2 символа")

    q_lower = q.lower()
    filtered = [
        task
        for task in tasks_db
        if q_lower in task["title"].lower()
        or (task["description"] and q_lower in task["description"].lower())
    ]

    if not filtered:
        raise HTTPException(status_code=404, detail="Задачи по запросу не найдены")

    return {"query": q, "count": len(filtered), "tasks": filtered}


@app.get("/tasks/{task_id}")
async def get_task_by_id(task_id: int) -> dict:
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Задача не найдена")
