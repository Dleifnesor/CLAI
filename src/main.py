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
    try:
        # Load configuration
        config = ConfigLoader(config_path)
        config.validate()
        
        # Setup logging
        log_config = config.get_logging_config()
        logger = setup_logger(
            level=log_config.get('level', 'INFO'),
            log_file=log_config.get('file'),
            format_type=log_config.get('format', 'json'),
            console_output=log_config.get('console_output', True),
        )
        
        logger.info("clai_started", objective=objective)
        
        print(f"\n🎯 Objective: {objective}\n")
        print("⚠️  Note: Full implementation in progress. Core components ready:")
        print("   ✓ Configuration system")
        print("   ✓ LLM integration (Ollama + dolphin3-abliterated:8b)")
        print("   ✓ Context management")
        print("   ✓ Logging system")
        print("\n   ⏳ In development:")
        print("   - Command execution engine")
        print("   - Safety validation system")
        print("   - Tool integration")
        print("   - AI agent orchestration")
        print("\nThe system will be fully operational once all components are integrated.")
        print("See IMPLEMENTATION_STATUS.md for current progress.\n")
        
        # TODO: Initialize and run AI agent
        # from src.core.agent import AIAgent
        # agent = AIAgent(config, llm_client, executor, state_manager)
        # await agent.execute_objective(objective)
        
        logger.info("clai_completed", objective=objective)
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Run 'sudo ./install.sh' to set up the system.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def list_sessions():
    """List all saved sessions."""
    sessions_dir = Path("logs/sessions")
    
    if not sessions_dir.exists():
        print("No sessions found.")
        return
    
    sessions = list(sessions_dir.glob("*.json"))
    
    if not sessions:
        print("No sessions found.")
        return
    
    print("\n📋 Saved Sessions:\n")
    for session_file in sorted(sessions, reverse=True):
        print(f"  - {session_file.stem}")
    
    print(f"\nTotal: {len(sessions)} sessions")
    print("\nResume a session with: clai --resume <session-id>\n")


async def resume_session(session_id: str):
    """
    Resume a previous session.
    
    Args:
        session_id: Session identifier
    """
    print(f"\n🔄 Resuming session: {session_id}\n")
    print("⚠️  Session resume functionality will be available once")
    print("   the state management system is fully implemented.\n")
    
    # TODO: Implement session resume
    # from src.core.state import StateManager
    # state = StateManager.load_session(session_id)
    # ... continue execution


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
        asyncio.run(resume_session(args[1]))
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