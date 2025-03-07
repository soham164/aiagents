from typing import Dict, List, Any, Callable, Optional
import asyncio
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExecutionModule:
    """Executes tasks and manages the feedback loop with the user"""
    
    def __init__(self):
        # Register action handlers
        self.action_handlers = {
            # App actions
            "check_app_installed": self._handle_check_app_installed,
            "launch_app": self._handle_launch_app,
            
            # Calendar actions
            "check_calendar_availability": self._handle_check_calendar_availability,
            "create_calendar_event": self._handle_create_calendar_event,
            
            # Transaction actions
            "verify_payment_details": self._handle_verify_payment_details,
            "confirm_transaction": self._handle_confirm_transaction,
            "execute_transaction": self._handle_execute_transaction,
            
            # Analysis actions
            "fetch_analysis_data": self._handle_fetch_analysis_data,
            "generate_analysis": self._handle_generate_analysis,
            "present_analysis_results": self._handle_present_analysis_results,
            
            # Utility actions
            "request_clarification": self._handle_request_clarification,
            "unsupported_intent": self._handle_unsupported_intent
        }
        
        # Initialize OS and app connectors
        self.os_connector = self._init_os_connector()
        self.app_connectors = {}
    
    def _init_os_connector(self):
        """Initialize the operating system connector"""
        # In a real implementation, this would connect to Android/iOS APIs
        return {
            "name": "Smartphone OS Connector",
            "status": "connected",
            "installed_apps": ["calendar", "maps", "messages", "email", "photos", "camera"]
        }
    
    async def execute_tasks(self, tasks: List, feedback_callback: Callable, approval_callback: Callable):
        """
        Execute a sequence of tasks with user feedback and approval
        
        Args:
            tasks: List of Task objects to execute
            feedback_callback: Function to call with step updates
            approval_callback: Function to get user approval for tasks
        
        Returns:
            Execution results
        """
        results = []
        
        for task in tasks:
            # Provide feedback that we're starting this task
            await feedback_callback({
                "type": "task_started",
                "task": task.to_dict(),
                "timestamp": datetime.now().isoformat()
            })
            
            # Check if task requires approval
            if task.requires_approval:
                approval = await approval_callback(task)
                if not approval:
                    task.approval_status = "rejected"
                    task.status = "failed"
                    task.error = "User rejected this task"
                    
                    await feedback_callback({
                        "type": "task_rejected",
                        "task": task.to_dict(),
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Stop execution if a task is rejected
                    break
                
                task.approval_status = "approved"
            
            # Update task status
            task.status = "in_progress"
            
            # Execute the task
            try:
                if task.action in self.action_handlers:
                    handler = self.action_handlers[task.action]
                    result = await handler(task.params)
                    
                    # Update task with result
                    task.status = "completed"
                    results.append({
                        "task": task.to_dict(),
                        "result": result
                    })
                    
                    # Provide feedback about completion
                    await feedback_callback({
                        "type": "task_completed",
                        "task": task.to_dict(),
                        "result": result,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    # Unknown action
                    task.status = "failed"
                    task.error = f"Unknown action: {task.action}"
                    
                    await feedback_callback({
                        "type": "task_failed",
                        "task": task.to_dict(),
                        "error": task.error,
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                # Handle execution error
                task.status = "failed"
                task.error = str(e)
                
                await feedback_callback({
                    "type": "task_failed",
                    "task": task.to_dict(),
                    "error": task.error,
                    "timestamp": datetime.now().isoformat()
                })
        
        return results
    
    # App action handlers
    
    async def _handle_check_app_installed(self, params: Dict) -> Dict:
        """Check if an app is installed on the device"""
        app_name = params.get("app_name")
        installed = app_name in self.os_connector["installed_apps"]
        
        # Simulate a small delay for API call
        await asyncio.sleep(0.5)
        
        return {
            "installed": installed,
            "app_name": app_name
        }
    
    async def _handle_launch_app(self, params: Dict) -> Dict:
        """Launch an app on the device"""
        app_name = params.get("app_name")
        
        # Check if app is installed first
        check_result = await self._handle_check_app_installed({"app_name": app_name})
        
        if not check_result["installed"]:
            raise Exception(f"App '{app_name}' is not installed")
        
        # Simulate app launch
        await asyncio.sleep(1)
        
        return {
            "launched": True,
            "app_name": app_name
        }
    
    # Calendar action handlers
    
    async def _handle_check_calendar_availability(self, params: Dict) -> Dict:
        """Check calendar availability for a given time slot"""
        date = params.get("date")
        time = params.get("time")
        duration = params.get("duration")
        
        # In a real implementation, this would query the calendar API
        # Simulate API delay
        await asyncio.sleep(1.5)
        
        # Simulate checking availability (always available in this demo)
        return {
            "available": True,
            "date": date,
            "time": time,
            "duration": duration,
            "conflicts": []
        }
    
    async def _handle_create_calendar_event(self, params: Dict) -> Dict:
        """Create a calendar event"""
        date = params.get("date")
        time = params.get("time")
        duration = params.get("duration")
        participants = params.get("participants", [])
        
        # In a real implementation, this would call the calendar API
        # Simulate API delay
        await asyncio.sleep(2)
        
        # Simulate event creation
        event_id = "evt_" + datetime.now().strftime("%Y%m%d%H%M%S")
        
        return {
            "created": True,
            "event_id": event_id,
            "date": date,
            "time": time,
            "duration": duration,
            "participants": participants
        }
    
    # Transaction action handlers
    
    async def _handle_verify_payment_details(self, params: Dict) -> Dict:
        """Verify payment details before executing a transaction"""
        amount = params.get("amount")
        recipient = params.get("recipient")
        payment_method = params.get("payment_method")
        
        # In a real implementation, this would verify recipient details
        # Simulate API delay
        await asyncio.sleep(1)
        
        return {
            "verified": True,
            "amount": amount,
            "recipient": recipient,
            "payment_method": payment_method,
            "fee": 0.0
        }
    
    async def _handle_confirm_transaction(self, params: Dict) -> Dict:
        """Get final confirmation for a transaction"""
        # This is a placeholder - the actual confirmation happens through the approval_callback
        return {"confirmed": True}
    
    async def _handle_execute_transaction(self, params: Dict) -> Dict:
        """Execute a payment transaction"""
        amount = params.get("amount")
        recipient = params.get("recipient")
        payment_method = params.get("payment_method")
        
        # In a real implementation, this would call payment APIs
        # Simulate API delay
        await asyncio.sleep(2.5)
        
        # Simulate transaction
        transaction_id = "tx_" + datetime.now().strftime("%Y%m%d%H%M%S")
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "amount": amount,
            "recipient": recipient,
            "payment_method": payment_method,
            "timestamp": datetime.now().isoformat()
        }
    
    # Analysis action handlers
    
    async def _handle_fetch_analysis_data(self, params: Dict) -> Dict:
        """Fetch data for analysis"""
        metric = params.get("metric")
        time_range = params.get("time_range")
        grouping = params.get("grouping")
        
        # In a real implementation, this would query analytics APIs
        # Simulate API delay
        await asyncio.sleep(2)
        
        # Simulate data retrieval
        # Generate sample data for demo purposes
        import random
        
        data_points = []
        categories = ["Category A", "Category B", "Category C"]
        
        for i in range(10):
            data_points.append({
                "date": f"2024-03-{i+1:02d}",
                "value": random.randint(10, 100),
                "category": random.choice(categories)
            })
        
        return {
            "success": True,
            "metric": metric,
            "time_range": time_range,
            "grouping": grouping,
            "data_points": data_points
        }
    
    async def _handle_generate_analysis(self, params: Dict) -> Dict:
        """Generate analysis from fetched data"""
        metric = params.get("metric")
        time_range = params.get("time_range")
        grouping = params.get("grouping")
        
        # In a real implementation, this would process the data
        # Simulate processing delay
        await asyncio.sleep(1.5)
        
        # Get data (in a real app, this would use the previously fetched data)
        fetch_result = await self._handle_fetch_analysis_data(params)
        data_points = fetch_result.get("data_points", [])
        
        # Calculate simple statistics
        total = sum(point["value"] for point in data_points)
        average = total / len(data_points) if data_points else 0
        maximum = max(point["value"] for point in data_points) if data_points else 0
        minimum = min(point["value"] for point in data_points) if data_points else 0
        
        # Group by category if needed
        category_totals = {}
        if grouping == "category":
            for point in data_points:
                category = point.get("category", "Unknown")
                if category not in category_totals:
                    category_totals[category] = 0
                category_totals[category] += point["value"]
        
        return {
            "success": True,
            "metric": metric,
            "time_range": time_range,
            "total": total,
            "average": average,
            "maximum": maximum,
            "minimum": minimum,
            "by_category": category_totals if grouping == "category" else {},
            "data_points": data_points
        }
    
    async def _handle_present_analysis_results(self, params: Dict) -> Dict:
        """Prepare presentation of analysis results"""
        metric = params.get("metric")
        format = params.get("format", "chart")
        
        # In a real implementation, this would format the results for display
        # Simulate formatting delay
        await asyncio.sleep(0.5)
        
        return {
            "success": True,
            "metric": metric,
            "format": format,
            "rendering_instructions": {
                "chart_type": "bar" if format == "chart" else "table",
                "title": f"Analysis of {metric}",
                "x_axis": "Date",
                "y_axis": "Value"
            }
        }
    
    # Utility action handlers
    
    async def _handle_request_clarification(self, params: Dict) -> Dict:
        """Handle a request for clarification"""
        missing = params.get("missing", [])
        if isinstance(missing, str):
            missing = [missing]
            
        return {
            "requires_clarification": True,
            "missing_parameters": missing
        }
    
    async def _handle_unsupported_intent(self, params: Dict) -> Dict:
        """Handle an unsupported intent"""
        return {
            "supported": False,
            "original_text": params.get("original_text")
        }