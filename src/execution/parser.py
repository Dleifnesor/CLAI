"""Output parser for extracting structured data from command outputs."""

import re
import json
import xmltodict
from typing import Dict, List, Any, Optional

from ..utils.helpers import (
    extract_ips_from_text,
    extract_ports_from_text,
    extract_cves_from_text,
)
from ..utils.logger import get_logger


class OutputParser:
    """Parses command output into structured data."""
    
    def __init__(self):
        """Initialize output parser."""
        self.logger = get_logger(__name__)
        self.parsers = {
            'nmap': self._parse_nmap,
            'masscan': self._parse_masscan,
            'nikto': self._parse_nikto,
            'sqlmap': self._parse_sqlmap,
            'hydra': self._parse_hydra,
            'searchsploit': self._parse_searchsploit,
            'generic': self._parse_generic,
        }
    
    def parse(self, result: Dict[str, Any], tool: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse command output based on tool type.
        
        Args:
            result: Command execution result
            tool: Tool name (optional, will try to detect)
            
        Returns:
            Parsed structured data
        """
        if not result.get('success'):
            return self._parse_error(result)
        
        output = result.get('output', '')
        command = result.get('command', '')
        
        # Detect tool if not specified
        if not tool:
            tool = self._detect_tool(command)
        
        # Get appropriate parser
        parser_func = self.parsers.get(tool, self.parsers['generic'])
        
        try:
            parsed = parser_func(output, command)
            parsed['tool'] = tool
            parsed['raw_output'] = output
            
            self.logger.info(
                "output_parsed",
                tool=tool,
                items_found=len(parsed.get('items', [])),
            )
            
            return parsed
            
        except Exception as e:
            self.logger.error(
                "parsing_error",
                tool=tool,
                error=str(e),
            )
            # Fallback to generic parser
            return self.parsers['generic'](output, command)
    
    def _detect_tool(self, command: str) -> str:
        """Detect tool from command string."""
        command_lower = command.lower()
        
        if 'nmap' in command_lower:
            return 'nmap'
        elif 'masscan' in command_lower:
            return 'masscan'
        elif 'nikto' in command_lower:
            return 'nikto'
        elif 'sqlmap' in command_lower:
            return 'sqlmap'
        elif 'hydra' in command_lower:
            return 'hydra'
        elif 'searchsploit' in command_lower:
            return 'searchsploit'
        elif 'msfconsole' in command_lower or 'metasploit' in command_lower:
            return 'metasploit'
        
        return 'generic'
    
    def _parse_nmap(self, output: str, command: str) -> Dict[str, Any]:
        """Parse nmap output."""
        parsed = {
            'hosts': [],
            'services': [],
            'items': [],
        }
        
        # Extract hosts
        host_pattern = r'Nmap scan report for ([^\s]+)(?: \(([^\)]+)\))?'
        hosts = re.findall(host_pattern, output)
        
        for hostname, ip in hosts:
            host_info = {
                'hostname': hostname if not ip else ip,
                'ip': ip if ip else hostname,
                'ports': [],
            }
            parsed['hosts'].append(host_info)
        
        # Extract open ports and services
        port_pattern = r'(\d+)/(tcp|udp)\s+open\s+(\S+)(?:\s+(.+))?'
        ports = re.findall(port_pattern, output)
        
        for port, protocol, service, version in ports:
            service_info = {
                'port': int(port),
                'protocol': protocol,
                'service': service,
                'version': version.strip() if version else '',
            }
            parsed['services'].append(service_info)
            parsed['items'].append(service_info)
        
        # Extract OS detection if present
        os_pattern = r'OS details: (.+)'
        os_match = re.search(os_pattern, output)
        if os_match:
            parsed['os_detection'] = os_match.group(1)
        
        return parsed
    
    def _parse_masscan(self, output: str, command: str) -> Dict[str, Any]:
        """Parse masscan output."""
        parsed = {
            'hosts': [],
            'services': [],
            'items': [],
        }
        
        # Masscan output format: Discovered open port 80/tcp on 192.168.1.1
        port_pattern = r'Discovered open port (\d+)/(tcp|udp) on ([\d\.]+)'
        matches = re.findall(port_pattern, output)
        
        for port, protocol, ip in matches:
            service_info = {
                'ip': ip,
                'port': int(port),
                'protocol': protocol,
            }
            parsed['services'].append(service_info)
            parsed['items'].append(service_info)
            
            # Add to hosts if not already present
            if ip not in [h['ip'] for h in parsed['hosts']]:
                parsed['hosts'].append({'ip': ip})
        
        return parsed
    
    def _parse_nikto(self, output: str, command: str) -> Dict[str, Any]:
        """Parse nikto output."""
        parsed = {
            'vulnerabilities': [],
            'items': [],
        }
        
        # Nikto findings format: + OSVDB-XXXX: /path: Description
        vuln_pattern = r'\+ ([A-Z]+-\d+): (.+?): (.+)'
        matches = re.findall(vuln_pattern, output)
        
        for vuln_id, path, description in matches:
            vuln_info = {
                'id': vuln_id,
                'path': path,
                'description': description.strip(),
                'severity': 'medium',  # Default, can be refined
            }
            parsed['vulnerabilities'].append(vuln_info)
            parsed['items'].append(vuln_info)
        
        return parsed
    
    def _parse_sqlmap(self, output: str, command: str) -> Dict[str, Any]:
        """Parse sqlmap output."""
        parsed = {
            'vulnerabilities': [],
            'databases': [],
            'items': [],
        }
        
        # Check for SQL injection
        if 'is vulnerable' in output.lower() or 'injectable' in output.lower():
            vuln_info = {
                'type': 'SQL Injection',
                'severity': 'high',
                'details': 'SQL injection vulnerability detected',
            }
            parsed['vulnerabilities'].append(vuln_info)
            parsed['items'].append(vuln_info)
        
        # Extract database names
        db_pattern = r'available databases \[(\d+)\]:\s*\[(.+?)\]'
        db_match = re.search(db_pattern, output, re.DOTALL)
        if db_match:
            databases = [db.strip().strip("'") for db in db_match.group(2).split(',')]
            parsed['databases'] = databases
        
        return parsed
    
    def _parse_hydra(self, output: str, command: str) -> Dict[str, Any]:
        """Parse hydra output."""
        parsed = {
            'credentials': [],
            'items': [],
        }
        
        # Hydra success format: [port][protocol] host: login   password: pass
        cred_pattern = r'\[(\d+)\]\[(\w+)\]\s+host:\s+(\S+)\s+login:\s+(\S+)\s+password:\s+(\S+)'
        matches = re.findall(cred_pattern, output)
        
        for port, protocol, host, login, password in matches:
            cred_info = {
                'host': host,
                'port': int(port),
                'protocol': protocol,
                'username': login,
                'password': password,
            }
            parsed['credentials'].append(cred_info)
            parsed['items'].append(cred_info)
        
        return parsed
    
    def _parse_searchsploit(self, output: str, command: str) -> Dict[str, Any]:
        """Parse searchsploit output."""
        parsed = {
            'exploits': [],
            'items': [],
        }
        
        # Extract exploit entries
        lines = output.split('\n')
        for line in lines:
            if '|' in line and not line.startswith('-'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 2:
                    exploit_info = {
                        'title': parts[0],
                        'path': parts[1] if len(parts) > 1 else '',
                    }
                    parsed['exploits'].append(exploit_info)
                    parsed['items'].append(exploit_info)
        
        return parsed
    
    def _parse_generic(self, output: str, command: str) -> Dict[str, Any]:
        """Generic parser for unknown tools."""
        parsed = {
            'summary': '',
            'items': [],
        }
        
        # Extract IPs
        ips = extract_ips_from_text(output)
        if ips:
            parsed['ips'] = ips
            parsed['items'].extend([{'type': 'ip', 'value': ip} for ip in ips])
        
        # Extract ports
        ports = extract_ports_from_text(output)
        if ports:
            parsed['ports'] = ports
            parsed['items'].extend([{'type': 'port', 'value': port} for port in ports])
        
        # Extract CVEs
        cves = extract_cves_from_text(output)
        if cves:
            parsed['cves'] = cves
            parsed['items'].extend([{'type': 'cve', 'value': cve} for cve in cves])
        
        # Create summary
        summary_parts = []
        if ips:
            summary_parts.append(f"{len(ips)} IP addresses")
        if ports:
            summary_parts.append(f"{len(ports)} ports")
        if cves:
            summary_parts.append(f"{len(cves)} CVEs")
        
        parsed['summary'] = ', '.join(summary_parts) if summary_parts else 'No structured data extracted'
        
        return parsed
    
    def _parse_error(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse error information."""
        error_text = result.get('error', '')
        
        # Classify error type
        error_type = 'OTHER'
        
        if 'timeout' in error_text.lower():
            error_type = 'TIMEOUT'
        elif 'permission denied' in error_text.lower() or 'not permitted' in error_text.lower():
            error_type = 'PERMISSION'
        elif 'not found' in error_text.lower() or 'command not found' in error_text.lower():
            error_type = 'NOT_FOUND'
        elif 'connection' in error_text.lower() or 'network' in error_text.lower():
            error_type = 'NETWORK'
        elif 'syntax' in error_text.lower() or 'invalid' in error_text.lower():
            error_type = 'SYNTAX'
        
        return {
            'error': True,
            'error_type': error_type,
            'error_message': error_text,
            'exit_code': result.get('exit_code', -1),
            'command': result.get('command', ''),
        }