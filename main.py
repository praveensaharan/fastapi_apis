from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Request, Header, HTTPException, Depends, Path, status, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import redis
import os
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
from mangum import Mangum



app = FastAPI(
    title="FastAPI Rate Limiting",
    description="Rate limiting users using Redis middleware",
    docs_url="/",
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["X-User"],
)


redis_conn = redis.Redis(
    host= os.getenv("REDIS_HOSTNAME"),
    port= os.getenv("REDIS_PORT"),
    password= os.getenv("REDIS_PASSWORD"),

)

Mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(Mongo_uri)
db = client["library_management"]
collection = db["students"]

class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address

class UpdateStudent(BaseModel):
    name: str = None
    age: int = None
    address: Address = None



def get_user(request: Request):
    user = request.headers.get("X-User")
    if not user:
        raise HTTPException(status_code=401, detail="X-User header is missing")
    return user

async def rate_limit_user(user: str) -> Optional[JSONResponse]:
    current_day = datetime.utcnow().strftime("%Y-%m-%d")
    redis_key = f"user:{user}:{current_day}"

    current_count = redis_conn.incr(redis_key)
    if current_count == 1:
        redis_conn.expire(redis_key, 86400) 
# 86400 seconds = 24 hours
# here we add only ten attenpts for user in 24 hours
    if current_count > 10:
        return JSONResponse(
            status_code=429,
            content={"detail": "User Rate Limit Exceeded"},
            headers={
                "Retry-After": "86400",  
            },
        )

    return None

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    user = get_user(request)
    rate_limit_exceeded_response = await rate_limit_user(user)
    if rate_limit_exceeded_response:
        return rate_limit_exceeded_response

    response = await call_next(request)
    return response

@app.post("/students", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_student(student: Student):
    result = collection.insert_one(student.dict())
    return {"id": str(result.inserted_id)}



@app.get("/students", response_model=dict)
async def list_students(country: str = Query(None, description="To apply filter of country."),
                        min_age: int = Query(None, description="Only records which have age greater than equal to the provided age should be present in the result.")):
    query = {}
    if country:
        # Use regular expression for case-insensitive comparison in MongoDB
        query["address.country"] = {"$regex": country, "$options": "i"}
    if min_age:
        query["age"] = {"$gte": min_age}

    students = []
    for student in collection.find(query, {"name": 1, "age": 1, "_id": 0}):
        students.append({"name": student["name"], "age": student["age"]})

    return JSONResponse(content={"data": students})



@app.get("/students/{id}", response_model=dict)
async def fetch_student(id: str = Path(..., title="The ID of the student to fetch")):
    student = collection.find_one({"_id": ObjectId(id)})
    if student:
        # Transform ObjectId to string
        student['_id'] = str(student['_id'])
        # Prepare the response with the correct schema
        response_data = {
            "name": student["name"],
            "age": student["age"],
            "address": {
                "city": student["address"]["city"],
                "country": student["address"]["country"]
            }
        }
        return response_data
    else:
        raise HTTPException(status_code=404, detail="Student not found")


@app.patch("/students/{id}", status_code=204)
async def update_student(id: str, student: UpdateStudent):
    student_data = {k: v for k, v in student.dict().items() if v is not None}
    if len(student_data) >= 1:
        result = collection.update_one(
            {"_id": ObjectId(id)}, {"$set": student_data})
        if result.modified_count == 1:
            return
        else:
            raise HTTPException(status_code=404, detail="Student not found")
    else:
        raise HTTPException(status_code=400, detail="No fields to update")


@app.delete("/students/{id}", status_code=200)
async def delete_student(id: str):
    result = collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return
    else:
        raise HTTPException(status_code=404, detail="Student not found")
    



handler = Mangum(app)
