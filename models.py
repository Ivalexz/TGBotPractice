from pydantic import BaseModel

class TaskCreate(BaseModel):
    name: str
    description: str

class TaskResponse(BaseModel):
    id: int
    name: str
    description: str
    status: str