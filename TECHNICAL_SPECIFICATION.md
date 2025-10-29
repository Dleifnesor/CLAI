# Kali AI Command Chaining System - Technical Specification

## Technology Stack

### Core Technologies
- **Language**: Python 3.10+
- **LLM Integration**: Ollama Python SDK
- **CLI Framework**: Rich (terminal formatting), Click (command parsing)
- **Async Operations**: asyncio, aiohttp
- **Configuration**: PyYAML, python-dotenv
- **Logging**: structlog (structured logging)
- **Testing**: pytest, pytest-asyncio, pytest-mock

### Key Dependencies
```python
# requirements.txt
ollama>=0.1.0
rich>=13.0.0
click>=8.1.0
pyyaml>=6.0
python-dotenv>=1.0.0
structlog>=23.0.0
aiohttp>=3.9.0
psutil>=5.9.0
xmltodict>=0.13.0
python-nmap>=0.7.1
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-mock>=3.11.0
```

## Detailed Component Specifications

### 1. CLI Interface (`src/cli/`)

#### interface.py - Main CLI Controller
```python
import click
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.layout import Layout

class CLIInterface:
    """Main CLI controller for the Kali AI Agent"""
    
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        
    @click.group()
    def cli():
        """Kali AI Command Chaining System"""
        pass
    
    @cli.command()
    @click.argument('objective')
    @click.option('--config', default='config.yaml', help='Configuration file')
    @click.option('--session', help='Resume from session ID')
    @click.option('--verbose', is_flag=True, help='Verbose output')
    def run(objective: str, config: str, session: str, verbose: bool):
        """Execute a security objective"""
        pass
    
    @cli.command()
    @click.argument('session_id')
    def resume(session_id: str):
        """Resume a previous session"""
        pass
    
    @cli.command()
    def list_sessions():
        """List all saved sessions"""
        pass
```

#### display.py - Rich Formatting
```python
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.markdown import Markdown

class DisplayManager:
    """Manages all terminal display formatting"""
    
    def __init__(self):
        self.console = Console()
    
    def show_objective(self, objective: str):
        """Display the security objective"""
        panel = Panel(
            objective,
            title="[bold cyan]Security Objective[/bold cyan]",
            border_style="cyan"
        )
        self.console.print(panel)
    
    def show_command(self, command: str, reasoning: str, risk_level: str):
        """Display command with AI reasoning"""
        # Color based on risk level
        color = {
            "safe": "green",
            "medium": "yellow",
            "high": "red"
        }.get(risk_level, "white")
        
        self.console.print(f"\n[bold {color}]Command:[/bold {color}] {command}")
        self.console.print(f"[dim]Reasoning: {reasoning}[/dim]")
    
    def show_output(self, output: str, tool: str):
        """Display command output with syntax highlighting"""
        syntax = Syntax(output, "bash", theme="monokai", line_numbers=True)
        panel = Panel(
            syntax,
            title=f"[bold]Output: {tool}[/bold]",
            border_style="blue"
        )
        self.console.print(panel)
    
    def show_findings(self, findings: dict):
        """Display discovered vulnerabilities and information"""
        table = Table(title="Discovered Findings")
        table.add_column("Type", style="cyan")
        table.add_column("Details", style="white")
        table.add_column("Severity", style="red")
        
        for finding in findings:
            table.add_row(
                finding['type'],
                finding['details'],
                finding['severity']
            )
        
        self.console.print(table)
    
    def show_progress(self, current: int, total: int, status: str):
        """Display progress toward objective"""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        )
        progress.add_task(f"[cyan]{status}", total=total, completed=current)
        self.console.print(progress)
```

#### prompts.py - User Interaction
```python
from rich.prompt import Prompt, Confirm

class PromptManager:
    """Handles user prompts and confirmations"""
    
    @staticmethod
    def confirm_command(command: str, risk_level: str) -> bool:
        """Request user approval for high-risk commands"""
        return Confirm.ask(
            f"[yellow]Execute {risk_level} risk command?[/yellow]\n{command}"
        )
    
    @staticmethod
    def get_target_info() -> dict:
        """Collect target information from user"""
        return {
            'target': Prompt.ask("Target IP/Domain"),
            'scope': Prompt.ask("Authorized scope (CIDR)", default=""),
            'constraints': Prompt.ask("Any constraints?", default="none")
        }
```

