# CLAI - Quick Start Guide

## Installation

```bash
# Clone and install
git clone https://github.com/Dleifnesor/CLAI.git
cd kali-ai-agent
chmod +x install.sh
sudo ./install.sh
```

The installer will:
- Install Python dependencies
- Set up Ollama (local or remote)
- Download the dolphin3-abliterated:8b model
- Create the global `clai` command
- Verify Kali tools availability

## Usage

### Simple Command Format

Just type `clai` followed by your security objective in quotes:

```bash
clai "your security objective here"
```

### Real Examples

**SMB Vulnerability Check**
```bash
clai "perform smb vulnerability check on any smb servers running on the 10.5.0.0/24"
```

**Network Scanning**
```bash
clai "scan network 192.168.1.0/24 for open ports and services"
```

**Web Application Testing**
```bash
clai "test web application at https://target.com for common vulnerabilities"
```

**Wireless Security Audit**
```bash
clai "audit wireless networks in the area and check for weak security"
```

**Comprehensive Assessment**
```bash
clai "perform full security assessment of 10.0.0.50 including port scan, service detection, and vulnerability check"
```

**Specific Tool Usage**
```bash
clai "use nmap to discover live hosts on 192.168.1.0/24 then scan for vulnerabilities"
```

## Additional Commands

```bash
# Show help
clai --help

# List saved sessions
clai --list-sessions

# Resume a previous session
clai --resume session_20231028_143022_a1b2c3d4

# Enable verbose output
clai --verbose "your objective"

# Use custom config file
clai --config /path/to/config.yaml "your objective"
```

## How It Works

1. **You provide an objective** in natural language
2. **AI analyzes** the objective and creates a plan
3. **Commands are generated** dynamically based on results
4. **Safe commands auto-execute** (scanning, enumeration)
5. **High-risk commands require approval** (exploitation, attacks)
6. **Results are analyzed** and next steps determined
7. **Process continues** until objective is achieved

## Safety Features

### Auto-Execute (Safe)
- Network scanning
- Port enumeration
- Service detection
- DNS queries
- Passive reconnaissance

### Require Approval (High-Risk)
- Exploitation attempts
- Password cracking
- Brute force attacks
- SQL injection testing
- System modifications

### Never Execute (Blacklisted)
- System shutdown/reboot
- Disk formatting
- Recursive deletion
- Kernel modifications

## Example Session

```bash
$ clai "check for smb vulnerabilities on 10.5.0.0/24"

╔══════════════════════════════════════════════════════════╗
║     CLAI - Kali AI Command Chaining System              ║
║     Autonomous AI-Powered Penetration Testing           ║
╚══════════════════════════════════════════════════════════╝

🎯 Objective: check for smb vulnerabilities on 10.5.0.0/24

🤖 AI Agent: Analyzing objective...
📋 Plan: 
   1. Discover live hosts on 10.5.0.0/24
   2. Identify SMB services (ports 139, 445)
   3. Enumerate SMB versions
   4. Check for known SMB vulnerabilities
   5. Generate report

💻 Executing: nmap -sn 10.5.0.0/24
✓ Found 12 live hosts

💻 Executing: nmap -p 139,445 --open 10.5.0.1-12
✓ Found 3 hosts with SMB services

💻 Executing: nmap -sV -p 139,445 10.5.0.5,10.5.0.8,10.5.0.11
✓ Detected SMB versions

⚠️  High-Risk Command Detected
Command: nmap --script smb-vuln* -p 445 10.5.0.5,10.5.0.8,10.5.0.11
Tool: Nmap (vulnerability scripts)
Risk Level: MEDIUM
Execute? [y/N]: y

💻 Executing vulnerability scan...
✓ Scan complete

📊 Results:
   - 10.5.0.5: Vulnerable to MS17-010 (EternalBlue)
   - 10.5.0.8: No vulnerabilities found
   - 10.5.0.11: Vulnerable to SMBv1 enabled

✅ Objective Complete
📄 Report saved to: logs/sessions/session_20231028_143022_a1b2c3d4.json
```

## Configuration

Edit `config.yaml` to customize:

```yaml
# LLM Settings
llm:
  server:
    host: localhost  # or remote IP
  model: huihui_ai/dolphin3-abliterated:8b

# Safety Mode
safety:
  mode: semi-autonomous  # or interactive, autonomous

# Target Scope
targets:
  allowed_networks:
    - 192.168.1.0/24
    - 10.0.0.0/8
  excluded_ips:
    - 192.168.1.1  # Gateway
```

## Tips

1. **Be specific** in your objectives for better results
2. **Define scope** in config.yaml before starting
3. **Review logs** in `logs/sessions/` for audit trail
4. **Use --verbose** for debugging
5. **Resume sessions** if interrupted
6. **Only use on authorized targets**

## Troubleshooting

**Command not found**
```bash
# Verify installation
which clai
# Should output: /usr/local/bin/clai

# If not found, reinstall
cd /path/to/kali-ai-agent
sudo ./install.sh
```

**Ollama connection error**
```bash
# Check Ollama status
systemctl status ollama

# Start Ollama
systemctl start ollama

# Test connection
ollama list
```

**Model not found**
```bash
# Download model
ollama pull huihui_ai/dolphin3-abliterated:8b
```

**Permission denied**
```bash
# Some tools require root
sudo clai "your objective"
```

## Documentation

- [`README.md`](README.md) - Full documentation
- [`ARCHITECTURE.md`](ARCHITECTURE.md) - System design
- [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) - Development roadmap
- [`config.yaml`](config.yaml) - Configuration reference

## Legal Notice

⚠️ **IMPORTANT**: Only use on systems you own or have explicit written authorization to test. Unauthorized access is illegal and unethical.

This tool is for:
- ✅ Authorized penetration testing
- ✅ Security research in lab environments
- ✅ Educational purposes
- ✅ Red team exercises with permission

---

**Need help?** Run `clai --help` or check the full documentation in README.md