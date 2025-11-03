"""Main entry point for the Kali AI Command Chaining System."""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import ConfigLoader
from src.utils.logger import setup_logger, get_logger
from src.utils.helpers import generate_session_id


def print_banner():
    """Print the application banner."""
    banner = """
╔══════════════════════════════════════════════════════════╗
║     CLAI - Kali AI Command Chaining System              ║
║     Autonomous AI-Powered Penetration Testing           ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_help():
    """Print help information."""
    help_text = """
Usage:
  clai "your security objective"
  clai [options]

Examples:
  clai "perform smb vulnerability check on 10.5.0.0/24"
  clai "scan network 192.168.1.0/24 for open ports"
  clai "test web application at https://target.com"
  clai "audit wireless networks in the area"

Options:
  --help              Show this help message
  --version           Show version information
  --list-sessions     List all saved sessions
  --resume <id>       Resume a previous session
  --config <path>     Use custom configuration file
  --verbose           Enable verbose output
  --debug             Enable debug mode

Configuration:
  Edit config.yaml to customize:
  - LLM settings (Ollama server, model)
  - Safety mode (semi-autonomous, interactive, autonomous)
  - Target scope and exclusions
  - Tool paths and timeouts
  - Logging preferences

Safety:
  - Semi-autonomous mode (default): Auto-execute safe commands,
    require approval for exploitation/modification operations
  - All commands are logged with full audit trail
  - Blacklist prevents destructive operations
  - Scope validation ensures authorized targets only

Documentation:
  - README.md - Quick start guide
  - ARCHITECTURE.md - System architecture
  - IMPLEMENTATION_PLAN.md - Development roadmap
  - docs/ - Detailed documentation

Warning:
  Only use on authorized targets. Unauthorized access is illegal.
