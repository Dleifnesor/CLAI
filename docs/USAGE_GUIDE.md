# CLAI Usage Guide

## Installation

```bash
git clone https://github.com/Dleifnesor/CLAI.git
cd CLAI
chmod +x install.sh
sudo ./install.sh
```

## Basic Usage

### Simple Command Format

```bash
clai "your security objective"
```

### Real-World Examples

**SMB Vulnerability Assessment**
```bash
clai "perform smb vulnerability check on any smb servers running on the 10.5.0.0/24"
```

**Network Discovery**
```bash
clai "discover all live hosts and services on 192.168.1.0/24"
```

**Web Application Testing**
```bash
clai "test web application at https://target.com for SQL injection and XSS"
```

**Wireless Security**
```bash
clai "audit wireless networks and check for weak encryption"
```

**Comprehensive Assessment**
```bash
clai "perform full security assessment of 10.0.0.50 including port scan, service detection, and vulnerability analysis"
```

## Advanced Usage

### Session Management

**List Sessions**
```bash
clai --list-sessions
```

**Resume Session**
```bash
clai --resume session_20231029_143022_a1b2c3d4
```

### Custom Configuration

**Use Custom Config**
```bash
clai --config /path/to/custom-config.yaml "your objective"
```

**Verbose Mode**
```bash
clai --verbose "your objective"
```

## Configuration

Edit `config.yaml` to customize behavior:

### LLM Settings
```yaml
llm:
  server:
    host: localhost  # or remote IP
    port: 11434
  model: huihui_ai/dolphin3-abliterated:8b
  parameters:
    temperature: 0.7  # Lower = more focused, Higher = more creative
```

### Safety Mode
```yaml
safety:
  mode: semi-autonomous  # Options: semi-autonomous, interactive, autonomous
  require_approval:
    - exploitation
    - password_cracking
    - brute_force
```

### Target Scope
```yaml
targets:
  allowed_networks:
    - 192.168.1.0/24
    - 10.0.0.0/8
  excluded_ips:
    - 192.168.1.1  # Gateway
```

### Execution Timeouts
```yaml
execution:
  timeout:
    default: 300
    scanning: 1800
    exploitation: 600
```

## Understanding the Workflow

### 1. Objective Analysis
CLAI analyzes your objective and creates a plan:

```
Input: "check for smb vulnerabilities on 10.5.0.0/24"

AI Plan:
1. Discover live hosts
2. Identify SMB services (ports 139, 445)
3. Enumerate SMB versions
4. Check for known vulnerabilities
5. Generate report
```

### 2. Command Generation
Each command is generated based on previous results:

```
Step 1: nmap -sn 10.5.0.0/24
Result: 12 hosts discovered

Step 2: nmap -p 139,445 --open 10.5.0.1-12
Result: 3 hosts with SMB

Step 3: nmap -sV -p 139,445 10.5.0.5,10.5.0.8,10.5.0.11
Result: SMB versions detected

Step 4: nmap --script smb-vuln* 10.5.0.5,10.5.0.8,10.5.0.11
[Requires Approval] → User approves
Result: Vulnerabilities found
```

### 3. Adaptive Behavior

**On Success:**
- Continues to next logical step
- Builds on discovered information

**On Failure:**
- Analyzes error
- Tries alternative approach
- Adjusts parameters

**On Discovery:**
- Pivots to investigate findings
- Prioritizes critical vulnerabilities

## Safety Features

### Auto-Execute (Safe Commands)
- Network scanning (nmap, masscan)
- Service enumeration
- DNS queries
- Port scanning
- Passive reconnaissance

### Require Approval (High-Risk)
- Exploitation attempts
- Password cracking
- Brute force attacks
- Vulnerability exploitation
- System modifications

### Never Execute (Blacklisted)
- System shutdown/reboot
- Disk formatting
- Recursive deletion
- Kernel modifications

## Approval Workflow

When a high-risk command is generated:

```
⚠️  High-Risk Command Detected

Command: nmap --script smb-vuln* -p 445 10.5.0.5
Risk Level: MEDIUM

AI Reasoning:
Testing for known SMB vulnerabilities including EternalBlue
and SMBv1 weaknesses on discovered SMB servers

Risk Assessment:
Command performs vulnerability testing which may trigger IDS

Execute this command? [y/N]:
```

## Output and Logging

