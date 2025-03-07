import assemblyai as aai
from typing import Dict, List, Tuple, Optional
from transformers import pipeline

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
        
        # Define supported intents
        self.supported_intents = {
            "app_switch": ["open", "switch to", "launch", "start"],
            "calendar": ["schedule", "appointment", "meeting", "reminder"],
            "transaction": ["send", "pay", "transfer", "purchase"],
            "analysis": ["analyze", "report", "metrics", "statistics"],
            "media_playback":["play", "pause", "stop", "next", "previous"],
            "timer":["set a timer", "set an alarm"],
            "web_search":["search", "look up", "find"] #add intents for web search
        }
    
    def parse_command(self, text: str) -> Dict:
        """
        Parse a text command into structured intent and entities
        
        Args:
            text: Text command from the Flutter app
            
        Returns:
            Dict containing intent, confidence, entities and parameters
        """
        # Normalize input
        normalized_text = text.lower().strip()
        
        # Detect intent
        intent, confidence = self._detect_intent(normalized_text)
        
        # Extract entities
        entities = self._extract_entities(normalized_text)
        
        # Extract parameters specific to the intent
        parameters = self._extract_parameters(intent, entities, normalized_text)
        
        return {
            "original_text": text,
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "parameters": parameters
        }
    
    def _detect_intent(self, text: str) -> Tuple[str, float]:
        """
        Detect the primary intent from the user's command
        """
        # Simple rule-based intent matching for initial version
        # In production, this would be replaced with a fine-tuned model
        
        for intent, phrases in self.supported_intents.items():
            for phrase in phrases:
                if phrase in text:
                    return intent, 0.85  # Placeholder confidence
        
        # Fallback to transformer model
        predictions = self.intent_classifier(text)
        top_prediction = predictions[0][0]
        
        return top_prediction["label"], top_prediction["score"]
    
    def _extract_entities(self, text: str) -> List[Dict]:
        """
        Extract named entities from the user's command
        """
        entities = self.ner_model(text)
        
        # Additional domain-specific entity extraction
        # (e.g., app names, contact names, etc.)
        # This would be expanded based on the application needs
        
        return entities
    
    def _extract_parameters(self, intent: str, entities: List[Dict], text: str) -> Dict:
        """
        Extract intent-specific parameters from the command
        """
        parameters = {}
        
        if intent == "app_switch":
            # Extract app name
            app_name = self._extract_app_name(text, entities)
            if app_name:
                parameters["app_name"] = app_name
                
        elif intent == "calendar":
            # Extract date, time, duration, participants
            date = self._extract_date(text, entities)
            time = self._extract_time(text, entities)
            duration = self._extract_duration(text, entities)
            participants = self._extract_participants(text, entities)
            
            if date:
                parameters["date"] = date
            if time:
                parameters["time"] = time
            if duration:
                parameters["duration"] = duration
            if participants:
                parameters["participants"] = participants
                
        elif intent == "transaction":
            # Extract amount, recipient, payment method
            amount = self._extract_amount(text, entities)
            recipient = self._extract_recipient(text, entities)
            payment_method = self._extract_payment_method(text, entities)
            
            if amount:
                parameters["amount"] = amount
            if recipient:
                parameters["recipient"] = recipient
            if payment_method:
                parameters["payment_method"] = payment_method
                
        elif intent == "analysis":
            # Extract metric type, time range, grouping
            metric = self._extract_metric(text, entities)
            time_range = self._extract_time_range(text, entities)
            grouping = self._extract_grouping(text, entities)
            
            if metric:
                parameters["metric"] = metric
            if time_range:
                parameters["time_range"] = time_range
            if grouping:
                parameters["grouping"] = grouping
        
        elif intent == "web_search": #extract search queries
                query = text 
                if query:
                    parameters["query"] = query 
        
        return parameters
    
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
    while True:
        text_command = input("Enter a command (or 'exit' to quit): ")
        if text_command.lower() == 'exit':
            break 
        
        parsed_result = nlu_module.parse_command(text_command)
        print("Parsed Result:", parsed_result) 

        #Now use the 'parsed_result' in your Flutter app. 
        # You can send this data to your Flutter app. 
