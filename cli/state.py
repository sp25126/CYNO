import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

STATE_FILE = Path("data/cli_state.json")

@dataclass
class UserState:
    resume_data: Optional[Dict[str, Any]] = None
    resume_text: Optional[str] = None
    resume_path: Optional[str] = None
    last_job_query: Optional[str] = None
    ngrok_url: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)

class StateManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateManager, cls).__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        """Load state from disk"""
        self.state = UserState()
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r") as f:
                    data = json.load(f)
                    self.state = UserState(**data)
            except Exception as e:
                print(f"[warning] Failed to load state: {e}[/warning]")

    def save(self):
        """Persist state to disk"""
        STATE_FILE.parent.mkdir(exist_ok=True, parents=True)
        with open(STATE_FILE, "w") as f:
            json.dump(self.state.to_dict(), f, indent=2, default=str)

    def set_resume(self, path: str, text: str, data: Dict[str, Any]):
        self.state.resume_path = path
        self.state.resume_text = text
        self.state.resume_data = data
        self.save()

    def get_resume(self) -> Optional[Dict[str, Any]]:
        return self.state.resume_data
        
    def get_resume_text(self) -> Optional[str]:
        return self.state.resume_text

    def set_ngrok(self, url: str):
        self.state.ngrok_url = url
        self.save()

# Global Instance
state = StateManager()
