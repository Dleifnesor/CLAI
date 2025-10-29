# Kali AI Command Chaining System

An autonomous AI-powered command chaining system for Kali Linux that integrates with the `huihui_ai/dolphin3-abliterated:8b` language model to execute penetration testing and security assessment workflows intelligently.

## Overview

This system accepts high-level security objectives and autonomously generates sequential commands from the complete Kali Purple toolset. Each command is dynamically formulated based on the actual output and results of previous command executions, creating an intelligent, adaptive penetration testing workflow.

##  Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Input: Objective                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      CLI Interface                          │
│  • Rich formatting  • Progress display  • User prompts      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      AI Agent Core                          │
│  • Objective parsing  • Goal decomposition  • Orchestration │
└─────┬──────────────┬──────────────┬──────────────┬──────────┘
      │              │              │              │
      ▼              ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│   LLM    │  │ Command  │  │  Safety  │  │  State   │
│          │  │Execution │  │ Validator│  │ Manager  │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
      │              │              │              │
      ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Kali Purple Toolset                        │
│  Recon • Vuln Scan • Exploit • WebApp • Wireless • More     │
└─────────────────────────────────────────────────────────────┘
```

##  Quick Start

### Prerequisites

- Kali Linux (2023.1 or later)
- Python 3.10+
- Ollama with dolphin3-abliterated:8b model
- Root/sudo access for certain tools

### Installation

```bash
# Clone the repository
git clone https://github.com/Dleifnesor/CLAI.git
cd kali-ai-agent

# Run installation script
chmod +x install.sh
sudo ./install.sh

# The script will:
# - Install Python dependencies
# - Set up Ollama (local or remote)
# - Configure the system
# - Verify tool availability
```

### Configuration

During installation, you'll be prompted for:
- **Ollama Server**: Leave blank for local, or enter remote IP address
- **Model**: Default is huihui_ai/dolphin3-abliterated:8b
- **Safety Mode**: Semi-autonomous (recommended)

Or manually edit `config.yaml`:

```yaml
llm:
  provider: ollama
  model: huihui_ai/dolphin3-abliterated:8b
  server:
    host: localhost  # or remote IP
    port: 11434

safety:
  mode: semi-autonomous
  require_approval:
    - exploitation
    - password_cracking
    - brute_force
```

### Basic Usage

The system is installed as a global `clai` command for easy access from anywhere:

```bash
# Simple usage - just provide your objective
clai "perform smb vulnerability check on 10.5.0.0/24"

# More examples
clai "scan network 192.168.1.0/24 for open ports"
clai "test web application at https://target.com"
clai "audit wireless networks in the area"

# Additional commands
clai --help              # Show help information
clai --list-sessions     # List all saved sessions
clai --resume <id>       # Resume a previous session
clai --verbose           # Enable verbose output
```

## 📖 Example Workflows

### Network Reconnaissance

```bash
clai "discover all hosts and services on 192.168.1.0/24"
```

**Expected AI Workflow**:
1. Network discovery with nmap ping scan
2. Port scanning on discovered hosts
3. Service version detection
4. Vulnerability scanning with OpenVAS
5. Report generation with findings

### Web Application Assessment

```bash
clai "assess security of https://target.example.com"
```

**Expected AI Workflow**:
1. Web crawling and directory enumeration
2. Technology stack detection
3. Vulnerability scanning (Nikto, OWASP ZAP)
4. SQL injection testing with sqlmap
5. XSS and CSRF testing
6. Authentication security assessment

### Wireless Security Audit

```bash
clai "audit wireless networks in the area"
```

**Expected AI Workflow**:
1. Wireless network discovery
2. WPS vulnerability assessment
3. Handshake capture
4. Password strength testing
5. Security recommendations

##  Safety Features

### Command Classification

**Auto-Execute (Safe)**:
- Network scanning (nmap, masscan)
- Service enumeration
- DNS queries
- Passive information gathering
- Port scanning

**Require Approval (High-Risk)**:
- Exploitation attempts
- Password cracking
- Brute force attacks
- SQL injection
- System modifications

**Blacklisted (Never Execute)**:
- System shutdown/reboot
- Disk formatting
- Recursive deletion
- Kernel modifications
- Critical service termination

### Approval Workflow

When a high-risk command is generated:

```
┌─────────────────────────────────────────────────────┐
│   High-Risk Command Detected                        │
├─────────────────────────────────────────────────────┤
│ Command: msfconsole -x "use exploit/..."            │
│ Tool: Metasploit Framework                          │
│ Risk Level: HIGH                                    │
│                                                     │
│ Reasoning: Attempting to exploit discovered         │
│ vulnerability CVE-2023-XXXX on target service       │
│                                                     │
│ Expected Outcome: Gain shell access to target       │
├─────────────────────────────────────────────────────┤
│ Execute this command? [y/N]:                        │
└─────────────────────────────────────────────────────┘
```

##  Supported Tools

### Reconnaissance
- **nmap**: Network scanning and service detection
- **masscan**: High-speed port scanning
- **netdiscover**: Network discovery
- **dnsenum**: DNS enumeration
- **theHarvester**: OSINT gathering
- **recon-ng**: Reconnaissance framework

### Vulnerability Scanning
- **OpenVAS**: Comprehensive vulnerability scanning
- **Nessus**: Professional vulnerability assessment
- **Nikto**: Web server scanner
- **wpscan**: WordPress security scanner
- **OWASP ZAP**: Web application security scanner

### Exploitation
- **Metasploit Framework**: Exploitation and post-exploitation
- **exploit-db**: Exploit database integration
- **searchsploit**: Local exploit search
- **BeEF**: Browser exploitation framework

### Web Application Testing
- **Burp Suite**: Web vulnerability scanner
- **sqlmap**: SQL injection automation
- **XSSer**: Cross-site scripting framework
- **wfuzz**: Web application fuzzer
- **dirb/gobuster**: Directory brute forcing

### Wireless Security
- **aircrack-ng**: WiFi security auditing
- **reaver**: WPS attack tool
- **wifite**: Automated wireless attack tool
- **kismet**: Wireless network detector

### Password Cracking
- **hashcat**: Advanced password recovery
- **John the Ripper**: Password cracking
- **hydra**: Network login cracker
- **medusa**: Parallel brute force tool

### Forensics
- **autopsy**: Digital forensics platform
- **volatility**: Memory forensics framework
- **binwalk**: Firmware analysis
- **foremost**: File carving

### Defensive Security
- **Suricata**: IDS/IPS engine
- **Snort**: Network intrusion detection
- **OSSEC**: Host-based intrusion detection
- **Wazuh**: Security monitoring platform

##  CLI Interface

The system features a beautiful, informative CLI interface:

```
╔══════════════════════════════════════════════════════════╗
║           Kali AI Command Chaining System                ║
╚══════════════════════════════════════════════════════════╝

 Security Objective
