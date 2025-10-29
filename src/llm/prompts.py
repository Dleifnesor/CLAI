"""Prompt engineering templates for the Kali AI Command Chaining System."""

from typing import Dict, List, Any


class PromptTemplates:
    """Collection of prompt templates for different tasks."""
    
    @staticmethod
    def system_prompt() -> str:
        """
        Get the system prompt that defines the AI's role and capabilities.
        
        Returns:
            System prompt string
        """
        return """You are an expert penetration tester and security researcher with deep knowledge of the Kali Linux toolset. Your role is to analyze security objectives and generate precise, effective commands to accomplish them.

You have access to the complete Kali Purple toolkit including:

RECONNAISSANCE TOOLS:
- nmap: Network scanning and service detection
- masscan: High-speed port scanning
- netdiscover: Network discovery
- dnsenum: DNS enumeration
- fierce: DNS reconnaissance
- theHarvester: OSINT gathering
- recon-ng: Reconnaissance framework

VULNERABILITY SCANNING:
- OpenVAS: Comprehensive vulnerability scanning
- Nessus: Professional vulnerability assessment
- Nikto: Web server scanner
- wpscan: WordPress security scanner
- joomscan: Joomla vulnerability scanner
- OWASP ZAP: Web application security scanner

EXPLOITATION:
- Metasploit Framework: Exploitation and post-exploitation
- exploit-db: Exploit database integration
- searchsploit: Local exploit search
- BeEF: Browser exploitation framework

WEB APPLICATION TESTING:
- Burp Suite: Web vulnerability scanner
- sqlmap: SQL injection automation
- XSSer: Cross-site scripting framework
- commix: Command injection exploiter
- wfuzz: Web application fuzzer
- dirb/gobuster: Directory brute forcing

WIRELESS SECURITY:
- aircrack-ng: WiFi security auditing
- reaver: WPS attack tool
- wifite: Automated wireless attack tool
- kismet: Wireless network detector

PASSWORD CRACKING:
- hashcat: Advanced password recovery
- John the Ripper: Password cracking
- hydra: Network login cracker
- medusa: Parallel brute force tool
- crunch: Wordlist generator

FORENSICS:
- autopsy: Digital forensics platform
- volatility: Memory forensics framework
- binwalk: Firmware analysis
- foremost: File carving

DEFENSIVE SECURITY:
- Suricata: IDS/IPS engine
- Snort: Network intrusion detection
- OSSEC: Host-based intrusion detection
- Wazuh: Security monitoring platform

GUIDELINES:
1. Generate ONE command at a time based on current context
2. Consider previous command outputs when deciding next steps
3. Follow penetration testing methodology (reconnaissance -> scanning -> exploitation)
4. Provide clear reasoning for each command
5. Specify expected outcomes
6. Adapt strategy based on results and errors
7. Respect safety constraints

RESPONSE FORMAT:
You MUST respond in this exact format:

COMMAND: <exact command to execute>
TOOL: <tool name>
REASONING: <why this command is optimal given the current context>
EXPECTED_OUTCOME: <what you expect to discover or achieve>

Example:
COMMAND: nmap -sn 192.168.1.0/24
TOOL: nmap
REASONING: Starting with network discovery to identify live hosts before detailed scanning
EXPECTED_OUTCOME: List of active hosts on the network with their IP addresses
"""
    
    @staticmethod
    def planning_prompt(objective: str, target_info: Dict[str, Any]) -> str:
        """
        Generate prompt for objective planning.
        
        Args:
            objective: Security objective
            target_info: Information about the target
            
        Returns:
            Planning prompt
        """
        return f"""Security Objective: {objective}

Target Information:
- Target: {target_info.get('target', 'Not specified')}
- Scope: {target_info.get('scope', 'Not specified')}
- Constraints: {target_info.get('constraints', 'None')}

Break down this objective into a logical sequence of goals. Consider:
1. What information do we need first?
2. What tools are most appropriate for each phase?
3. What is the optimal order of operations?
4. What are potential obstacles or challenges?
5. What safety considerations apply?

Provide a structured plan with prioritized goals and the general approach for each phase.
"""
    
    @staticmethod
    def command_prompt(context: Dict[str, Any]) -> str:
        """
        Generate prompt for next command selection.
        
        Args:
            context: Current context including history and discoveries
            
        Returns:
            Command generation prompt
        """
        # Format recent commands
        recent_commands = context.get('recent_commands', [])
        command_history = []
        
        for cmd in recent_commands[-3:]:  # Last 3 commands
            summary = cmd.get('analysis', {}).get('interpretation', {}).get('summary', 'No summary')
            command_history.append(
                f"- Command: {cmd['command']}\n"
                f"  Result: {summary}\n"
                f"  Exit Code: {cmd.get('exit_code', 'unknown')}"
            )
        
        history_text = "\n".join(command_history) if command_history else "No previous commands"
        
        # Format discoveries
        discoveries = context.get('discoveries', {})
        discovery_text = f"""
Discovered Hosts: {len(discoveries.get('hosts', []))}
Discovered Services: {len(discoveries.get('services', []))}
Discovered Vulnerabilities: {len(discoveries.get('vulnerabilities', []))}
Discovered Credentials: {len(discoveries.get('credentials', []))}
"""
        
        # Format progress
        progress = context.get('current_progress', 0)
        
        return f"""Current Objective: {context.get('objective', 'Not specified')}

Progress: {progress}%

Recent Command History:
{history_text}

Current Discoveries:
{discovery_text}

Based on the current state and previous results, what is the next optimal command to execute?

Consider:
1. What information have we gathered so far?
2. What do we still need to achieve the objective?
3. Are there any errors or obstacles from previous commands?
4. What is the logical next step in the penetration testing methodology?

Generate the next command following the specified format (COMMAND, TOOL, REASONING, EXPECTED_OUTCOME).
"""
    
    @staticmethod
    def strategy_adjustment_prompt(
        analysis: Dict[str, Any],
        failed_attempts: List[Dict[str, Any]],
    ) -> str:
        """
        Generate prompt for strategy adjustment.
        
        Args:
            analysis: Analysis of current situation
            failed_attempts: List of failed command attempts
            
        Returns:
            Strategy adjustment prompt
        """
        failed_commands = "\n".join([
            f"- {attempt['command']}: {attempt.get('error', 'Unknown error')}"
            for attempt in failed_attempts[-3:]
        ])
        
        return f"""Current strategy is not progressing effectively.

Recent Analysis:
{analysis.get('summary', 'No analysis available')}

Failed Attempts:
{failed_commands}

The current approach has encountered obstacles. Suggest an alternative strategy to achieve the objective.

Consider:
1. Are we targeting the right assets or services?
2. Should we try different tools or techniques?
3. Do we need to gather more information before proceeding?
4. Are there alternative attack vectors we haven't explored?
5. Should we adjust our scanning parameters or timing?

Provide a revised strategy with specific next steps and reasoning for the change.
"""
    
    @staticmethod
    def objective_assessment_prompt(
        objective: str,
        discoveries: Dict[str, Any],
        command_count: int,
    ) -> str:
        """
        Generate prompt for objective completion assessment.
        
        Args:
            objective: Original objective
            discoveries: All discoveries made
            command_count: Number of commands executed
            
        Returns:
            Assessment prompt
        """
        return f"""Original Objective: {objective}

Commands Executed: {command_count}

Discoveries Made:
- Hosts: {len(discoveries.get('hosts', []))}
- Services: {len(discoveries.get('services', []))}
- Vulnerabilities: {len(discoveries.get('vulnerabilities', []))}
- Credentials: {len(discoveries.get('credentials', []))}

Detailed Discoveries:
{discoveries}

Assess whether the objective has been achieved:
1. Have we accomplished what was requested?
2. Is there sufficient information gathered?
3. Are there any critical gaps in our assessment?
4. Should we continue with additional testing?

Provide:
- Completion status (COMPLETE, PARTIAL, or INCOMPLETE)
- Reasoning for the assessment
- Recommendations for next steps if incomplete
"""
    
    @staticmethod
    def error_analysis_prompt(
        command: str,
        error: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Generate prompt for error analysis and recovery.
        
        Args:
            command: Command that failed
            error: Error message
            context: Current context
            
        Returns:
            Error analysis prompt
        """
        return f"""A command has failed and needs analysis.

Failed Command: {command}
Error Message: {error}

Current Context:
- Objective: {context.get('objective', 'Not specified')}
- Progress: {context.get('current_progress', 0)}%
- Previous successful commands: {len(context.get('recent_commands', []))}

Analyze this error and suggest a recovery strategy:
1. What caused the error?
2. Is this a temporary issue or a fundamental problem?
3. Should we retry with different parameters?
4. Should we try an alternative tool or approach?
5. Do we need to gather more information first?

Provide:
- Error classification (TIMEOUT, PERMISSION, NOT_FOUND, NETWORK, SYNTAX, OTHER)
- Root cause analysis
- Recommended recovery action
- Alternative command if applicable
"""
    
    @staticmethod
    def tool_selection_prompt(
        task: str,
        available_tools: List[str],
        context: Dict[str, Any],
    ) -> str:
        """
        Generate prompt for tool selection.
        
        Args:
            task: Task to accomplish
            available_tools: List of available tools
            context: Current context
            
        Returns:
            Tool selection prompt
        """
        tools_list = "\n".join([f"- {tool}" for tool in available_tools])
        
        return f"""Task: {task}

Available Tools:
{tools_list}

Current Context:
- Objective: {context.get('objective', 'Not specified')}
- Progress: {context.get('current_progress', 0)}%
- Recent discoveries: {len(context.get('discoveries', {}).get('hosts', []))} hosts, {len(context.get('discoveries', {}).get('services', []))} services

Select the most appropriate tool for this task and explain why.

Consider:
1. Tool capabilities and strengths
2. Current phase of assessment
3. Information already gathered
4. Efficiency and speed requirements
5. Stealth considerations if applicable

Provide:
- Selected tool name
- Reasoning for selection
- Suggested command parameters
"""