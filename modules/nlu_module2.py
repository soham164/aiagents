import assemblyai as aai
from typing import Dict, List, Tuple, Optional
from transformers import pipeline
from datetime import datetime, timedelta
import re
import uuid
import json

# Your AssemblyAI API key (Not used here, but keep for reference)
# In your settings.py or config file:
AAI_API_KEY = "bf0c580ca5c74eb6a07cbca2ad2dc0ee"  # Replace placeholder

class NLUModule:
    """
    Natural Language Understanding Module for interpreting text commands
    from a Flutter app.
    """
    def __init__(self):
        # Load intent classification model
        self.intent_classifier = pipeline(
            "text-classification",
            model="distilbert-base-uncased-finetuned-sst-2-english",  # Placeholder model
            top_k=3
        )
        
        # Load named entity recognition model
        self.ner_model = pipeline(
            "ner",
            model="dbmdz/bert-large-cased-finetuned-conll03-english",  # Placeholder model
            aggregation_strategy="simple"
        )
        
        # Define regular expression patterns for intents
        self.patterns = {
            "youtube_search": re.compile(
                r'^(?:open\s+youtube\s+and\s+search|search\s+(?:on|in)\s+youtube\s+for|youtube\s+search)(?:\s+for)?\s+(.+)$',
                re.IGNORECASE
            ),
            "youtube_open": re.compile(
                r'^open\s+youtube$',
                re.IGNORECASE
            ),
            "calendar_open": re.compile(
                r'^open\s+(?:my\s+)?calendar$',
                re.IGNORECASE
            ),
            "add_event": re.compile(
                r'^(?:add|create|schedule)(?:\s+a)?(?:\s+new)?(?:\s+meeting|event|appointment)(?:\s+(?:on|in|to)(?:\s+my)?(?:\s+calendar))?\s+(.+)$',
                re.IGNORECASE
            ),
            "view_date": re.compile(
                r'^(?:show|view|open|check)(?:\s+my)?(?:\s+calendar)(?:\s+for)?\s+(.+)$',
                re.IGNORECASE
            ),
            "maps_open": re.compile(
                r'^open\s+(?:google\s+)?maps$',
                re.IGNORECASE
            ),
            "gmail_open": re.compile(
                r'^open\s+gmail$',
                re.IGNORECASE
            ),
            "settings_open": re.compile(
                r'^open\s+settings$',
                re.IGNORECASE
            ),
            "camera_open": re.compile(
                r'^open\s+camera$',
                re.IGNORECASE
            ),
            "gallery_open": re.compile(
                r'^open\s+(?:gallery|photos)$',
                re.IGNORECASE
            )
        }
        
        # Map pattern keys to intent types
        self.pattern_to_intent = {
            "youtube_search": "web_search",
            "youtube_open": "app_switch",
            "calendar_open": "app_switch",
            "add_event": "calendar",
            "view_date": "calendar",
            "maps_open": "app_switch",
            "gmail_open": "app_switch",
            "settings_open": "app_switch",
            "camera_open": "app_switch",
            "gallery_open": "app_switch"
        }
        
        # Define supported intents for fallback detection
        self.supported_intents = {
            "app_switch": ["open", "switch to", "launch", "start"],
            "calendar": ["schedule", "appointment", "meeting", "reminder"],
            "transaction": ["send", "pay", "transfer", "purchase"],
            "analysis": ["analyze", "report", "metrics", "statistics"],
            "media_playback":["play", "pause", "stop", "next", "previous"],
            "timer":["set a timer", "set an alarm"],
            "web_search":["search", "look up", "find"] 
        }
        
        # Define common event types for calendar intent
        self.event_types = ["meeting", "call", "appointment", "event", "reminder", "conference"]
        
        # Define platforms for web search
        self.search_platforms = ["youtube", "google", "bing", "yahoo", "duckduckgo"]
    
    def parse_command(self, text: str) -> Dict:
        """
        Parse a text command into structured intent and entities
        
        Args:
            text: Text command from the Flutter app
            
        Returns:
            Dict containing intent, confidence, entities and parameters
        """
        # Check for pattern matches first
        pattern_match, pattern_key, captured_text = self._check_pattern_match(text)
        
        if pattern_match:
            # Handle according to the matched pattern
            return self._handle_pattern_match(pattern_key, captured_text, text)
        
        # If no pattern match, fall back to the regular NLU pipeline
        # Normalize input
        normalized_text = text.lower().strip()
        
        # Detect intent
        intent, confidence = self._detect_intent(normalized_text)
        
        # Extract entities
        entities = self._extract_entities(normalized_text, intent)
        
        # Extract parameters specific to the intent
        parameters = self._extract_parameters(intent, entities, normalized_text)
        
        # Create the parsed intent structure
        parsed_intent = {
            "original_text": text,
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "parameters": parameters
        }
        
        # Create the full response structure with session_id and tasks
        session_id = str(uuid.uuid4())[:5]
        
        # Generate appropriate tasks based on intent
        tasks = self._generate_tasks(intent, parsed_intent, parameters)
        
        # Generate appropriate message
        message = self._generate_message(tasks)
        
        # Construct the full response
        response = {
            "session_id": session_id,
            "parsed_intent": parsed_intent,
            "tasks": tasks,
            "message": message
        }
        
        return response
    
    def _check_pattern_match(self, text: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if the input text matches any of our defined patterns
        
        Returns:
            Tuple of (matched, pattern_key, captured_text)
        """
        for pattern_key, pattern in self.patterns.items():
            match = pattern.match(text)
            if match:
                # If there's a capture group, get the captured text
                captured_text = match.group(1) if match.lastindex else None
                return True, pattern_key, captured_text
        
        return False, None, None
    
    def _handle_pattern_match(self, pattern_key: str, captured_text: Optional[str], original_text: str) -> Dict:
        """
        Handle a matched pattern based on its type
        """
        intent_type = self.pattern_to_intent.get(pattern_key, "unsupported")
        session_id = str(uuid.uuid4())[:5]
        
        if pattern_key == "youtube_search":
            # Handle YouTube search
            parsed_intent = {
                "original_text": original_text,
                "intent": "web_search",
                "confidence": 0.95,
                "entities": {
                    "platform": "youtube",
                    "query": captured_text
                },
                "parameters": {
                    "platform": "youtube",
                    "query": captured_text
                }
            }
            
            tasks = [{
                "id": str(uuid.uuid4()),
                "action": "search_youtube",
                "params": {
                    "query": captured_text
                },
                "description": f"I'll search YouTube for '{captured_text}'",
                "status": "pending",
                "requires_approval": True,
                "approval_status": "pending",
                "error": None
            }]
            
        elif pattern_key == "youtube_open":
            # Handle open YouTube
            parsed_intent = {
                "original_text": original_text,
                "intent": "app_switch",
                "confidence": 0.95,
                "entities": {
                    "app_name": "youtube"
                },
                "parameters": {
                    "app_name": "youtube"
                }
            }
            
            tasks = [{
                "id": str(uuid.uuid4()),
                "action": "open_app",
                "params": {
                    "app_name": "youtube"
                },
                "description": "I'll open YouTube for you",
                "status": "pending",
                "requires_approval": True,
                "approval_status": "pending",
                "error": None
            }]
            
        elif pattern_key == "add_event":
            # Extract date and participant from the event text
            event_text = captured_text
            
            # Simple extraction for date and participant
            date_match = re.search(r'(today|tomorrow|on \w+)', event_text, re.IGNORECASE)
            date_text = date_match.group(1) if date_match else None
            
            participant_match = re.search(r'with (\w+)', event_text, re.IGNORECASE)
            participant = participant_match.group(1) if participant_match else None
            
            # Determine date object
            date_obj = None
            if date_text == "tomorrow":
                today = datetime.now()
                tomorrow = today + timedelta(days=1)
                date_obj = tomorrow.strftime("%Y-%m-%d")
            elif date_text == "today":
                today = datetime.now()
                date_obj = today.strftime("%Y-%m-%d")
            
            # Determine event type
            event_type = None
            for et in self.event_types:
                if et in original_text.lower():
                    event_type = et
                    break
            
            if not event_type:
                event_type = "meeting"  # Default
            
            parsed_intent = {
                "original_text": original_text,
                "intent": "calendar",
                "confidence": 0.95,
                "entities": {
                    "event_type": event_type,
                    "date": date_text,
                    "participant": participant
                },
                "parameters": {
                    "date": date_obj,
                    "time": None,
                    "duration": None,
                    "participants": [participant] if participant else None,
                    "event_title": event_type
                }
            }
            
            # Check if we need to ask for more info
            if not parsed_intent["parameters"]["time"]:
                tasks = [{
                    "id": str(uuid.uuid4()),
                    "action": "request_clarification",
                    "params": {
                        "missing": ["time"]
                    },
                    "description": "I need more information: time",
                    "status": "pending",
                    "requires_approval": True,
                    "approval_status": "pending",
                    "error": None
                }]
            else:
                tasks = [{
                    "id": str(uuid.uuid4()),
                    "action": "create_calendar_event",
                    "params": parsed_intent["parameters"],
                    "description": f"I'll create a {event_type} in your calendar",
                    "status": "pending",
                    "requires_approval": True,
                    "approval_status": "pending",
                    "error": None
                }]
                
        else:
            # Handle other app opening patterns
            app_name = pattern_key.split("_")[0]  # Extract app name from pattern key
            
            parsed_intent = {
                "original_text": original_text,
                "intent": "app_switch",
                "confidence": 0.95,
                "entities": {
                    "app_name": app_name
                },
                "parameters": {
                    "app_name": app_name
                }
            }
            
            tasks = [{
                "id": str(uuid.uuid4()),
                "action": "open_app",
                "params": {
                    "app_name": app_name
                },
                "description": f"I'll open {app_name} for you",
                "status": "pending",
                "requires_approval": True,
                "approval_status": "pending",
                "error": None
            }]
        
        # Generate message
        message = self._generate_message(tasks)
        
        return {
            "session_id": session_id,
            "parsed_intent": parsed_intent,
            "tasks": tasks,
            "message": message
        }
    
    def _detect_intent(self, text: str) -> Tuple[str, float]:
        """
        Detect the primary intent from the user's command
        """
        # Special handling for web search intent
        if any(phrase in text for phrase in self.supported_intents["web_search"]):
            return "web_search", 0.85
        
        # Simple rule-based intent matching for other intents
        for intent, phrases in self.supported_intents.items():
            for phrase in phrases:
                if phrase in text:
                    # Increase confidence for calendar intent
                    if intent == "calendar":
                        return intent, 0.95  # Match expected confidence
                    return intent, 0.85
        
        # Fallback to transformer model
        predictions = self.intent_classifier(text)
        top_prediction = predictions[0][0]
        
        return top_prediction["label"], top_prediction["score"]
    
    def _extract_entities(self, text: str, intent: str) -> Dict:
        """
        Extract named entities from the user's command
        """
        entities = {}
        
        # Intent-specific entity extraction
        if intent == "calendar":
            # Extract event type
            event_type = None
            for et in self.event_types:
                if et in text:
                    event_type = et
                    break
            
            if event_type:
                entities["event_type"] = event_type
            
            # Extract date
            date = self._extract_date(text, [])
            if date:
                entities["date"] = date
            
            # Extract participants
            participants = self._extract_participants_from_text(text)
            if participants:
                entities["participant"] = participants[0] if participants else None
        
        elif intent == "web_search":
            # Extract search platform
            platform = None
            for p in self.search_platforms:
                if p in text:
                    platform = p
                    break
            
            if platform:
                entities["platform"] = platform
            
            # Extract search query by removing search keywords and platform
            query = text
            for phrase in self.supported_intents["web_search"]:
                query = query.replace(phrase, "").strip()
            
            if platform:
                query = query.replace(f"on {platform}", "").strip()
                query = query.replace(f"in {platform}", "").strip()
            
            if query:
                entities["query"] = query
        
        return entities
    
    def _extract_participants_from_text(self, text: str) -> List[str]:
        """
        Extract participant names from text using common patterns
        """
        participants = []
        
        # Check for "with [name]" pattern
        with_pattern = r'with\s+(\w+)'
        with_matches = re.findall(with_pattern, text)
        participants.extend(with_matches)
        
        return participants
    
    def _extract_parameters(self, intent: str, entities: Dict, text: str) -> Dict:
        """
        Extract intent-specific parameters from the command
        """
        parameters = {}
        
        if intent == "calendar":
            # Extract date, time, duration, participants
            date_text = entities.get("date")
            date_obj = None
            
            # Convert relative date to actual date
            if date_text == "tomorrow":
                today = datetime.now()
                tomorrow = today + timedelta(days=1)
                date_obj = tomorrow.strftime("%Y-%m-%d")
            elif date_text == "today":
                today = datetime.now()
                date_obj = today.strftime("%Y-%m-%d")
            
            # Set parameters
            parameters["date"] = date_obj
            parameters["time"] = None
            parameters["duration"] = None
            
            # Get participants from entities
            participant = entities.get("participant")
            if participant:
                parameters["participants"] = [participant]
            else:
                parameters["participants"] = None
            
            # Set event title from event type
            event_type = entities.get("event_type")
            if event_type:
                parameters["event_title"] = event_type
                
        elif intent == "app_switch":
            # Extract app name
            app_name = self._extract_app_name(text, [])
            if app_name:
                parameters["app_name"] = app_name
                
        elif intent == "transaction":
            # Extract amount, recipient, payment method
            amount = self._extract_amount(text, [])
            recipient = self._extract_recipient(text, [])
            payment_method = self._extract_payment_method(text, [])
            
            if amount:
                parameters["amount"] = amount
            if recipient:
                parameters["recipient"] = recipient
            if payment_method:
                parameters["payment_method"] = payment_method
                
        elif intent == "analysis":
            # Extract metric type, time range, grouping
            metric = self._extract_metric(text, [])
            time_range = self._extract_time_range(text, [])
            grouping = self._extract_grouping(text, [])
            
            if metric:
                parameters["metric"] = metric
            if time_range:
                parameters["time_range"] = time_range
            if grouping:
                parameters["grouping"] = grouping
        
        elif intent == "web_search":
            # For web search, use the refined query if available
            if "query" in entities:
                parameters["query"] = entities["query"]
            else:
                # Remove search keywords to get cleaner query
                query = text
                for phrase in self.supported_intents["web_search"]:
                    query = query.replace(phrase, "").strip()
                parameters["query"] = query
            
            # Add platform if available
            if "platform" in entities:
                parameters["platform"] = entities["platform"]
        
        return parameters
    
    def _generate_tasks(self, intent: str, parsed_intent: Dict, parameters: Dict) -> List[Dict]:
        """
        Generate tasks based on the identified intent and parameters
        """
        tasks = []
        
        if intent == "calendar":
            # Check if we need to ask for more info
            missing_params = []
            if not parameters.get("time"):
                missing_params.append("time")
            
            if missing_params:
                task = {
                    "id": str(uuid.uuid4()),
                    "action": "request_clarification",
                    "params": {
                        "missing": missing_params
                    },
                    "description": f"I need more information: {', '.join(missing_params)}",
                    "status": "pending",
                    "requires_approval": True,
                    "approval_status": "pending",
                    "error": None
                }
                tasks.append(task)
            else:
                # If we have all info, create a calendar event
                task = {
                    "id": str(uuid.uuid4()),
                    "action": "create_calendar_event",
                    "params": parameters,
                    "description": "I'll create that calendar event for you",
                    "status": "pending",
                    "requires_approval": True,
                    "approval_status": "pending",
                    "error": None
                }
                tasks.append(task)
        
        elif intent == "web_search":
            # For web search, create a search task
            search_action = "search_web"
            
            # If a specific platform is mentioned, use platform-specific action
            if "platform" in parameters:
                platform = parameters["platform"]
                if platform == "youtube":
                    search_action = "search_youtube"
            
            task = {
                "id": str(uuid.uuid4()),
                "action": search_action,
                "params": parameters,
                "description": f"I'll search for that information for you",
                "status": "pending",
                "requires_approval": True,
                "approval_status": "pending",
                "error": None
            }
            tasks.append(task)
        
        else:
            # Default for unsupported intents
            task = {
                "id": str(uuid.uuid4()),
                "action": "unsupported_intent",
                "params": {
                    "original_text": parsed_intent["original_text"]
                },
                "description": "I'm not sure how to handle this request yet.",
                "status": "pending",
                "requires_approval": True,
                "approval_status": "pending",
                "error": None
            }
            tasks.append(task)
        
        return tasks
    
    def _generate_message(self, tasks: List[Dict]) -> str:
        """
        Generate a user-friendly message based on the tasks
        """
        if not tasks:
            return "I'm not sure how to help with that."
            
        message = "I'll help you with that. Here's what I'll do:\n"
        
        for task in tasks:
            message += f"- {task['description']}"
        
        return message
    
    # Parameter extraction helper methods
    def _extract_app_name(self, text: str, entities: List[Dict]) -> Optional[str]:
        # Simplified for demo - would use more sophisticated matching in production
        common_apps = ["calendar", "email", "messages", "maps", "photos", "camera", 
                       "weather", "notes", "reminders", "clock", "calculator"]
        
        for app in common_apps:
            if app in text:
                return app
        
        return None
    
    def _extract_date(self, text: str, entities: List[Dict]) -> Optional[str]:
        # Simple date extraction - would use a date parser in production
        if "tomorrow" in text:
            return "tomorrow"
        elif "today" in text:
            return "today"
        # Would extract more complex dates in production
        
        return None
    
    def _extract_time(self, text: str, entities: List[Dict]) -> Optional[str]:
        # Would implement time extraction logic
        return None
    
    def _extract_duration(self, text: str, entities: List[Dict]) -> Optional[str]:
        # Would implement duration extraction logic
        return None
    
    def _extract_participants(self, text: str, entities: List[Dict]) -> Optional[List[str]]:
        # Would implement participant extraction logic
        return None
    
    def _extract_amount(self, text: str, entities: List[Dict]) -> Optional[float]:
        # Simple amount extraction for demo
        import re
        amount_patterns = [
            r'\$(\d+(?:\.\d+)?)',  # $50 or $50.25
            r'(\d+(?:\.\d+)?) dollars',  # 50 dollars or 50.25 dollars
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text)
            if match:
                return float(match.group(1))
        
        return None
    
    def _extract_recipient(self, text: str, entities: List[Dict]) -> Optional[str]:
        # Would implement recipient extraction logic
        return None
    
    def _extract_payment_method(self, text: str, entities: List[Dict]) -> Optional[str]:
        # Would implement payment method extraction logic
        return None
    
    def _extract_metric(self, text: str, entities: List[Dict]) -> Optional[str]:
        # Would implement metric extraction logic
        return None
    
    def _extract_time_range(self, text: str, entities: List[Dict]) -> Optional[Dict]:
        # Would implement time range extraction logic
        return None
    
    def _extract_grouping(self, text: str, entities: List[Dict]) -> Optional[str]:
        # Would implement grouping extraction logic
        return None


if __name__ == "__main__":
    nlu_module = NLUModule() 
    
    # Interactive mode
    while True:
        text_command = input("\nEnter a command (or 'exit' to quit): ")
        if text_command.lower() == 'exit':
            break 
        
        parsed_result = nlu_module.parse_command(text_command)
        print(json.dumps(parsed_result, indent=2))