### 2. Core Agent (`src/core/`)

#### agent.py - AI Agent Core
```python
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class AgentState(Enum):
    INITIALIZING = "initializing"
    PLANNING = "planning"
    EXECUTING = "executing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Goal:
    description: str
    priority: int
    status: str
    sub_goals: List['Goal']

class AIAgent:
    """Central AI agent orchestrator"""
    
    def __init__(self, config: dict, llm_client, executor, state_manager):
        self.config = config
        self.llm = llm_client
        self.executor = executor
        self.state = state_manager
        self.current_state = AgentState.INITIALIZING
        self.goals: List[Goal] = []
    
    async def execute_objective(self, objective: str) -> dict:
        """Main execution loop for security objective"""
        self.current_state = AgentState.PLANNING
        
        # Parse objective and create goals
        await self._parse_objective(objective)
        
        # Main execution loop
        while not self._is_objective_complete():
            self.current_state = AgentState.EXECUTING
            
            # Get next command from LLM
            command_info = await self._get_next_command()
            
            # Validate and execute
            if await self._should_execute(command_info):
                result = await self.executor.execute(command_info['command'])
                
                # Analyze results
                self.current_state = AgentState.ANALYZING
                analysis = await self._analyze_result(result)
                
                # Update state
                self.state.add_command(command_info, result, analysis)
                
                # Check for strategy adjustment
                if analysis['requires_pivot']:
                    await self._adjust_strategy(analysis)
        
        self.current_state = AgentState.COMPLETED
        return self._generate_report()
    
    async def _parse_objective(self, objective: str):
        """Parse objective into actionable goals"""
        prompt = self._build_planning_prompt(objective)
        response = await self.llm.generate(prompt)
        self.goals = self._extract_goals(response)
    
    async def _get_next_command(self) -> dict:
        """Query LLM for next optimal command"""
        context = self.state.get_full_context()
        prompt = self._build_command_prompt(context)
        response = await self.llm.generate(prompt)
        
        return {
            'command': response['command'],
            'reasoning': response['reasoning'],
            'tool': response['tool'],
            'expected_outcome': response['expected_outcome']
        }
    
    async def _should_execute(self, command_info: dict) -> bool:
        """Determine if command should be executed"""
        # Safety validation
        risk_level = self.executor.safety.classify(command_info['command'])
        
        if risk_level == 'high':
            # Require user approval
            return await self._request_approval(command_info, risk_level)
        
        return True
    
    async def _analyze_result(self, result: dict) -> dict:
        """Analyze command execution result"""
        # Parse output
        parsed = self.executor.parser.parse(result)
        
        # Interpret findings
        interpretation = self.executor.interpreter.interpret(parsed)
        
        # Assess progress
        progress = self._assess_progress(interpretation)
        
        return {
            'parsed': parsed,
            'interpretation': interpretation,
            'progress': progress,
            'requires_pivot': self._needs_strategy_change(interpretation)
        }
    
    def _is_objective_complete(self) -> bool:
        """Check if objective has been achieved"""
        # Check goal completion
        completed_goals = [g for g in self.goals if g.status == 'completed']
        return len(completed_goals) == len(self.goals)
    
    async def _adjust_strategy(self, analysis: dict):
        """Adjust strategy based on analysis"""
        prompt = self._build_strategy_prompt(analysis)
        new_strategy = await self.llm.generate(prompt)
        self._update_goals(new_strategy)
```

