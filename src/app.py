"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import threading

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# MongoDB setup
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "mergington"
COLLECTION_NAME = "activities"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
activities_collection = db[COLLECTION_NAME]

# Pre-populate activities if collection is empty (thread-safe, only once)
prepopulate_lock = threading.Lock()
def prepopulate_activities():
    with prepopulate_lock:
        if activities_collection.count_documents({}) == 0:
            initial_activities = {
                "Chess Club": {
                    "description": "Learn strategies and compete in chess tournaments",
                    "schedule": "Fridays, 3:30 PM - 5:00 PM",
                    "max_participants": 12,
                    "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
                },
                "Programming Class": {
                    "description": "Learn programming fundamentals and build software projects",
                    "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                    "max_participants": 20,
                    "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
                },
                "Gym Class": {
                    "description": "Physical education and sports activities",
                    "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
                    "max_participants": 30,
                    "participants": ["john@mergington.edu", "olivia@mergington.edu"]
                },
                "Soccer Team": {
                    "description": "Join the school soccer team and compete in matches",
                    "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
                    "max_participants": 22,
                    "participants": ["liam@mergington.edu", "noah@mergington.edu"]
                },
                "Basketball Team": {
                    "description": "Practice and compete in basketball tournaments",
                    "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
                    "max_participants": 15,
                    "participants": ["ava@mergington.edu", "mia@mergington.edu"]
                },
                "Art Club": {
                    "description": "Explore various art techniques and create masterpieces",
                    "schedule": "Thursdays, 3:30 PM - 5:00 PM",
                    "max_participants": 15,
                    "participants": ["isabella@mergington.edu", "amelia@mergington.edu"]
                },
                "Drama Club": {
                    "description": "Act, direct, and produce plays and performances",
                    "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
                    "max_participants": 20,
                    "participants": ["elijah@mergington.edu", "charlotte@mergington.edu"]
                },
                "Math Club": {
                    "description": "Solve challenging problems and participate in math competitions",
                    "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
                    "max_participants": 10,
                    "participants": ["lucas@mergington.edu", "harper@mergington.edu"]
                },
                "Science Club": {
                    "description": "Conduct experiments and explore scientific concepts",
                    "schedule": "Fridays, 3:30 PM - 5:00 PM",
                    "max_participants": 12,
                    "participants": ["jackson@mergington.edu", "ella@mergington.edu"]
                }
            }
            for name, data in initial_activities.items():
                doc = {"_id": name, **data}
                try:
                    activities_collection.insert_one(doc)
                except DuplicateKeyError:
                    pass

prepopulate_activities()

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    activities = {}
    for doc in activities_collection.find():
        name = doc["_id"]
        activities[name] = {
            "description": doc["description"],
            "schedule": doc["schedule"],
            "max_participants": doc["max_participants"],
            "participants": doc["participants"]
        }
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    doc = activities_collection.find_one({"_id": activity_name})
    if not doc:
        raise HTTPException(status_code=404, detail="Activity not found")
    if email in doc["participants"]:
        raise HTTPException(status_code=400, detail="Already signed up for this activity")
    if len(doc["participants"]) >= doc["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")
    activities_collection.update_one(
        {"_id": activity_name},
        {"$push": {"participants": email}}
    )
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    doc = activities_collection.find_one({"_id": activity_name})
    if not doc:
        raise HTTPException(status_code=404, detail="Activity not found")
    if email not in doc["participants"]:
        raise HTTPException(status_code=400, detail="Student not signed up for this activity")
    activities_collection.update_one(
        {"_id": activity_name},
        {"$pull": {"participants": email}}
    )
    return {"message": f"Unregistered {email} from {activity_name}"}
