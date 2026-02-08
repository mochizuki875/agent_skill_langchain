from pathlib import Path
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain.tools import tool
import subprocess
import os
from typing import Optional, List, Dict
import yaml

# Application run name
RUN_NAME="agent_skill"

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize LLM Model based on provider
# LLM Provider Selection (set via environment variable or default to ollama)
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-oss:20b")
MODEL_BASE_URL = os.getenv("MODEL_BASE_URL", "http://127.0.0.1:11434")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
if LLM_PROVIDER == "ollama":
    model = ChatOllama(
        model=MODEL_NAME,
        base_url=MODEL_BASE_URL
    )
    print(f"Using Ollama: {MODEL_NAME} at {MODEL_BASE_URL}")
else:
    raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}. Use 'ollama'.")

# Base agent system prompt (will be enhanced with skill information)
BASE_SYSTEM_PROMPT = "You are a helpful assistant."

# Skills directory path
SKILLS_DIR = Path(__file__).parent / "SKILLS"

# Skill Management
def discover_skills() -> Dict[str, Dict[str, str]]:
    """
    Discover all available skills from SKILLS directory.
    
    Returns:
        Dictionary mapping skill names to their metadata (name, description, path)
    """
    skills = {}
    
    if not SKILLS_DIR.exists():
        return skills
    
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
            
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        
        # Parse SKILL.md frontmatter
        try:
            content = skill_md.read_text(encoding='utf-8')
            # Parse YAML frontmatter (between --- markers)
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    # Use YAML parser for proper frontmatter parsing
                    frontmatter_text = parts[1].strip()
                    metadata = yaml.safe_load(frontmatter_text) or {}
                    
                    skill_name = metadata.get('name', skill_dir.name)
                    scripts_dir = skill_dir / "scripts"
                    skills[skill_name] = {
                        'name': skill_name,
                        'description': metadata.get('description', ''),
                        'path': str(skill_dir),
                        'scripts_path': str(scripts_dir) if scripts_dir.exists() else None,
                        'content': parts[2].strip()
                    }
        except Exception as e:
            print(f"Warning: Failed to parse skill {skill_dir.name}: {e}")
    
    return skills


# Load available skills at module level
AVAILABLE_SKILLS = discover_skills()

# Build system prompt with skill awareness
SYSTEM_PROMPT = BASE_SYSTEM_PROMPT
if AVAILABLE_SKILLS:
    SYSTEM_PROMPT += "\n\nYou have access to specialized skills:\n"
    for name, info in AVAILABLE_SKILLS.items():
        SYSTEM_PROMPT += f"  - {name}: {info['description']}\n"
    SYSTEM_PROMPT += "\nUse the load_skill tool to load a skill when you need specialized knowledge or capabilities for these tasks."


# Tool Definitions
@tool
def load_skill(skill_name: str) -> str:
    """
    Load a specialized skill with its full context and instructions.
    
    Available skills:
    {skill_list}
    
    Args:
        skill_name: Name of the skill to load
        
    Returns:
        The skill's full documentation including usage instructions
    """
    if skill_name not in AVAILABLE_SKILLS:
        available = ', '.join(AVAILABLE_SKILLS.keys())
        return f"Error: Skill '{skill_name}' not found. Available skills: {available}"
    
    skill = AVAILABLE_SKILLS[skill_name]
    
    # Build skill output
    output = f"""# Skill: {skill['name']}

{skill['content']}

---
**Important Notes:**
- Script paths are relative to project root: `SKILLS/<skill-name>/scripts/<script>.py`
- Execute using: `SKILLS/<skill-name>/scripts/<script>.py <args>`
- The `output` directory is at project root level (same directory as main.py)
- When reading files in `output/`, use: `output/filename.md` (relative to project root)
"""
    
    return output

# Update load_skill tool docstring with actual skills
if AVAILABLE_SKILLS:
    skill_list = '\n    '.join([
        f"- {name}: {info['description']}"
        for name, info in AVAILABLE_SKILLS.items()
    ])
    load_skill.__doc__ = load_skill.__doc__.format(skill_list=skill_list)
else:
    load_skill.__doc__ = load_skill.__doc__.format(skill_list="    (No skills found)")


