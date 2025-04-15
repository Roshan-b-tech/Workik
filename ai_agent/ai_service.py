from typing import List, Dict, Any
from openai import OpenAI
import os
from pydantic import BaseModel
from dotenv import load_dotenv
import json

class AIService:
    def __init__(self, api_key: str = None, base_url: str = None):
        # Load environment variables
        load_dotenv()
        
        # Use provided values or fall back to environment variables
        self.api_key = api_key or os.getenv("NETMIND_API_KEY")
        self.base_url = base_url or os.getenv("NETMIND_BASE_URL")
        
        if not self.api_key:
            raise ValueError("API key is required. Set it in .env file or pass it to the constructor.")
        
        if not self.base_url:
            raise ValueError("Base URL is required. Set it in .env file or pass it to the constructor.")
        
        # Initialize the OpenAI client
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

    def generate_plan(self, task: str) -> List[Dict[str, Any]]:
        """Generate a plan for the given task using AI"""
        try:
            response = self.client.chat.completions.create(
                model="meta-llama/Llama-4-Maverick-17B-128E-Instruct",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a task planning AI. 
                        Generate a step-by-step plan to accomplish the given task.
                        Each step should be either a command to run or code to execute.
                        Format your response as a JSON array of steps, where each step has:
                        - type: either "command" or "code"
                        - description: what this step does
                        - command/code: the actual command or code to execute"""
                    },
                    {"role": "user", "content": task}
                ],
                max_tokens=512,
                temperature=0.7
            )
            
            # Extract the content from the response
            content = response.choices[0].message.content
            print(f"AI Response: {content}")
            
            # Try to parse the content as JSON
            try:
                # Look for JSON array in the content
                import re
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    plan_json = json_match.group(0)
                    plan = json.loads(plan_json)
                    return plan
                else:
                    print("No JSON array found in the response")
                    return self._get_default_plan(task)
            except json.JSONDecodeError:
                print("Failed to parse JSON from AI response")
                return self._get_default_plan(task)
                
        except Exception as e:
            print(f"Error generating plan: {str(e)}")
            return self._get_default_plan(task)
    
    def _get_default_plan(self, task):
        """Return a default plan when AI plan generation fails"""
        print("Using default plan")
        return [
            {
                "type": "command",
                "description": "Create a new Python file",
                "command": "echo 'print(\"Hello, World!\")' > hello.py"
            },
            {
                "type": "code",
                "description": "Run the Python file",
                "code": "import subprocess\nsubprocess.run(['python', 'hello.py'])"
            }
        ]

    def refine_plan(self, task: str, failure_reason: str) -> List[Dict[str, Any]]:
        """Refine the plan based on failure feedback"""
        try:
            response = self.client.chat.completions.create(
                model="meta-llama/Llama-4-Maverick-17B-128E-Instruct",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a task planning AI.
                        The previous attempt to complete the task failed.
                        Generate a refined plan taking into account the failure reason.
                        Format your response as a JSON array of steps."""
                    },
                    {"role": "user", "content": f"Task: {task}\nFailure reason: {failure_reason}"}
                ],
                max_tokens=512,
                temperature=0.7
            )
            
            # Extract the content from the response
            content = response.choices[0].message.content
            print(f"AI Response: {content}")
            
            # Try to parse the content as JSON
            try:
                # Look for JSON array in the content
                import re
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    plan_json = json_match.group(0)
                    plan = json.loads(plan_json)
                    return plan
                else:
                    print("No JSON array found in the response")
                    return self._get_default_plan(task)
            except json.JSONDecodeError:
                print("Failed to parse JSON from AI response")
                return self._get_default_plan(task)
                
        except Exception as e:
            print(f"Error refining plan: {str(e)}")
            return self._get_default_plan(task) 