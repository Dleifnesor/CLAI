"""Helper utilities for the Kali AI Command Chaining System."""

import re
import ipaddress
import uuid
from datetime import datetime
from typing import List, Optional
import shlex


def validate_ip(ip: str) -> bool:
    """
    Validate an IP address.
    
    Args:
        ip: IP address string
        
    Returns:
        True if valid IP address
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def validate_cidr(cidr: str) -> bool:
    """
    Validate a CIDR notation network.
    
    Args:
        cidr: CIDR notation string (e.g., '192.168.1.0/24')
        
    Returns:
        True if valid CIDR notation
    """
    try:
        ipaddress.ip_network(cidr, strict=False)
        return True
    except ValueError:
        return False


def is_in_scope(
    target: str,
    allowed_networks: List[str],
    excluded_ips: Optional[List[str]] = None,
) -> bool:
    """
    Check if a target is within authorized scope.
    
    Args:
        target: Target IP address or hostname
        allowed_networks: List of allowed network ranges in CIDR notation
        excluded_ips: List of excluded IP addresses
        
    Returns:
        True if target is in scope
    """
    excluded_ips = excluded_ips or []
    
    # Try to parse as IP address
    try:
        target_ip = ipaddress.ip_address(target)
    except ValueError:
        # If not an IP, assume it's a hostname (would need DNS resolution)
        return True  # Allow hostnames for now
    
    # Check if in excluded list
    if str(target_ip) in excluded_ips:
        return False
    
    # Check if in any allowed network
    for network_str in allowed_networks:
        try:
            network = ipaddress.ip_network(network_str, strict=False)
            if target_ip in network:
                return True
        except ValueError:
            continue
    
    return False


def sanitize_command(command: str) -> str:
    """
    Sanitize a command string to prevent injection attacks.
    
    Args:
        command: Command string to sanitize
        
    Returns:
        Sanitized command string
    """
    # Remove dangerous characters and patterns
    dangerous_patterns = [
        r'[;&|`$]',  # Command chaining and substitution
        r'\$\(',     # Command substitution
        r'>\s*/dev/', # Writing to devices
    ]
    
    sanitized = command
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized)
    
    return sanitized.strip()


def generate_session_id() -> str:
    """
    Generate a unique session identifier.
    
    Returns:
        Session ID string
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"session_{timestamp}_{unique_id}"


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format a timestamp in ISO 8601 format.
    
    Args:
        dt: Datetime object. If None, uses current time.
        
    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat() + 'Z'


def parse_command_args(command: str) -> List[str]:
    """
    Parse command string into arguments safely.
    
    Args:
        command: Command string
        
    Returns:
        List of command arguments
    """
    try:
        return shlex.split(command)
    except ValueError:
        # If parsing fails, return as single argument
        return [command]


def truncate_output(output: str, max_length: int = 1000) -> str:
    """
    Truncate output to a maximum length.
    
    Args:
        output: Output string
        max_length: Maximum length
        
    Returns:
        Truncated output with indicator if truncated
    """
    if len(output) <= max_length:
        return output
    
    return output[:max_length] + f"\n... (truncated, {len(output) - max_length} more characters)"


def extract_ips_from_text(text: str) -> List[str]:
    """
    Extract IP addresses from text.
    
    Args:
        text: Text to search
        
    Returns:
        List of IP addresses found
    """
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    matches = re.findall(ip_pattern, text)
    
    # Validate and return only valid IPs
    return [ip for ip in matches if validate_ip(ip)]


def extract_ports_from_text(text: str) -> List[int]:
    """
    Extract port numbers from text.
    
    Args:
        text: Text to search
        
    Returns:
        List of port numbers found
    """
    # Look for patterns like "port 80", "80/tcp", etc.
    port_patterns = [
        r'port\s+(\d+)',
        r'(\d+)/tcp',
        r'(\d+)/udp',
        r':(\d+)\b',
    ]
    
    ports = set()
    for pattern in port_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                port = int(match)
                if 0 < port <= 65535:
                    ports.add(port)
            except ValueError:
                continue
    
    return sorted(list(ports))


def extract_cves_from_text(text: str) -> List[str]:
    """
    Extract CVE identifiers from text.
    
    Args:
        text: Text to search
        
    Returns:
        List of CVE identifiers found
    """
    cve_pattern = r'CVE-\d{4}-\d{4,7}'
    matches = re.findall(cve_pattern, text, re.IGNORECASE)
    return list(set(matches))


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.2f}h"


def calculate_progress(completed: int, total: int) -> float:
    """
    Calculate progress percentage.
    
    Args:
        completed: Number of completed items
        total: Total number of items
        
    Returns:
        Progress percentage (0-100)
    """
    if total == 0:
        return 0.0
    return min(100.0, (completed / total) * 100)


def is_private_ip(ip: str) -> bool:
    """
    Check if an IP address is private.
    
    Args:
        ip: IP address string
        
    Returns:
        True if IP is private
    """
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private
    except ValueError:
        return False


def normalize_tool_name(tool: str) -> str:
    """
    Normalize tool name for consistent lookup.
    
    Args:
        tool: Tool name
        
    Returns:
        Normalized tool name
    """
    # Remove common suffixes and normalize
    normalized = tool.lower().strip()
    normalized = normalized.replace('-', '_')
    normalized = normalized.replace('.py', '')
    normalized = normalized.replace('.sh', '')
    
    return normalized