### Real-Time Display
- Command being executed
- Live output streaming
- Discoveries as they're found
- Progress updates

### Session Logs
All sessions are saved to `logs/sessions/<session-id>.json`:

```json
{
  "session_id": "session_20231029_143022_a1b2c3d4",
  "objective": "check for smb vulnerabilities on 10.5.0.0/24",
  "command_history": [...],
  "discoveries": {
    "hosts": [...],
    "services": [...],
    "vulnerabilities": [...]
  },
  "progress": 85.5
}
```

### Audit Trail
Every command is logged with:
- Timestamp
- Command executed
- Output received
- User approvals
- Discoveries made
- Errors encountered

## Troubleshooting

### Ollama Connection Issues
```bash
# Check Ollama status
systemctl status ollama

# Start Ollama
systemctl start ollama

# Test connection
ollama list
```

### Model Not Found
```bash
# Pull the model
ollama pull huihui_ai/dolphin3-abliterated:8b
```

### Permission Errors
```bash
# Run with sudo for tools requiring root
sudo clai "your objective"
```

### Tool Not Found
```bash
# Install missing tools
sudo apt update
sudo apt install nmap masscan nikto sqlmap
```

## Best Practices

### 1. Define Clear Objectives
**Good:**
- "scan 192.168.1.0/24 for SMB vulnerabilities"
- "test web app at https://target.com for SQL injection"

**Too Vague:**
- "hack the network"
- "find vulnerabilities"

### 2. Set Proper Scope
Always configure authorized targets in `config.yaml`:

```yaml
targets:
  allowed_networks:
    - 192.168.1.0/24  # Your test network
  excluded_ips:
    - 192.168.1.1  # Critical systems
```

### 3. Review Approvals Carefully
When prompted for approval:
- Read the AI reasoning
- Understand the risk
- Verify the target
- Approve only if authorized

### 4. Monitor Progress
- Watch for discoveries
- Review command outputs
- Check for errors
- Assess progress

### 5. Save Important Sessions
Sessions are auto-saved, but you can:
- Resume interrupted assessments
- Review historical scans
- Export reports

## Example Workflows

### Network Reconnaissance
```bash
clai "discover all hosts and services on 192.168.1.0/24"
```

Expected workflow:
1. Ping sweep to find live hosts
2. Port scan on discovered hosts
3. Service version detection
4. OS fingerprinting
5. Vulnerability scanning
6. Report generation

### Web Application Security
```bash
clai "assess security of https://webapp.example.com"
```

Expected workflow:
1. Directory enumeration
2. Technology detection
3. Nikto scan
4. SQL injection testing
5. XSS testing
6. Authentication testing

### Wireless Audit
```bash
clai "audit wireless networks in the area"
```

Expected workflow:
1. Network discovery
2. WPS vulnerability check
3. Encryption analysis
4. Handshake capture
5. Security recommendations

## Tips and Tricks

### 1. Use Specific Targets
```bash
# Specific
clai "scan 192.168.1.50 for web vulnerabilities"

# Too broad
clai "scan everything"
```

### 2. Combine Multiple Goals
```bash
clai "scan 10.0.0.0/24 for SMB and HTTP services, then test for vulnerabilities"
```

### 3. Resume Long Scans
If interrupted:
```bash
clai --list-sessions
clai --resume <session-id>
```

### 4. Adjust Configuration
For faster scans:
```yaml
execution:
  timeout:
    scanning: 900  # Reduce from 1800
```

### 5. Review Logs
```bash
# View session log
cat logs/sessions/<session-id>.json | jq

# View main log
tail -f logs/kali-ai-agent.log
```

## Legal and Ethical Use

### ✅ Authorized Use
- Your own systems
- Client systems with written permission
- Lab environments
- Bug bounty programs (within scope)
- Educational purposes (authorized labs)

### ❌ Unauthorized Use
- Systems you don't own
- Without explicit permission
- Outside defined scope
- Malicious purposes

### Always:
1. Get written authorization
2. Define clear scope
3. Follow rules of engagement
4. Document everything
5. Report responsibly

## Getting Help

```bash
# Show help
clai --help

# Check version
clai --version

# View documentation
cat README.md
cat QUICK_START.md
```

## Support

- GitHub Issues: https://github.com/Dleifnesor/CLAI/issues
- Documentation: See docs/ directory
- Examples: See examples/ directory