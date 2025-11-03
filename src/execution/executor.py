"""Command execution engine with safety controls and monitoring."""

import asyncio
import os
import signal
import time
from typing import Dict, Optional, Callable, Any
from datetime import datetime
import psutil

from ..utils.logger import get_logger


class CommandExecutionError(Exception):
    """Exception raised for command execution errors."""
    pass


class CommandExecutor:
    """Executes commands with safety checks and monitoring."""
    
    def __init__(self, config: Dict[str, Any], safety_validator=None):
        """
        Initialize command executor.
        
        Args:
            config: Execution configuration
            safety_validator: Safety validator instance (optional)
        """
        self.config = config
        self.safety = safety_validator
        self.active_processes: Dict[str, asyncio.subprocess.Process] = {}
        self.logger = get_logger(__name__)
    
    async def execute(
        self,
        command: str,
        timeout: Optional[int] = None,
        working_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute command with safety checks and monitoring.
        
        Args:
            command: Command to execute
            timeout: Timeout in seconds (uses config default if None)
            working_dir: Working directory for command execution
            
        Returns:
            Dictionary containing execution results
        """
        start_time = time.time()
        
        # Validate command if safety validator is available
        if self.safety:
            validation = self.safety.validate(command)
            if not validation['allowed']:
                self.logger.error(
                    "command_blocked",
                    command=command,
                    reason=validation['reason'],
                )
                return {
                    'success': False,
                    'error': f"Command blocked: {validation['reason']}",
                    'exit_code': -1,
                    'command': command,
                    'duration': 0,
                }
        
        # Set timeout from config if not specified
        if timeout is None:
            timeout = self.config.get('timeout', {}).get('default', 300)
        
        # Set working directory
        cwd = working_dir or self.config.get('working_directory', '/tmp/kali-ai-agent')
        os.makedirs(cwd, exist_ok=True)
        
        self.logger.info(
            "command_execution_start",
            command=command,
            timeout=timeout,
            working_dir=cwd,
        )
        
        try:
            # Create subprocess
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                preexec_fn=os.setsid if os.name != 'nt' else None,
            )
            
            # Store process reference
            process_id = str(id(process))
            self.active_processes[process_id] = process
            
            try:
                # Wait for completion with timeout
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                duration = time.time() - start_time
                
                # Decode output
                stdout_text = stdout.decode('utf-8', errors='ignore')
                stderr_text = stderr.decode('utf-8', errors='ignore')
                
                result = {
                    'success': process.returncode == 0,
                    'output': stdout_text,
                    'error': stderr_text,
                    'exit_code': process.returncode,
                    'command': command,
                    'duration': duration,
                    'timestamp': datetime.utcnow().isoformat(),
                }
                
                self.logger.info(
                    "command_execution_complete",
                    command=command,
                    exit_code=process.returncode,
                    duration=duration,
                    output_length=len(stdout_text),
                )
                
                return result
                
            except asyncio.TimeoutError:
                # Kill process group
                if os.name != 'nt':
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                else:
                    process.kill()
                
                duration = time.time() - start_time
                
                self.logger.warning(
                    "command_timeout",
                    command=command,
                    timeout=timeout,
                    duration=duration,
                )
                
                return {
                    'success': False,
                    'error': f'Command timed out after {timeout} seconds',
                    'exit_code': -1,
                    'command': command,
                    'duration': duration,
                    'timestamp': datetime.utcnow().isoformat(),
                }
            
            finally:
                # Remove from active processes
                if process_id in self.active_processes:
                    del self.active_processes[process_id]
        
        except Exception as e:
            duration = time.time() - start_time
            
            self.logger.error(
                "command_execution_error",
                command=command,
                error=str(e),
                error_type=type(e).__name__,
                duration=duration,
            )
            
            return {
                'success': False,
                'error': str(e),
                'exit_code': -1,
                'command': command,
                'duration': duration,
                'timestamp': datetime.utcnow().isoformat(),
            }
    
    async def execute_with_streaming(
        self,
        command: str,
        callback: Callable[[str, str], None],
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute command with real-time output streaming.
        
        Args:
            command: Command to execute
            callback: Callback function for output lines (prefix, line)
            timeout: Timeout in seconds
            
        Returns:
            Execution result dictionary
        """
        start_time = time.time()
        
        if timeout is None:
            timeout = self.config.get('timeout', {}).get('default', 300)
        
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                preexec_fn=os.setsid if os.name != 'nt' else None,
            )
            
            output_lines = []
            
            async def read_stream(stream, prefix):
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    
                    decoded = line.decode('utf-8', errors='ignore')
                    output_lines.append(decoded)
                    await asyncio.to_thread(callback, prefix, decoded)
            
            # Read both streams concurrently with timeout
            try:
                await asyncio.wait_for(
                    asyncio.gather(
                        read_stream(process.stdout, 'stdout'),
                        read_stream(process.stderr, 'stderr')
                    ),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                if os.name != 'nt':
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                else:
                    process.kill()
                
                return {
                    'success': False,
                    'output': ''.join(output_lines),
                    'error': f'Command timed out after {timeout} seconds',
                    'exit_code': -1,
                    'command': command,
                    'duration': time.time() - start_time,
                }
            
            await process.wait()
            
            return {
                'success': process.returncode == 0,
                'output': ''.join(output_lines),
                'exit_code': process.returncode,
                'command': command,
                'duration': time.time() - start_time,
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'exit_code': -1,
                'command': command,
                'duration': time.time() - start_time,
            }
    
    def kill_all_processes(self) -> None:
        """Kill all active processes."""
        for process_id, process in list(self.active_processes.items()):
            try:
                if os.name != 'nt':
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.kill()
            except (ProcessLookupError, AttributeError):
                pass
        
        self.active_processes.clear()
        self.logger.info("all_processes_killed")
    
    def get_resource_usage(self) -> Dict[str, float]:
        """
        Get current resource usage.
        
        Returns:
            Dictionary with CPU and memory usage
        """
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
        }