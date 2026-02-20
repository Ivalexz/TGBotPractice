from typing import Dict
from models import TaskCreate
from auth import get_current_user

tasks_db: Dict[int, Dict] = {}
next_task_id = {}
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

myapp = FastAPI()

@myapp.post("/tasks/{user_id}")
def create_task(user_id: int, task: TaskCreate):
    if user_id not in tasks_db:
        tasks_db[user_id] = {}
        next_task_id[user_id] = 1

    task_id = next_task_id[user_id]
    next_task_id[user_id] += 1

    tasks_db[user_id][task_id] = {
        "name": task.name,
        "description": task.description,
        "status": "Не виконано"
    }

    return {
        "message": "Task created",
        "task": {
            "id": task_id,
            "name": task.name,
            "description": task.description,
            "status": "Не виконано"
        }
    }

@myapp.get("/tasks/{user_id}")
def get_tasks(user_id: int):
    user_tasks = tasks_db.get(user_id, {})
    return {
        "tasks": user_tasks,
        "count": len(user_tasks)
    }

@myapp.delete("/tasks/{user_id}/{task_id}")
def delete_task(user_id: int, task_id: int):

    if user_id not in tasks_db or task_id not in tasks_db[user_id]:
        raise HTTPException(status_code=404, detail="Task not found")

    del tasks_db[user_id][task_id]

    return {"message": "Task deleted"}

@myapp.patch("/tasks/{user_id}/{task_id}")
def edit_status(user_id: int, task_id: int):

    if user_id not in tasks_db or task_id not in tasks_db[user_id]:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks_db[user_id][task_id]

    if task["status"] == "Не виконано":
        task["status"] = "Виконано"
    else:
        task["status"] = "Не виконано"

    return {
        "message": "Status updated",
        "task": {
            "id": task_id,
            "status": task["status"]
        }
    }