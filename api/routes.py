import asyncio
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
import json
import logging
import uuid

# Import our modules
from modules.nlu_module import NLUModule
from modules.task_planning import TaskPlanner, Task
from modules.execution import ExecutionModule

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Smartphone AI Agent API")

# Initialize our modules
nlu_module = NLUModule()
task_planner = TaskPlanner()
execution_module = ExecutionModule()

# Define API models
class CommandRequest(BaseModel):
    text: str
    session_id: Optional[str] = None

class TaskApprovalRequest(BaseModel):
    session_id: str
    task_id: str
    approved: bool

class CommandResponse(BaseModel):
    session_id: str
    parsed_intent: Dict
    tasks: List[Dict]
    message: str

# Active sessions
active_sessions = {}

@app.post("/command", response_model=CommandResponse)
async def process_command(request: CommandRequest):
    """Process a natural language command"""
    # Create a session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # Parse the command
        parsed_intent = nlu_module.parse_command(request.text)
        
        # Create task plan
        tasks = task_planner.create_task_plan(parsed_intent)
        
        # Store tasks in session
        active_sessions[session_id] = {
            "parsed_intent": parsed_intent,
            "tasks": tasks,
            "status": "pending_approval"
        }
        
        # Prepare response
        task_descriptions = [task.description for task in tasks]
        response_message = f"I'll help you with that. Here's what I'll do:\n" + "\n".join([f"- {desc}" for desc in task_descriptions])
        
        return CommandResponse(
            session_id=session_id,
            parsed_intent=parsed_intent,
            tasks=[task.to_dict() for task in tasks],
            message=response_message
        )
    
    except Exception as e:
        logger.error(f"Error processing command: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing command: {str(e)}")

@app.post("/approve-task")
async def approve_task(request: TaskApprovalRequest):
    """Approve or reject a task"""
    session_id = request.session_id
    task_id = request.task_id
    approved = request.approved
    
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    session = active_sessions[session_id]
    tasks = session.get("tasks", [])
    
    # Find the task by ID
    found_task = None
    for task in tasks:
        if task.get("task_id") == task_id:
            found_task = task
            break
    
    if not found_task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found in session")
    
    if approved:
        # Execute the task
        try:
            await execution_module.execute_task(found_task)
            session["status"] = "completed"
            return {"message": f"Task '{found_task.get('description', '')}' approved and executed"}
        except Exception as e:
            logger.error(f"Error executing task: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error executing task: {str(e)}")
    else:
        # Handle task rejection 
        session["status"] = "rejected"
        return {"message": f"Task '{found_task.get('description', '')}' rejected"}


@app.get("/")
async def root():
    return {"message": "Hello World"}
