# gateway/main.py
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import httpx
from typing import Any

from auth import get_current_user, oauth2_scheme
from middleware.logging_middleware import log_requests
from middleware.error_handler import add_exception_handlers

app = FastAPI(
    title="API Gateway", 
    version="1.0.0",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": "fastapi"
    }
)

app.middleware("http")(log_requests)
add_exception_handlers(app)

# Service URLs
SERVICES = {
    "student": "http://localhost:8001",
    "course": "http://localhost:8002",
    "auth": "http://localhost:8003"
}

# Duplicate the model here just for Swagger UI documentation purposes
class UserCreate(BaseModel):
    username: str
    password: str

# Auth Service Routes
@app.post("/gateway/auth/register")
async def register_user(user: UserCreate):
    """Register a new user through gateway"""
    return await forward_request("auth", "/api/auth/register", "POST", json=user.model_dump())

@app.post("/gateway/auth/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login a user through gateway"""
    # For OAuth2PasswordRequestForm compatibility, we need to extract and forward form data 
    data = {"username": form_data.username, "password": form_data.password}
    return await forward_request("auth", "/api/auth/login", "POST", data=data)

async def forward_request(service: str, path: str, method: str, **kwargs) -> Any:
    """Forward request to the appropriate microservice"""
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")
    
    url = f"{SERVICES[service]}{path}"
    
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, **kwargs)
            elif method == "POST":
                response = await client.post(url, **kwargs)
            elif method == "PUT":
                response = await client.put(url, **kwargs)
            elif method == "DELETE":
                response = await client.delete(url, **kwargs)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")

            if response.status_code >= 400:
                # Provide a more structured error from the microservice
                error_detail = response.json() if response.text else "Integration error"
                raise HTTPException(status_code=response.status_code, detail=error_detail)

            return JSONResponse(
                content=response.json() if response.text else None,
                status_code=response.status_code
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "API Gateway is running", "available_services": list(SERVICES.keys())}

# Student Service Routes
@app.get("/gateway/students")
async def get_all_students(current_user: str = Depends(get_current_user)):
    """Get all students through gateway"""
    return await forward_request("student", "/api/students", "GET")

@app.get("/gateway/students/{student_id}")
async def get_student(student_id: int, current_user: str = Depends(get_current_user)):
    """Get a student by ID through gateway"""
    return await forward_request("student", f"/api/students/{student_id}", "GET")

@app.post("/gateway/students")
async def create_student(request: Request, current_user: str = Depends(get_current_user)):
    """Create a new student through gateway"""
    body = await request.json()
    return await forward_request("student", "/api/students", "POST", json=body)

@app.put("/gateway/students/{student_id}")
async def update_student(student_id: int, request: Request, current_user: str = Depends(get_current_user)):
    """Update a student through gateway"""
    body = await request.json()
    return await forward_request("student", f"/api/students/{student_id}", "PUT", json=body)

@app.delete("/gateway/students/{student_id}")
async def delete_student(student_id: int, current_user: str = Depends(get_current_user)):
    """Delete a student through gateway"""
    return await forward_request("student", f"/api/students/{student_id}", "DELETE")

# Course Service Routes
@app.get("/gateway/courses")
async def get_all_courses(current_user: str = Depends(get_current_user)):
    """Get all courses through gateway"""
    return await forward_request("course", "/api/courses", "GET")

@app.get("/gateway/courses/{course_id}")
async def get_course(course_id: int, current_user: str = Depends(get_current_user)):
    """Get a course by ID through gateway"""
    return await forward_request("course", f"/api/courses/{course_id}", "GET")

@app.post("/gateway/courses")
async def create_course(request: Request, current_user: str = Depends(get_current_user)):
    """Create a new course through gateway"""
    body = await request.json()
    return await forward_request("course", "/api/courses", "POST", json=body)

@app.put("/gateway/courses/{course_id}")
async def update_course(course_id: int, request: Request, current_user: str = Depends(get_current_user)):
    """Update a course through gateway"""
    body = await request.json()
    return await forward_request("course", f"/api/courses/{course_id}", "PUT", json=body)

@app.delete("/gateway/courses/{course_id}")
async def delete_course(course_id: int, current_user: str = Depends(get_current_user)):
    """Delete a course through gateway"""
    return await forward_request("course", f"/api/courses/{course_id}", "DELETE")