@tool
def execute_command(command_path: str, command_args: Optional[List[str]] = None) -> str:
    """
    Execute a command or script file with optional arguments and return its output.
    Supports shell scripts (.sh), Python scripts (.py), and other executable files.
    
    IMPORTANT: Use direct commands like 'cat', 'ls', 'mkdir' as command_path.
    Do NOT use shell names like 'sh', 'bash' as command_path.
    
    Args:
        command_path: Path to the command or script file to execute (absolute or relative path)
                     Examples: 'cat', 'ls', 'mkdir', 'SKILLS/skill-name/scripts/script.py'
        command_args: Optional list of command-line arguments to pass to the command
        
    Returns:
        String containing the command's stdout/stderr output
    """
    # Check if command_path is a system command or a file path
    # System commands: no path separators (e.g., 'cat', 'ls', 'mkdir')
    # Exclude shell names from being treated as system commands
    is_system_command = (os.path.sep not in command_path and not command_path.startswith('.'))
    
    if is_system_command:
        # It's a system command - execute with /bin/bash -c for proper shell interpretation
        if command_args:
            # Combine command and args into a single shell command string
            full_command = command_path + ' ' + ' '.join(command_args)
            command = ['/bin/bash', '-c', full_command]
        else:
            command = ['/bin/bash', '-c', command_path]
    else:
        # It's a file path - convert relative path to absolute path
        abs_path = os.path.abspath(command_path)
        
        # Validate file exists
        if not os.path.exists(abs_path):
            return f"Error: File not found: {abs_path}"
        
        # Validate file is executable or is a known script type
        if not os.access(abs_path, os.X_OK):
            # If not executable, check if it's a known script type
            if not (abs_path.endswith('.sh') or abs_path.endswith('.py')):
                return f"Error: File is not executable and not a recognized script type: {abs_path}"
        
        # Build command with arguments
        # For .py files, use python explicitly
        # For .sh files, use bash explicitly
        if abs_path.endswith('.py'):
            command = ['python', abs_path]
        elif abs_path.endswith('.sh'):
            command = ['bash', abs_path]
        else:
            command = [abs_path]
        
        if command_args:
            command.extend(command_args)
    
    try:
        # Execute the command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        # Combine stdout and stderr
        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        if result.returncode != 0:
            output += f"\nExit code: {result.returncode}"
            
        return output if output else "Command executed successfully with no output."
        
    except subprocess.TimeoutExpired:
        return f"Error: Command execution timed out after 30 seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"


def display_tools(tools):
    """
    Display available tools and their arguments.
    
    This function prints tool information that will be sent to the model
    in the system prompt, allowing the model to understand what tools
    are available and how to use them.
    
    Args:
        tools: List of tool objects to display
    """
    print("Available Tools:")
    for t in tools:
        print(f"  - Name: {t.name}")
        print(f"    Description: {t.description}")
        # Display tool arguments if available
        if hasattr(t, 'args') and t.args:
            print(f"    Arguments:")
            for arg_name, arg_info in t.args.items():
                arg_type = arg_info.get('type', 'unknown')
                arg_desc = arg_info.get('description', '')
                print(f"      - {arg_name} ({arg_type}): {arg_desc}")
        print()


def get_tools():
    """
    Return all available tools.
    
    Returns:
        List of all available tools
    """
    return [load_skill, execute_command]


def run_agent_loop(agent):
    """
    Run the interactive agent conversation loop.
    
    This function:
    1. Maintains conversation history
    2. Accepts user input
    3. Streams agent responses
    4. Updates message history after each turn
    
    Args:
        agent: The LangChain agent to run
    """
    # Initialize empty message history
    messages = []

    while True:
        # Get user input
        query = input("Enter your question (exit/quit/q to quit): ")
        
        # Check for exit commands
        if query.lower() in ['exit', 'quit', 'q']:
            print("Exiting...")
            break
        
        # Add user message to conversation history
        messages.append({"role": "user", "content": query})
        
        # Stream agent response
        # agent.stream() yields intermediate states during execution
        for event in agent.stream(
            {"messages": messages},
            stream_mode="values",  # Stream complete state at each step
            config={"run_name": RUN_NAME},
        ):
            # Print the last message (agent's response or tool output)
            event["messages"][-1].pretty_print()
        
        # Update message history with the complete conversation
        # including agent responses and tool calls
        messages = event["messages"]


def main():
    """
    Main entry point for the application.
    
    This function orchestrates:
    1. Skill discovery
    2. Tool setup
    3. Tool display (for debugging)
    4. Agent creation with model and tools
    5. Interactive conversation loop
    """
    # Display available skills
    if AVAILABLE_SKILLS:
        print("Available Skills:")
        for name, info in AVAILABLE_SKILLS.items():
            print(f"  - {name}")
            print(f"    {info['description']}")
        print("="*70 + "\n")
    else:
        print("\nWarning: No skills found in SKILLS directory\n")
    
    # Get all available tools
    tools = get_tools()
    
    # Display tools for debugging
    # This shows what capabilities the model has access to
    display_tools(tools)
    
    # Create agent with LLM model, tools, and system prompt
    # The agent will use these tools to answer user queries
    agent = create_agent(
        model, 
        tools,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Start interactive conversation loop
    run_agent_loop(agent)

# Script Entry Point
if __name__ == "__main__":
    main()