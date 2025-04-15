import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
import subprocess
import json
import platform

def execute_command(command):
    """Execute a command and return the output"""
    try:
        # Convert Unix commands to Windows commands if needed
        if platform.system() == 'Windows':
            if command.startswith('chmod'):
                return "", "", 0  # Skip chmod on Windows
            if command.startswith('./'):
                command = command[2:]  # Remove ./ prefix
            if command.startswith('python'):
                command = 'python ' + command[7:]  # Ensure proper spacing
            
            # Handle paths with spaces in Windows
            if '&&' in command:
                # Split the command into parts
                parts = command.split('&&')
                results = []
                for part in parts:
                    part = part.strip()
                    # If the part contains a path with spaces, wrap it in quotes
                    if ' ' in part and not (part.startswith('"') and part.endswith('"')):
                        # Find the executable and its arguments
                        exe_parts = part.split()
                        exe = exe_parts[0]
                        args = exe_parts[1:]
                        # Wrap the executable path in quotes if it contains spaces
                        if ' ' in exe and not (exe.startswith('"') and exe.endswith('"')):
                            exe = f'"{exe}"'
                        # Reconstruct the command
                        part = f'{exe} {" ".join(args)}'
                    results.append(part)
                command = ' && '.join(results)
        
        print(f"\nExecuting command: {command}")
        print("(If the command requires input, please enter it below)")
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True, input="5\n")  # Default input of 5
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def execute_code(code):
    """Execute Python code and return the output"""
    try:
        # Create a temporary file to execute the code
        with open("temp_execution.py", "w") as f:
            f.write(code)
        
        # Execute the temporary file
        result = subprocess.run(["python", "temp_execution.py"], capture_output=True, text=True)
        
        # Clean up
        os.remove("temp_execution.py")
        
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def get_user_approval(plan):
    """Ask the user to approve the plan"""
    print("\nGenerated Plan:")
    print(json.dumps(plan, indent=2))
    
    while True:
        approval = input("\nDo you want to execute this plan? (yes/no): ").lower()
        if approval in ["yes", "y"]:
            return True
        elif approval in ["no", "n"]:
            return False
        else:
            print("Please enter 'yes' or 'no'")

def check_task_success():
    """Ask the user if the task was successful"""
    while True:
        success = input("\nWas the task successful? (yes/no): ").lower()
        if success in ["yes", "y"]:
            return True, None
        elif success in ["no", "n"]:
            reason = input("What was the issue? ")
            return False, reason
        else:
            print("Please enter 'yes' or 'no'")

def execute_plan(plan):
    """Execute the plan and return success status"""
    for step in plan:
        print(f"\nExecuting: {step['description']}")
        
        # Get the command/code from either key
        command = step.get("command/code") or step.get("command")
        if not command:
            print(f"Error: No command found in step")
            return False
        
        if step["type"] == "command":
            stdout, stderr, returncode = execute_command(command)
        elif step["type"] == "code":
            stdout, stderr, returncode = execute_code(command)
        else:
            print(f"Unknown step type: {step['type']}")
            continue
        
        if returncode != 0:
            print(f"Error: {stderr}")
            return False
        elif stdout:
            print(f"Output: {stdout}")
    
    return True

def main():
    # Load environment variables
    load_dotenv()
    
    # Get API key and base URL from environment
    api_key = os.getenv("NETMIND_API_KEY")
    base_url = os.getenv("NETMIND_BASE_URL")
    
    if not api_key or not base_url:
        print("Error: NETMIND_API_KEY and NETMIND_BASE_URL must be set in .env file")
        return
    
    # Initialize the OpenAI client
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    # Get the task from command line arguments or prompt
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = input("Enter your task: ")
    
    print(f"\nTask: {task}")
    
    # Generate and execute plans until successful
    attempt = 1
    while True:
        print(f"\nAttempt {attempt}:")
        
        # Generate a plan
        response = client.chat.completions.create(
            model="meta-llama/Llama-4-Maverick-17B-128E-Instruct",
            messages=[
                {
                    "role": "system",
                    "content": """You are a task planning AI. 
                    Generate a step-by-step plan to accomplish the given task.
                    Each step should be either a command to run or code to execute.
                    Your response MUST be a valid JSON array of steps, where each step has:
                    {
                        "type": "command" or "code",
                        "description": "what this step does",
                        "command/code": "the actual command or code to execute"
                    }
                    
                    For code type steps, use Python's file operations:
                    with open(filename, "w") as f: f.write(content)
                    
                    For command type steps, use appropriate shell commands.
                    
                    DO NOT include any explanatory text outside the JSON array.
                    DO NOT include any additional formatting or indentation."""
                },
                {"role": "user", "content": task}
            ],
            max_tokens=512,
            temperature=0.7
        )
        
        # Parse the plan
        content = response.choices[0].message.content.strip()
        try:
            # Look for JSON array in the content, strip any non-JSON content
            content = content.strip()
            if not content.startswith('['):
                # Find the first '[' and last ']'
                start = content.find('[')
                end = content.rfind(']') + 1
                if start != -1 and end != 0:
                    content = content[start:end]
            
            # Clean the content of any invalid control characters
            content = ''.join(char for char in content if ord(char) >= 32 or char in '\n\r\t')
            
            plan = json.loads(content)
            if not isinstance(plan, list):
                raise ValueError("Response is not a JSON array")
                
            # Validate each step has required fields
            for step in plan:
                if not all(key in step for key in ["type", "description", "command/code"]):
                    raise ValueError("Step missing required fields")
                if step["type"] not in ["command", "code"]:
                    raise ValueError(f"Invalid step type: {step['type']}")
                    
        except Exception as e:
            print(f"Failed to parse AI response: {str(e)}")
            print("Retrying with a more specific prompt...")
            
            # Retry with a more specific prompt
            response = client.chat.completions.create(
                model="meta-llama/Llama-4-Maverick-17B-128E-Instruct",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a task planning AI. Generate a plan as a JSON array. Each step must have type, description, and command/code fields. Use Python's file operations for code steps."
                    },
                    {"role": "user", "content": f"Create a plan for: {task}"}
                ],
                max_tokens=512,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            try:
                plan = json.loads(content)
            except:
                print("AI is having trouble generating a valid plan. Please try rephrasing your request.")
                return
        
        # Get user approval
        if not get_user_approval(plan):
            print("Plan rejected. Exiting.")
            return
        
        # Execute the plan
        execute_plan(plan)
        
        # Check if the task was successful
        success, reason = check_task_success()
        if success:
            print("\nTask completed successfully!")
            return
        
        # If not successful, refine the plan
        print("\nRefining the plan...")
        task = f"Task: {task}\nFailure reason: {reason}"
        attempt += 1

if __name__ == "__main__":
    main() 