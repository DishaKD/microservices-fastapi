from pydantic import BaseModel
from typing import Optional

class Course(BaseModel):
    id: int
    title: str
    description: str
    instructor: str

class CourseCreate(BaseModel):
    title: str
    description: str
    instructor: str

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    instructor: Optional[str] = None