#### state.py - State Manager
```python
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class StateManager:
    """Manages agent state and conversation context"""
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or self._generate_session_id()
        self.objective = ""
        self.command_history: List[Dict] = []
        self.discoveries: Dict = {
            'hosts': [],
            'services': [],
            'vulnerabilities': [],
            'credentials': []
        }
        self.context_window: List[Dict] = []
        self.max_context_size = 10
    
    def add_command(self, command_info: dict, result: dict, analysis: dict):
        """Add command execution to history"""
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'command': command_info['command'],
            'reasoning': command_info['reasoning'],
            'tool': command_info['tool'],
            'output': result['output'],
            'exit_code': result['exit_code'],
            'analysis': analysis
        }
        
        self.command_history.append(entry)
        self._update_context_window(entry)
        self._update_discoveries(analysis)
    
    def get_full_context(self) -> dict:
        """Get complete context for LLM"""
        return {
            'objective': self.objective,
            'session_id': self.session_id,
            'command_count': len(self.command_history),
            'recent_commands': self.context_window,
            'discoveries': self.discoveries,
            'current_progress': self._calculate_progress()
        }
    
    def _update_context_window(self, entry: dict):
        """Maintain sliding window of recent context"""
        self.context_window.append(entry)
        if len(self.context_window) > self.max_context_size:
            # Compress older entries
            self.context_window = self._compress_context(self.context_window)
    
    def _update_discoveries(self, analysis: dict):
        """Update discovered assets and vulnerabilities"""
        if 'hosts' in analysis['interpretation']:
            self.discoveries['hosts'].extend(analysis['interpretation']['hosts'])
        
        if 'vulnerabilities' in analysis['interpretation']:
            self.discoveries['vulnerabilities'].extend(
                analysis['interpretation']['vulnerabilities']
            )
    
    def save_session(self):
        """Persist session to disk"""
        session_file = Path(f"logs/sessions/{self.session_id}.json")
        session_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(session_file, 'w') as f:
            json.dump({
                'session_id': self.session_id,
                'objective': self.objective,
                'command_history': self.command_history,
                'discoveries': self.discoveries,
                'timestamp': datetime.utcnow().isoformat()
            }, f, indent=2)
    
    @classmethod
    def load_session(cls, session_id: str) -> 'StateManager':
        """Load session from disk"""
        session_file = Path(f"logs/sessions/{session_id}.json")
        
        with open(session_file, 'r') as f:
            data = json.load(f)
        
        manager = cls(session_id)
        manager.objective = data['objective']
        manager.command_history = data['command_history']
        manager.discoveries = data['discoveries']
        
        return manager
```

#### decision.py - Decision Engine
```python
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class CommandOption:
    command: str
    tool: str
    reasoning: str
    expected_outcome: str
    confidence: float
    risk_level: str

class DecisionEngine:
    """Intelligent decision-making for next commands"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.strategy_patterns = self._load_strategy_patterns()
    
    async def select_next_command(self, context: dict) -> CommandOption:
        """Select optimal next command based on context"""
        # Generate multiple options
        options = await self._generate_options(context)
        
        # Rank options
        ranked = self._rank_options(options, context)
        
        # Select best option
        return ranked[0]
    
    async def _generate_options(self, context: dict) -> List[CommandOption]:
        """Generate multiple command options"""
        prompt = self._build_options_prompt(context)
        response = await self.llm.generate(prompt)
        
        return [
            CommandOption(
                command=opt['command'],
                tool=opt['tool'],
                reasoning=opt['reasoning'],
                expected_outcome=opt['expected_outcome'],
                confidence=opt['confidence'],
                risk_level=opt['risk_level']
            )
            for opt in response['options']
        ]
    
    def _rank_options(self, options: List[CommandOption], 
                     context: dict) -> List[CommandOption]:
        """Rank options by likelihood of success"""
        scored_options = []
        
        for option in options:
            score = self._calculate_score(option, context)
            scored_options.append((score, option))
        
        # Sort by score descending
        scored_options.sort(key=lambda x: x[0], reverse=True)
        
        return [opt for _, opt in scored_options]
    
    def _calculate_score(self, option: CommandOption, context: dict) -> float:
        """Calculate option score based on multiple factors"""
        score = option.confidence
        
        # Adjust for progress toward goal
        if self._advances_objective(option, context):
            score += 0.2
        
        # Penalize high-risk commands
        if option.risk_level == 'high':
            score -= 0.1
        
        # Bonus for novel approaches
        if not self._recently_attempted(option, context):
            score += 0.1
        
        return score
    
    def _load_strategy_patterns(self) -> dict:
        """Load common penetration testing strategy patterns"""
        return {
            'reconnaissance': [
                'network_discovery',
                'port_scanning',
                'service_enumeration',
                'vulnerability_scanning'
            ],
            'exploitation': [
                'vulnerability_validation',
                'exploit_selection',
                'exploit_execution',
                'post_exploitation'
            ],
            'privilege_escalation': [
                'local_enumeration',
                'exploit_search',
                'escalation_attempt',
                'persistence'
            ]
        }
```

