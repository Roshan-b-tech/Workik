import os
from dotenv import load_dotenv
from openai import OpenAI

def test_netmind_api():
    # Load environment variables
    load_dotenv()
    
    # Get API key and base URL from environment
    api_key = os.getenv("NETMIND_API_KEY")
    base_url = os.getenv("NETMIND_BASE_URL")
    
    if not api_key or not base_url:
        print("Error: NETMIND_API_KEY and NETMIND_BASE_URL must be set in .env file")
        return
    
    print(f"Testing NetMind AI API with base URL: {base_url}")
    
    try:
        # Initialize the OpenAI client
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # Test task
        test_task = "Create a simple Python script that prints 'Hello, World!'"
        print(f"\nTesting task: {test_task}")
        
        # Generate a plan
        response = client.chat.completions.create(
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
                {"role": "user", "content": test_task}
            ],
            max_tokens=512,
            temperature=0.7
        )
        
        # Print the response
        print("\nGenerated plan:")
        print(response.choices[0].message.content)
        
        print("\nAPI test completed successfully!")
        
    except Exception as e:
        print(f"Error testing API: {str(e)}")

if __name__ == "__main__":
    test_netmind_api() 