"""
    print(help_text)


def print_version():
    """Print version information."""
    from src import __version__
    print(f"CLAI - Kali AI Command Chaining System v{__version__}")
    print("Powered by dolphin3-abliterated:8b via Ollama")


async def run_objective(objective: str, config_path: str = None, verbose: bool = False):
    """
    Run a security objective.
    
    Args:
        objective: Security objective to accomplish
        config_path: Path to configuration file
        verbose: Enable verbose output
    """
    from src.cli.interface import CLIInterface
    from src.core.agent import AIAgent
    from src.core.state import StateManager
    from src.llm.client import OllamaClient
    from src.execution.executor import CommandExecutor
    from src.safety.validator import SafetyValidator
    
    try:
        # Load configuration
        config = ConfigLoader(config_path)
        config.validate()
        
        # Setup logging
        log_config = config.get_logging_config()
        logger = setup_logger(
            level='DEBUG' if verbose else log_config.get('level', 'INFO'),
            log_file=log_config.get('file'),
            format_type=log_config.get('format', 'json'),
            console_output=log_config.get('console_output', True),
        )
        
        logger.info("clai_started", objective=objective)
        
        # Initialize CLI
        cli = CLIInterface()
        cli.display.show_banner()
        cli.display.show_objective(objective)
        
        # Initialize components
        cli.display.show_info("Initializing AI agent...")
        
        # Create LLM client
        llm_config = config.get_llm_config()
        llm_client = OllamaClient(llm_config)
        
        # Test connection
        cli.display.show_info("Testing Ollama connection...")
        if not await llm_client.test_connection():
            cli.display.show_error("Failed to connect to Ollama server", "Connection Error")
            cli.display.show_info(
                f"Please ensure Ollama is running at {llm_config['server']['host']}:{llm_config['server']['port']}"
            )
            sys.exit(1)
        
        # Check model availability
        if not await llm_client.check_model_availability():
            cli.display.show_warning(
                f"Model {llm_config['model']} not found. Attempting to pull..."
            )
            # Model will be pulled automatically by Ollama on first use
        
        # Create safety validator
        safety_config = config.get_safety_config()
        safety_validator = SafetyValidator(safety_config)
        
        # Create command executor
        exec_config = config.get_execution_config()
        executor = CommandExecutor(exec_config, safety_validator)
        
        # Create state manager
        state_manager = StateManager()
        
        # Create AI agent
        agent_config = config.get_agent_config()
        agent = AIAgent(
            config=agent_config,
            llm_client=llm_client,
            executor=executor,
            state_manager=state_manager,
            approval_callback=cli.approval_callback,
            progress_callback=cli.progress_callback,
        )
        
        cli.display.show_success("AI agent initialized successfully")
        cli.display.show_info(f"Session ID: {state_manager.session_id}")
        
        # Execute objective
        report = await agent.execute_objective(objective)
        
        # Show final report
        cli.display.show_final_report(report)
        
        cli.display.show_success(
            f"Session saved: logs/sessions/{state_manager.session_id}.json"
        )
        
        logger.info("clai_completed", objective=objective, session_id=state_manager.session_id)
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Run 'sudo ./install.sh' to set up the system.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def list_sessions():
    """List all saved sessions."""
    from src.cli.interface import CLIInterface
    
    cli = CLIInterface()
    cli.display.show_banner()
    cli.list_sessions()


async def resume_session(session_id: str, config_path: str = None, verbose: bool = False):
    """
    Resume a previous session.
    
    Args:
        session_id: Session identifier
        config_path: Path to configuration file
        verbose: Enable verbose output
    """
    from src.cli.interface import CLIInterface
    from src.core.agent import AIAgent
    from src.core.state import StateManager
    from src.llm.client import OllamaClient
    from src.execution.executor import CommandExecutor
    from src.safety.validator import SafetyValidator
    
    try:
        # Load configuration
        config = ConfigLoader(config_path)
        config.validate()
        
        # Setup logging
        log_config = config.get_logging_config()
        logger = setup_logger(
            level='DEBUG' if verbose else log_config.get('level', 'INFO'),
            log_file=log_config.get('file'),
            format_type=log_config.get('format', 'json'),
            console_output=log_config.get('console_output', True),
        )
        
        # Initialize CLI
        cli = CLIInterface()
        cli.display.show_banner()
        cli.display.show_info(f"Resuming session: {session_id}")
        
        # Load session state
        state_manager = StateManager.load(session_id)
        
        cli.display.show_objective(state_manager.objective)
        cli.display.show_info(f"Previous progress: {state_manager.calculate_progress():.1f}%")
        cli.display.show_info(f"Commands executed: {len(state_manager.command_history)}")
        
        # Show current discoveries
        if any(state_manager.discoveries.values()):
            cli.display.show_discoveries(state_manager.discoveries)
        
        # Initialize components
        llm_config = config.get_llm_config()
        llm_client = OllamaClient(llm_config)
        
        safety_config = config.get_safety_config()
        safety_validator = SafetyValidator(safety_config)
        
        exec_config = config.get_execution_config()
        executor = CommandExecutor(exec_config, safety_validator)
        
        # Create AI agent with loaded state
        agent_config = config.get_agent_config()
        agent = AIAgent(
            config=agent_config,
            llm_client=llm_client,
            executor=executor,
            state_manager=state_manager,
            approval_callback=cli.approval_callback,
            progress_callback=cli.progress_callback,
        )
        
        cli.display.show_success("Session resumed, continuing execution...")
        
        # Continue execution
        report = await agent.execute_objective(state_manager.objective)
        
        # Show final report
        cli.display.show_final_report(report)
        
        logger.info("session_resumed_and_completed", session_id=session_id)
        
    except FileNotFoundError as e:
        print(f"❌ Error: Session not found: {session_id}")
        print("Use 'clai --list-sessions' to see available sessions.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point."""
    args = sys.argv[1:]
    
    # No arguments - show help
    if not args:
        print_banner()
        print_help()
        return
    
    # Parse arguments
    if args[0] == "--help" or args[0] == "-h":
        print_banner()
        print_help()
        return
    
    if args[0] == "--version" or args[0] == "-v":
        print_version()
        return
    
    if args[0] == "--list-sessions":
        list_sessions()
        return
    
    if args[0] == "--resume":
        if len(args) < 2:
            print("❌ Error: Session ID required")
            print("Usage: clai --resume <session-id>")
            sys.exit(1)
        
        # Parse remaining args for config and verbose
        session_id = args[1]
        config_path = None
        verbose = False
        
        for i in range(2, len(args)):
            if args[i] == "--config" and i + 1 < len(args):
                config_path = args[i + 1]
            elif args[i] in ["--verbose", "--debug"]:
                verbose = True
        
        asyncio.run(resume_session(session_id, config_path, verbose))
        return
    
    # Check for options
    config_path = None
    verbose = False
    objective_args = []
    
    i = 0
    while i < len(args):
        if args[i] == "--config":
            if i + 1 < len(args):
                config_path = args[i + 1]
                i += 2
            else:
                print("❌ Error: --config requires a path")
                sys.exit(1)
        elif args[i] == "--verbose":
            verbose = True
            i += 1
        elif args[i] == "--debug":
            verbose = True
            i += 1
        else:
            objective_args.append(args[i])
            i += 1
    
    # Join remaining arguments as objective
    objective = " ".join(objective_args)
    
    if not objective:
        print("❌ Error: No objective specified")
        print("Usage: clai \"your security objective\"")
        print("       clai --help for more information")
        sys.exit(1)
    
    # Print banner and run
    print_banner()
    asyncio.run(run_objective(objective, config_path, verbose))


if __name__ == "__main__":
    main()