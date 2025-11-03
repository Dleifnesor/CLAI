"""Safety rules and command classifications."""

from typing import List, Dict, Set


class SafetyRules:
    """Defines safety rules for command classification."""
    
    # Commands that are always safe to auto-execute
    SAFE_COMMANDS: Set[str] = {
        'nmap',
        'masscan',
        'ping',
        'traceroute',
        'whois',
        'dig',
        'host',
        'nslookup',
        'dnsenum',
        'fierce',
        'theharvester',
        'recon-ng',
        'netdiscover',
    }
    
    # Commands that require user approval
    HIGH_RISK_COMMANDS: Set[str] = {
        'msfconsole',
        'metasploit',
        'sqlmap',
        'hydra',
        'medusa',
        'john',
        'hashcat',
        'aircrack-ng',
        'aireplay-ng',
        'reaver',
        'wifite',
        'exploit',
    }
    
    # Patterns that indicate high-risk operations
    HIGH_RISK_PATTERNS: List[str] = [
        r'--script.*vuln',  # Nmap vulnerability scripts
        r'-A\s',  # Aggressive nmap scan
        r'--exploit',
        r'--attack',
        r'--crack',
        r'--brute',
        r'--inject',
        r'--deauth',
    ]
    
    # Commands that are absolutely forbidden
    BLACKLIST: List[str] = [
        'rm -rf /',
        'rm -rf /*',
        'mkfs',
        'dd if=/dev/zero',
        ':(){ :|:& };:',  # Fork bomb
        'shutdown',
        'reboot',
        'halt',
        'poweroff',
        'init 0',
        'init 6',
        'systemctl poweroff',
        'systemctl reboot',
        '> /dev/sda',
        'wipefs',
        'fdisk',
        'parted',
        'mkswap',
    ]
    
    # Patterns that indicate blacklisted operations
    BLACKLIST_PATTERNS: List[str] = [
        r'rm\s+-rf\s+/',
        r'rm\s+-rf\s+/\*',
        r'>\s*/dev/sd',
        r'dd\s+if=/dev/zero',
        r'mkfs\.',
        r'shutdown',
        r'reboot',
        r'halt',
        r'poweroff',
    ]
    
    # Safe command patterns (for partial matching)
    SAFE_PATTERNS: List[str] = [
        r'^nmap\s+-s[nP]',  # Ping scans
        r'^nmap\s+.*--script\s+(?!.*vuln)',  # Non-vuln scripts
        r'^ping\s+',
        r'^traceroute\s+',
        r'^whois\s+',
        r'^dig\s+',
        r'^host\s+',
    ]
    
    @classmethod
    def get_safe_commands(cls) -> Set[str]:
        """Get set of safe commands."""
        return cls.SAFE_COMMANDS.copy()
    
    @classmethod
    def get_high_risk_commands(cls) -> Set[str]:
        """Get set of high-risk commands."""
        return cls.HIGH_RISK_COMMANDS.copy()
    
    @classmethod
    def get_blacklist(cls) -> List[str]:
        """Get blacklist of forbidden commands."""
        return cls.BLACKLIST.copy()
    
    @classmethod
    def get_blacklist_patterns(cls) -> List[str]:
        """Get blacklist patterns."""
        return cls.BLACKLIST_PATTERNS.copy()
    
    @classmethod
    def get_high_risk_patterns(cls) -> List[str]:
        """Get high-risk patterns."""
        return cls.HIGH_RISK_PATTERNS.copy()
    
    @classmethod
    def get_safe_patterns(cls) -> List[str]:
        """Get safe command patterns."""
        return cls.SAFE_PATTERNS.copy()