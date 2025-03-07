import speech_recognition as sr
import assemblyai as aai
from typing import Dict, List, Tuple, Optional
from transformers import pipeline

# Your AssemblyAI API key
# In your settings.py or config file:
AAI_API_KEY = "bf0c580ca5c74eb6a07cbca2ad2dc0ee"  # Replace placeholder

class NLUModule:
    """
    Natural Language Understanding Module for interpreting user commands
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
            "analysis": ["analyze", "report", "metrics", "statistics"]
        }
    
    def parse_command(self, text: str) -> Dict:
        """
        Parse a natural language command into structured intent and entities
        
        Args:
            text: User's natural language input
            
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

class VoiceCommandProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.nlu_module = NLUModule()  

    def process_command(self):
        with sr.Microphone() as source:
            print("Say something:")
            audio = self.recognizer.listen(source)

            try:
                # Use AssemblyAI for speech-to-text
                print("Sending audio to AssemblyAI...")
                audio_data = audio.get_wav_data()
                transcript = self._transcribe_with_assemblyai(audio_data)

                if transcript:
                    print("You said:", transcript)
                    return self.nlu_module.parse_command(transcript)
                else:
                    print("No transcript received from AssemblyAI.")
                    return {"error": "No transcript"}

            except sr.UnknownValueError:
                print("Could not understand audio")
                return {"error": "Audio unclear"}
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                return {"error": "Speech recognition service error"}
            except Exception as e:
                print(f"Error during transcription: {e}")
                return {"error": "Transcription error"}

    def _transcribe_with_assemblyai(self, audio_data):
        """Transcribes audio using the AssemblyAI API."""
        try:
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(audio_data)
            return transcript.text 
        except Exception as e:
            print(f"Error transcribing with AssemblyAI: {e}")
            return None 

if __name__ == "__main__":
    processor = VoiceCommandProcessor()
    while True:
        parsed_result = processor.process_command()
        if 'error' not in parsed_result:
            print("Parsed Result:", parsed_result)
            
            # Command handling logic
            intent = parsed_result.get("intent")
            parameters = parsed_result.get("parameters", {})
            
            # Application switching
            if intent == "app_switch":
                app_name = parameters.get("app_name", "").lower()
                if app_name:
                    print(f"Opening {app_name}...")
                    # Cross-platform app opening
                    import os
                    import platform
                    
                    system = platform.system()
                    if system == "Windows":
                        os.system(f"start {app_name}")
                    elif system == "Darwin":  # macOS
                        os.system(f"open -a '{app_name}'")
                    elif system == "Linux":
                        os.system(f"{app_name} &")
                    print(f"Attempted to open {app_name}")
            
            # Calendar operations
            elif intent == "calendar":
                action = parameters.get("action")
                date = parameters.get("date")
                event = parameters.get("event")
                
                # Import calendar integration library
                try:
                    import calendar_utils  # You'd need to create this module
                    
                    if action == "add" and date and event:
                        calendar_utils.add_event(date, event)
                        print(f"Added event '{event}' on {date}")
                    elif action == "check" and date:
                        events = calendar_utils.get_events(date)
                        if events:
                            print(f"Events on {date}:")
                            for evt in events:
                                print(f"- {evt}")
                        else:
                            print(f"No events scheduled for {date}")
                except ImportError:
                    print("Calendar functionality not available. Missing calendar_utils module.")
            
            # Weather information
            elif intent == "weather":
                location = parameters.get("location", "current")
                date = parameters.get("date", "today")
                
                try:
                    import requests
                    
                    # You would need to sign up for a weather API key
                    API_KEY = "YOUR_WEATHER_API_KEY"
                    
                    if location.lower() == "current":
                        # Get user's location based on IP (simplified)
                        ip_response = requests.get("https://ipinfo.io/json")
                        ip_data = ip_response.json()
                        location = ip_data.get("city", "")
                    
                    # Make API request to weather service
                    weather_url = f"https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={location}&days=3"
                    response = requests.get(weather_url)
                    
                    if response.status_code == 200:
                        weather_data = response.json()
                        if date.lower() == "today":
                            temp = weather_data["current"]["temp_c"]
                            condition = weather_data["current"]["condition"]["text"]
                            print(f"Weather in {location}: {condition}, {temp}°C")
                        else:
                            print(f"Weather forecast for {location} on {date} is not implemented yet")
                    else:
                        print(f"Could not retrieve weather information. Error: {response.status_code}")
                except Exception as e:
                    print(f"Weather functionality error: {str(e)}")
            
            # Music or media playback
            elif intent == "media_playback":
                action = parameters.get("action")
                song = parameters.get("song")
                artist = parameters.get("artist")
                
                try:
                    # This would integrate with your preferred music service
                    import media_player  # You'd need to create this module
                    
                    if action == "play" and song:
                        media_player.play(song=song, artist=artist)
                        if artist:
                            print(f"Playing '{song}' by {artist}")
                        else:
                            print(f"Playing '{song}'")
                    elif action == "pause":
                        media_player.pause()
                        print("Paused playback")
                    elif action == "stop":
                        media_player.stop()
                        print("Stopped playback")
                    elif action == "next":
                        media_player.next_track()
                        print("Playing next track")
                    elif action == "previous":
                        media_player.previous_track()
                        print("Playing previous track")
                except ImportError:
                    print("Media playback not available. Missing media_player module.")
            
            # Set timers or alarms
            elif intent == "timer":
                action = parameters.get("action")
                duration = parameters.get("duration")  # in seconds
                
                import threading
                import time
                
                def timer_done(duration_str):
                    print(f"\nTimer for {duration_str} is done!")
                    # Add sound notification here
                
                if action == "set" and duration:
                    duration_str = str(duration)
                    try:
                        # Convert human-readable duration to seconds
                        import re
                        
                        seconds = 0
                        if isinstance(duration, str):
                            # Parse strings like "2 hours 30 minutes"
                            hours = re.search(r'(\d+)\s*hour', duration)
                            minutes = re.search(r'(\d+)\s*minute', duration)
                            secs = re.search(r'(\d+)\s*second', duration)
                            
                            if hours:
                                seconds += int(hours.group(1)) * 3600
                            if minutes:
                                seconds += int(minutes.group(1)) * 60
                            if secs:
                                seconds += int(secs.group(1))
                        else:
                            seconds = int(duration)
                        
                        print(f"Setting timer for {duration_str}")
                        timer_thread = threading.Thread(target=lambda: (time.sleep(seconds), timer_done(duration_str)))
                        timer_thread.daemon = True
                        timer_thread.start()
                    except Exception as e:
                        print(f"Failed to set timer: {str(e)}")
            
            # Web search
            elif intent == "web_search":
                query = parameters.get("query")
                
                if query:
                    import webbrowser
                    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                    webbrowser.open(search_url)
                    print(f"Searching the web for: {query}")
            
            # Unknown intent
            else:
                print(f"Unknown intent: {intent}. I don't know how to handle this request.")
        
        else:
            print("Error processing command:", parsed_result.get("error"))
        
        # Optional: add a way to exit the loop
        print("Say another command or say 'exit' to quit")