### 3. LLM Integration (`src/llm/`)

#### client.py - Ollama Client
```python
import ollama
import asyncio
from typing import Dict, Optional, List

class OllamaClient:
    """Wrapper for Ollama API communication"""
    
    def __init__(self, config: dict):
        self.config = config
        self.model = config['llm']['model']
        self.host = config['llm']['server']['host']
        self.port = config['llm']['server']['port']
        self.client = ollama.Client(host=f"http://{self.host}:{self.port}")
        self.conversation_history: List[Dict] = []
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> dict:
        """Generate response from LLM"""
        messages = []
        
        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add current prompt
        messages.append({
            'role': 'user',
            'content': prompt
        })
        
        try:
            response = await asyncio.to_thread(
                self.client.chat,
                model=self.model,
                messages=messages,
                options={
                    'temperature': self.config['llm']['parameters']['temperature'],
                    'top_p': self.config['llm']['parameters']['top_p'],
                    'num_predict': self.config['llm']['parameters']['max_tokens']
                }
            )
            
            # Update conversation history
            self.conversation_history.append({
                'role': 'user',
                'content': prompt
            })
            self.conversation_history.append({
                'role': 'assistant',
                'content': response['message']['content']
            })
            
            # Parse structured response
            return self._parse_response(response['message']['content'])
            
        except Exception as e:
            raise LLMCommunicationError(f"Failed to generate response: {e}")
    
    def _parse_response(self, content: str) -> dict:
        """Parse LLM response into structured format"""
        # Expected format:
        # COMMAND: <command>
        # TOOL: <tool_name>
        # REASONING: <reasoning>
        # EXPECTED_OUTCOME: <outcome>
        
        lines = content.strip().split('\n')
        result = {}
        
        for line in lines:
            if line.startswith('COMMAND:'):
                result['command'] = line.replace('COMMAND:', '').strip()
            elif line.startswith('TOOL:'):
                result['tool'] = line.replace('TOOL:', '').strip()
            elif line.startswith('REASONING:'):
                result['reasoning'] = line.replace('REASONING:', '').strip()
            elif line.startswith('EXPECTED_OUTCOME:'):
                result['expected_outcome'] = line.replace('EXPECTED_OUTCOME:', '').strip()
        
        return result
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def compress_history(self, max_messages: int = 10):
        """Compress conversation history to manage context window"""
        if len(self.conversation_history) > max_messages:
            # Keep system prompt and recent messages
            self.conversation_history = self.conversation_history[-max_messages:]
```

