import re
import json
import requests
from datetime import datetime
import dateparser
from typing import Optional

OLLAMA_URL = "http://localhost:11434/api/generate"

def safe_parse(raw: str) -> dict:
    raw = re.sub(r"```json|```", "", raw).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"tasks": []}

def call_ollama(user_input: str) -> dict:
    prompt = f"""You are a task extraction assistant. Extract structured data from user input. Return ONLY valid JSON. No explanation. No markdown. No extra text. Format: {{"tasks": [{{"title": "short task title", "due_date": "natural language date or null"}}]}} Rules: - Keep titles short (3-6 words max) - Only extract actionable tasks - If no tasks found, return {{"tasks": []}} - Do not hallucinate tasks not mentioned User input: "{user_input}" """
    try:
        response = requests.post(OLLAMA_URL, json={"model": "llama3.2", "prompt": prompt}, timeout=30)
        if response.status_code == 200:
            # Ollama returns NDJSON (newline-delimited JSON) streaming responses
            full_response = ""
            for line in response.text.strip().split('\n'):
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        if 'response' in data:
                            full_response += data['response']
                    except json.JSONDecodeError:
                        continue
            return safe_parse(full_response)
    except Exception:
        pass
    return {"tasks": []}

TASK_PATTERNS = [
    r"\b(finish|complete|submit|do|study|prepare|fix|build|write|review)\b.{3,40}",
    r"\b\w+\s+(test|exam|assignment|meeting|deadline|due)\b",
]

def rule_based_extract(text: str) -> list[dict]:
    tasks = []
    for pattern in TASK_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            tasks.append({"title": match.strip(), "due_date": None})
    return tasks

def resolve_date(raw: str | None) -> Optional[datetime]:
    if not raw:
        return None
    parsed = dateparser.parse(raw, settings={"PREFER_DATES_FROM": "future"})
    return parsed

def extract_tasks(user_input: str) -> list[dict]:
    result = call_ollama(user_input)
    if not result.get("tasks"):
        result = {"tasks": rule_based_extract(user_input)}
    resolved_tasks = []
    for task in result.get("tasks", []):
        resolved_tasks.append({
            "title": task["title"],
            "due_date": resolve_date(task.get("due_date"))
        })
    return resolved_tasks