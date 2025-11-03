"""Result interpreter for semantic analysis of command outputs."""

from typing import Dict, List, Any
from ..utils.logger import get_logger


class ResultInterpreter:
    """Interprets parsed command results for semantic meaning."""
    
    def __init__(self):
        """Initialize result interpreter."""
        self.logger = get_logger(__name__)
    
    def interpret(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interpret parsed results to extract semantic meaning.
        
        Args:
            parsed: Parsed command output
            
        Returns:
            Interpretation with discoveries and insights
        """
        if parsed.get('error'):
            return self._interpret_error(parsed)
        
        interpretation = {
            'hosts': [],
            'services': [],
            'vulnerabilities': [],
            'credentials': [],
            'summary': '',
            'significance': 'low',
            'next_steps': [],
        }
        
        # Extract hosts
        if 'hosts' in parsed:
            interpretation['hosts'] = [
                {
                    'ip': h.get('ip', h.get('hostname', 'unknown')),
                    'hostname': h.get('hostname', ''),
                    'status': 'up',
                }
                for h in parsed['hosts']
            ]
        
        # Extract services
        if 'services' in parsed:
            interpretation['services'] = [
                {
                    'ip': s.get('ip', ''),
                    'port': s.get('port'),
                    'protocol': s.get('protocol', 'tcp'),
                    'service': s.get('service', 'unknown'),
                    'version': s.get('version', ''),
                }
                for s in parsed['services']
            ]
        
        # Extract vulnerabilities
        if 'vulnerabilities' in parsed:
            interpretation['vulnerabilities'] = [
                {
                    'type': v.get('type', 'unknown'),
                    'severity': v.get('severity', 'medium'),
                    'details': v.get('details', v.get('description', '')),
                    'cve': v.get('id', v.get('cve', '')),
                }
                for v in parsed['vulnerabilities']
            ]
        
        # Extract credentials
        if 'credentials' in parsed:
            interpretation['credentials'] = [
                {
                    'host': c.get('host', ''),
                    'service': c.get('protocol', 'unknown'),
                    'username': c.get('username', ''),
                    'password': c.get('password', ''),
                }
                for c in parsed['credentials']
            ]
        
        # Extract exploits
        if 'exploits' in parsed:
            interpretation['exploits'] = parsed['exploits']
        
        # Determine significance
        interpretation['significance'] = self._assess_significance(interpretation)
        
        # Generate summary
        interpretation['summary'] = self._generate_summary(interpretation, parsed)
        
        # Suggest next steps
        interpretation['next_steps'] = self._suggest_next_steps(interpretation)
        
        self.logger.info(
            "result_interpreted",
            hosts=len(interpretation['hosts']),
            services=len(interpretation['services']),
            vulnerabilities=len(interpretation['vulnerabilities']),
            significance=interpretation['significance'],
        )
        
        return interpretation
    
    def _interpret_error(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Interpret error results."""
        error_type = parsed.get('error_type', 'OTHER')
        error_message = parsed.get('error_message', '')
        
        interpretation = {
            'error': True,
            'error_type': error_type,
            'error_message': error_message,
            'recoverable': self._is_recoverable(error_type),
            'suggested_action': self._suggest_error_recovery(error_type, error_message),
            'summary': f"Command failed: {error_type}",
        }
        
        return interpretation
    
    def _is_recoverable(self, error_type: str) -> bool:
        """Determine if error is recoverable."""
        recoverable_types = ['TIMEOUT', 'NETWORK', 'SYNTAX']
        return error_type in recoverable_types
    
    def _suggest_error_recovery(self, error_type: str, error_message: str) -> str:
        """Suggest recovery action for error."""
        suggestions = {
            'TIMEOUT': 'Retry with increased timeout or split into smaller tasks',
            'PERMISSION': 'Run with elevated privileges (sudo) or use alternative tool',
            'NOT_FOUND': 'Install missing tool or use alternative',
            'NETWORK': 'Check target connectivity and network configuration',
            'SYNTAX': 'Correct command syntax and retry',
            'OTHER': 'Analyze error message and try alternative approach',
        }
        
        return suggestions.get(error_type, 'Try alternative approach')
    
    def _assess_significance(self, interpretation: Dict[str, Any]) -> str:
        """Assess the significance of findings."""
        # High significance if vulnerabilities found
        if interpretation['vulnerabilities']:
            critical_count = sum(
                1 for v in interpretation['vulnerabilities']
                if v.get('severity') in ['critical', 'high']
            )
            if critical_count > 0:
                return 'critical'
            return 'high'
        
        # Medium significance if credentials found
        if interpretation['credentials']:
            return 'high'
        
        # Medium significance if many services found
        if len(interpretation['services']) > 10:
            return 'medium'
        
        # Low significance for basic discoveries
        if interpretation['hosts'] or interpretation['services']:
            return 'low'
        
        return 'minimal'
    
    def _generate_summary(self, interpretation: Dict[str, Any], parsed: Dict[str, Any]) -> str:
        """Generate human-readable summary."""
        parts = []
        
        if interpretation['hosts']:
            parts.append(f"Discovered {len(interpretation['hosts'])} hosts")
        
        if interpretation['services']:
            parts.append(f"Found {len(interpretation['services'])} services")
        
        if interpretation['vulnerabilities']:
            vuln_count = len(interpretation['vulnerabilities'])
            critical = sum(1 for v in interpretation['vulnerabilities'] if v.get('severity') == 'critical')
            high = sum(1 for v in interpretation['vulnerabilities'] if v.get('severity') == 'high')
            
            vuln_summary = f"Identified {vuln_count} vulnerabilities"
            if critical > 0:
                vuln_summary += f" ({critical} critical"
                if high > 0:
                    vuln_summary += f", {high} high)"
                else:
                    vuln_summary += ")"
            elif high > 0:
                vuln_summary += f" ({high} high)"
            
            parts.append(vuln_summary)
        
        if interpretation['credentials']:
            parts.append(f"Found {len(interpretation['credentials'])} credentials")
        
        if 'exploits' in interpretation:
            parts.append(f"Found {len(interpretation['exploits'])} potential exploits")
        
        if not parts:
            # Use generic summary from parser
            return parsed.get('summary', 'Command executed successfully')
        
        return '; '.join(parts)
    
    def _suggest_next_steps(self, interpretation: Dict[str, Any]) -> List[str]:
        """Suggest logical next steps based on findings."""
        suggestions = []
        
        # If hosts found, suggest service scanning
        if interpretation['hosts'] and not interpretation['services']:
            suggestions.append("Perform service detection on discovered hosts")
        
        # If services found, suggest vulnerability scanning
        if interpretation['services'] and not interpretation['vulnerabilities']:
            suggestions.append("Scan services for known vulnerabilities")
        
        # If vulnerabilities found, suggest exploitation
        if interpretation['vulnerabilities']:
            critical_vulns = [
                v for v in interpretation['vulnerabilities']
                if v.get('severity') in ['critical', 'high']
            ]
            if critical_vulns:
                suggestions.append("Attempt exploitation of critical vulnerabilities")
        
        # If credentials found, suggest using them
        if interpretation['credentials']:
            suggestions.append("Attempt authentication with discovered credentials")
        
        return suggestions