#### prompts.py - Prompt Templates
```python
class PromptTemplates:
    """Prompt engineering templates for different tasks"""
    
    @staticmethod
    def system_prompt() -> str:
        return """You are an expert penetration tester and security researcher with deep knowledge of the Kali Linux toolset. Your role is to analyze security objectives and generate precise, effective commands to accomplish them.

You have access to the complete Kali Purple toolkit including:
- Reconnaissance: nmap, masscan, dnsenum, theHarvester
- Vulnerability Scanning: OpenVAS, Nessus, Nikto
- Exploitation: Metasploit, exploit-db, searchsploit
- Web Testing: Burp Suite, sqlmap, XSSer
- Wireless: aircrack-ng, reaver, wifite
- Password Cracking: hashcat, John the Ripper, hydra
- Forensics: autopsy, volatility, binwalk
- Defensive: Suricata, Snort, OSSEC

Guidelines:
1. Generate ONE command at a time based on current context
2. Consider previous command outputs when deciding next steps
3. Follow penetration testing methodology (recon -> scanning -> exploitation)
4. Provide clear reasoning for each command
5. Specify expected outcomes
6. Adapt strategy based on results and errors
7. Respect safety constraints

Response Format:
COMMAND: <exact command to execute>
TOOL: <tool name>
REASONING: <why this command is optimal>
EXPECTED_OUTCOME: <what you expect to discover>
"""
    
    @staticmethod
    def planning_prompt(objective: str) -> str:
        return f"""Security Objective: {objective}

Break down this objective into a logical sequence of goals. Consider:
1. What information do we need first?
2. What tools are most appropriate?
3. What is the optimal order of operations?
4. What are potential obstacles?

Provide a structured plan with prioritized goals."""
    
    @staticmethod
    def command_prompt(context: dict) -> str:
        recent_commands = "\n".join([
            f"- {cmd['command']} -> {cmd['analysis']['interpretation'].get('summary', 'No summary')}"
            for cmd in context['recent_commands'][-3:]
        ])
        
        discoveries = f"""
Discovered Hosts: {len(context['discoveries']['hosts'])}
Discovered Services: {len(context['discoveries']['services'])}
Discovered Vulnerabilities: {len(context['discoveries']['vulnerabilities'])}
"""
        
        return f"""Current Objective: {context['objective']}

Progress: {context['current_progress']}%

Recent Commands:
{recent_commands}

Discoveries:
{discoveries}

Based on the current state and previous results, what is the next optimal command to execute?
Consider what information we've gathered and what we still need to achieve the objective.

Generate the next command following the specified format."""
    
    @staticmethod
    def strategy_adjustment_prompt(analysis: dict) -> str:
        return f"""Current strategy is not progressing effectively.

Recent Analysis:
{analysis}

Suggest an alternative approach or strategy adjustment to achieve the objective.
Consider:
1. Are we targeting the right assets?
2. Should we try different tools or techniques?
3. Do we need to gather more information first?
4. Are there alternative attack vectors?

Provide a revised strategy with specific next steps."""
```

### 4. Command Execution (`src/execution/`)

#### executor.py - Command Executor
```python
import asyncio
import subprocess
from typing import Dict, Optional
import psutil
import signal

class CommandExecutor:
    """Executes commands with safety controls"""
    
    def __init__(self, config: dict, safety_validator, parser, interpreter):
        self.config = config
        self.safety = safety_validator
        self.parser = parser
        self.interpreter = interpreter
        self.active_processes: Dict[str, subprocess.Popen] = {}
    
    async def execute(self, command: str, timeout: Optional[int] = None) -> dict:
        """Execute command with safety checks and monitoring"""
        # Validate command
        validation = self.safety.validate(command)
        if not validation['allowed']:
            return {
                'success': False,
                'error': f"Command blocked: {validation['reason']}",
                'exit_code': -1
            }
        
        # Set timeout
        timeout = timeout or self.config['execution']['timeout']['default']
        
        try:
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                preexec_fn=os.setsid  # Create new process group
            )
            
            # Monitor execution
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            result = {
                'success': process.returncode == 0,
                'output': stdout.decode('utf-8', errors='ignore'),
                'error': stderr.decode('utf-8', errors='ignore'),
                'exit_code': process.returncode,
                'command': command
            }
            
            return result
            
        except asyncio.TimeoutError:
            # Kill process group
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            return {
                'success': False,
                'error': f'Command timed out after {timeout} seconds',
                'exit_code': -1,
                'command': command
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'exit_code': -1,
                'command': command
            }
    
    async def execute_with_streaming(self, command: str, 
                                     callback) -> dict:
        """Execute command with real-time output streaming"""
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        output_lines = []
        
        async def read_stream(stream, prefix):
            while True:
                line = await stream.readline()
                if not line:
                    break
                
                decoded = line.decode('utf-8', errors='ignore')
                output_lines.append(decoded)
                await callback(prefix, decoded)
        
        # Read both streams concurrently
        await asyncio.gather(
            read_stream(process.stdout, 'stdout'),
            read_stream(process.stderr, 'stderr')
        )
        
        await process.wait()
        
        return {
            'success': process.returncode == 0,
            'output': ''.join(output_lines),
            'exit_code': process.returncode,
            'command': command
        }
```

This specification continues with detailed implementations for all remaining components. Would you like me to continue with the remaining sections, or would you prefer to review this architectural plan first?