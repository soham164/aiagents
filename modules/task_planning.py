from typing import Dict, List, Any, Optional
import uuid

class Task:
    """Represents a single executable task in the system"""
    
    def __init__(self, action: str, params: Dict[str, Any], description: str):
        self.id = str(uuid.uuid4())
        self.action = action
        self.params = params
        self.description = description
        self.status = "pending"  # pending, in_progress, completed, failed
        self.requires_approval = True
        self.approval_status = "pending"  # pending, approved, rejected
        self.error = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "action": self.action,
            "params": self.params,
            "description": self.description,
            "status": self.status,
            "requires_approval": self.requires_approval,
            "approval_status": self.approval_status,
            "error": self.error
        }


class TaskPlanner:
    """Plans tasks based on parsed NLU output"""
    
    def __init__(self):
        # Define task templates for different intents
        self.task_templates = {
            "app_switch": self._plan_app_switch,
            "calendar": self._plan_calendar,
            "transaction": self._plan_transaction,
            "analysis": self._plan_analysis
        }
    
    def create_task_plan(self, nlu_result: Dict) -> List[Task]:
        """
        Create a sequence of tasks based on NLU parsing results
        
        Args:
            nlu_result: Output from the NLU module
            
        Returns:
            List of tasks to be executed
        """
        intent = nlu_result.get("intent")
        
        if intent in self.task_templates:
            return self.task_templates[intent](nlu_result)
        else:
            # Return a fallback task for unsupported intents
            return [Task(
                "unsupported_intent",
                {"original_text": nlu_result.get("original_text")},
                "I'm not sure how to handle this request yet."
            )]
    
    def _plan_app_switch(self, nlu_result: Dict) -> List[Task]:
        """Plan tasks for app switching intent"""
        parameters = nlu_result.get("parameters", {})
        app_name = parameters.get("app_name")
        
        if not app_name:
            return [Task(
                "request_clarification",
                {"missing": "app_name"},
                "Which app would you like to open?"
            )]
        
        return [
            Task(
                "check_app_installed",
                {"app_name": app_name},
                f"Checking if {app_name} is installed"
            ),
            Task(
                "launch_app",
                {"app_name": app_name},
                f"Opening {app_name}"
            )
        ]
    
    def _plan_calendar(self, nlu_result: Dict) -> List[Task]:
        """Plan tasks for calendar management intent"""
        parameters = nlu_result.get("parameters", {})
        tasks = []
        
        # Check if we have all required parameters
        missing_params = []
        if not parameters.get("date"):
            missing_params.append("date")
        if not parameters.get("time"):
            missing_params.append("time")
        
        if missing_params:
            return [Task(
                "request_clarification",
                {"missing": missing_params},
                f"I need more information: {', '.join(missing_params)}"
            )]
        
        # Add tasks for calendar operations
        tasks.append(Task(
            "check_calendar_availability",
            {
                "date": parameters.get("date"),
                "time": parameters.get("time"),
                "duration": parameters.get("duration", "1 hour")
            },
            f"Checking availability on {parameters.get('date')} at {parameters.get('time')}"
        ))
        
        tasks.append(Task(
            "create_calendar_event",
            {
                "date": parameters.get("date"),
                "time": parameters.get("time"),
                "duration": parameters.get("duration", "1 hour"),
                "participants": parameters.get("participants", [])
            },
            f"Creating calendar event on {parameters.get('date')} at {parameters.get('time')}"
        ))
        
        return tasks
    
    def _plan_transaction(self, nlu_result: Dict) -> List[Task]:
        """Plan tasks for transaction intent"""
        parameters = nlu_result.get("parameters", {})
        tasks = []
        
        # Check if we have all required parameters
        missing_params = []
        if not parameters.get("amount"):
            missing_params.append("amount")
        if not parameters.get("recipient"):
            missing_params.append("recipient")
        
        if missing_params:
            return [Task(
                "request_clarification",
                {"missing": missing_params},
                f"I need more information: {', '.join(missing_params)}"
            )]
        
        # Add tasks for transaction
        amount = parameters.get("amount")
        recipient = parameters.get("recipient")
        payment_method = parameters.get("payment_method", "default")
        
        tasks.append(Task(
            "verify_payment_details",
            {
                "amount": amount,
                "recipient": recipient,
                "payment_method": payment_method
            },
            f"Verifying payment details for {amount} to {recipient}"
        ))
        
        tasks.append(Task(
            "confirm_transaction",
            {
                "amount": amount,
                "recipient": recipient,
                "payment_method": payment_method
            },
            f"Confirming payment of {amount} to {recipient}"
        ))
        
        tasks.append(Task(
            "execute_transaction",
            {
                "amount": amount,
                "recipient": recipient,
                "payment_method": payment_method
            },
            f"Sending {amount} to {recipient}"
        ))
        
        return tasks
    
    def _plan_analysis(self, nlu_result: Dict) -> List[Task]:
        """Plan tasks for metrics analysis intent"""
        parameters = nlu_result.get("parameters", {})
        tasks = []
        
        metric = parameters.get("metric")
        time_range = parameters.get("time_range", "last week")
        grouping = parameters.get("grouping")
        
        tasks.append(Task(
            "fetch_analysis_data",
            {
                "metric": metric,
                "time_range": time_range,
                "grouping": grouping
            },
            f"Fetching data for {metric} analysis over {time_range}"
        ))
        
        tasks.append(Task(
            "generate_analysis",
            {
                "metric": metric,
                "time_range": time_range,
                "grouping": grouping
            },
            f"Generating analysis for {metric}"
        ))
        
        tasks.append(Task(
            "present_analysis_results",
            {
                "metric": metric,
                "format": "chart"  # Could be customized based on the request
            },
            f"Presenting {metric} analysis results"
        ))
        
        return tasks