┌──────────────────────────────────────────────────────────┐
│ Perform comprehensive network reconnaissance of          │
│ 192.168.1.0/24                                           │
└──────────────────────────────────────────────────────────┘

 AI Agent Status: Executing
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Progress: ████████████████░░░░░░░░░░░░░░░░░░░░ 40%

 Current Command
┌──────────────────────────────────────────────────────────┐
│ nmap -sV -p- 192.168.1.0/24                              │
│ Tool: Nmap                                               │
│ Reasoning: Performing comprehensive port scan to         │
│ identify all open ports and service versions             │
└──────────────────────────────────────────────────────────┘

 Discoveries
┌─────────────┬──────────────────────────┬──────────────┐
│ Type        │ Details                  │ Severity     │
├─────────────┼──────────────────────────┼──────────────┤
│ Host        │ 192.168.1.10            │ Info         │
│ Service     │ SSH (22/tcp)            │ Info         │
│ Service     │ HTTP (80/tcp)           │ Info         │
│ Vulnerability│ Apache 2.4.49 RCE       │ Critical     │
└─────────────┴──────────────────────────┴──────────────┘
```

##  Project Structure

```
kali-ai-agent/
├── install.sh                 # Installation script
├── requirements.txt           # Python dependencies
├── config.yaml               # Configuration file
├── README.md                 # This file
├── ARCHITECTURE.md           # System architecture
├── IMPLEMENTATION_PLAN.md    # Development plan
├── LICENSE                   # License information
│
├── src/
│   ├── main.py              # Entry point
│   ├── cli/                 # CLI interface
│   ├── core/                # AI agent core
│   ├── llm/                 # LLM integration
│   ├── execution/           # Command execution
│   ├── safety/              # Safety system
│   ├── tools/               # Tool integrations
│   ├── feedback/            # Feedback loop
│   └── utils/               # Utilities
│
├── tests/                   # Test suite
├── examples/                # Example objectives
├── docs/                    # Documentation
└── logs/                    # Runtime logs
```

##  How It Works

### 1. Objective Parsing
The AI agent analyzes your security objective and breaks it down into actionable goals:

```
Objective: "Assess security of web application"
↓
Goals:
1. Discover web technologies
2. Enumerate directories and files
3. Scan for vulnerabilities
4. Test for common web attacks
5. Generate security report
```

### 2. Intelligent Command Generation
For each goal, the AI generates the optimal command based on:
- Current objective and progress
- Previous command results
- Discovered information
- Available tools
- Safety constraints

### 3. Dynamic Adaptation
The system adapts its strategy based on:
- **Success**: Continue with next logical step
- **Failure**: Try alternative approach
- **Discovery**: Pivot to investigate findings
- **Obstacle**: Backtrack and adjust strategy

### 4. Continuous Learning
Each command execution provides context for the next:

```
Command 1: nmap -sn 192.168.1.0/24
Result: 5 hosts discovered
↓
Command 2: nmap -sV -p- 192.168.1.10
Result: HTTP service on port 80, Apache 2.4.49
↓
Command 3: searchsploit Apache 2.4.49
Result: CVE-2023-XXXX RCE vulnerability found
↓
Command 4: [Requires Approval] msfconsole -x "use exploit/..."
```

**Never use against systems without explicit authorization.**

### Scope Management
Always define authorized scope in `config.yaml`:

```yaml
targets:
  allowed_networks:
    - 192.168.1.0/24
    - 10.0.0.0/8
  excluded_ips:
    - 192.168.1.1  # Gateway
    - 192.168.1.254  # Critical infrastructure
```

### Audit Trail
All commands are logged with:
- Timestamp
- Command executed
- Output received
- User approvals
- Discoveries made

Logs are stored in: `logs/sessions/<session-id>.json`

##  Documentation

- [Installation Guide](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [Configuration Reference](docs/configuration.md)
- [Safety Guidelines](docs/safety.md)
- [Architecture Overview](ARCHITECTURE.md)
- [Implementation Plan](IMPLEMENTATION_PLAN.md)
- [API Documentation](docs/api.md)
- [Troubleshooting](docs/troubleshooting.md)

##  Testing

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/

# Run safety tests
pytest tests/test_safety.py -v
```

### Development Setup

```bash
# Clone repository
git clone https://github.com/Dleifnesor/CLAI.git
cd kali-ai-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```


**Built with ❤️ for the security community**
