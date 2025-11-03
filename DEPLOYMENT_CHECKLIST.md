# CLAI Deployment Checklist

## Pre-Deployment Verification

### ✅ System Requirements
- [ ] Kali Linux 2023.1 or later
- [ ] Python 3.10+ installed
- [ ] pip3 available
- [ ] Root/sudo access
- [ ] Internet connection (for Ollama model download)

### ✅ Installation Steps

1. **Clone Repository**
```bash
git clone https://github.com/Dleifnesor/CLAI.git
cd CLAI
```

2. **Run Installer**
```bash
chmod +x install.sh
sudo ./install.sh
```

The installer will:
- [x] Check Python version
- [x] Create virtual environment
- [x] Install Python dependencies
- [x] Install/configure Ollama
- [x] Download dolphin3-abliterated:8b model
- [x] Verify Kali tools
- [x] Create directories
- [x] Set permissions
- [x] Install global `clai` command

3. **Verify Installation**
```bash
# Check clai command
which clai
# Should output: /usr/local/bin/clai

# Test help
clai --help

# Check Ollama
systemctl status ollama
ollama list
```

### ✅ Configuration

1. **Review config.yaml**
```bash
nano config.yaml
```

2. **Set Target Scope**
```yaml
targets:
  allowed_networks:
    - 192.168.1.0/24  # Your authorized networks
    - 10.0.0.0/8
  excluded_ips:
    - 192.168.1.1  # Critical systems to exclude
```

3. **Configure Safety Mode**
```yaml
safety:
  mode: semi-autonomous  # Recommended for first use
```

4. **Set Ollama Server** (if using remote)
```yaml
llm:
  server:
    host: 192.168.1.100  # Remote Ollama server IP
```

### ✅ First Run Test

```bash
# Simple test objective
clai "scan localhost for open ports"
```

Expected output:
- Banner display
- Objective shown
- AI initialization
- Command generation
- Execution
- Results display
- Report generation

### ✅ Functional Tests

**Test 1: Safe Command Auto-Execution**
```bash
clai "ping 8.8.8.8 to test connectivity"
```
- Should execute without approval

**Test 2: High-Risk Approval**
```bash
clai "test for sql injection on http://testsite.local"
```
- Should request approval before executing sqlmap

**Test 3: Blacklist Enforcement**
```bash
# This should be blocked
clai "shutdown the system"
```
- Should refuse to execute

**Test 4: Session Management**
```bash
# Start a scan
clai "scan 192.168.1.0/24"
# Interrupt with Ctrl+C
# List sessions
clai --list-sessions
# Resume
clai --resume <session-id>
```

### ✅ Component Verification

**Configuration System**
```bash
python3 -c "from src.utils.config import ConfigLoader; c = ConfigLoader(); c.validate(); print('✓ Config OK')"
```

**LLM Connection**
```bash
python3 -c "import asyncio; from src.llm.client import OllamaClient; from src.utils.config import ConfigLoader; c = ConfigLoader(); client = OllamaClient(c.get_llm_config()); asyncio.run(client.test_connection()) and print('✓ Ollama OK')"
```

**Safety System**
```bash
python3 -c "from src.safety.validator import SafetyValidator; from src.utils.config import ConfigLoader; c = ConfigLoader(); v = SafetyValidator(c.get_safety_config()); print('✓ Safety OK')"
```

---

## 🔍 Post-Deployment Monitoring

### Check Logs
```bash
# Main log
tail -f logs/kali-ai-agent.log

# Session logs
ls -lh logs/sessions/
```

### Monitor Resource Usage
```bash
# During execution
htop
# Watch for CPU/memory usage
```

### Verify Ollama
```bash
# Check service
systemctl status ollama

# Monitor Ollama logs
journalctl -u ollama -f
```

---

## 🛡️ Security Checklist

### Before First Use
- [ ] Review and understand safety features
- [ ] Configure authorized target scope
- [ ] Set up excluded IPs for critical systems
- [ ] Review blacklist in config.yaml
- [ ] Ensure you have written authorization for targets

### During Use
- [ ] Monitor command executions
- [ ] Review approval requests carefully
- [ ] Check discoveries for sensitive data
- [ ] Verify targets are in scope
- [ ] Watch for unexpected behavior

### After Use
- [ ] Review session logs
- [ ] Check for any errors
- [ ] Verify no unauthorized commands executed
- [ ] Archive important sessions
- [ ] Clean up temporary files

---

## 🐛 Troubleshooting

### Issue: Virtual Environment Error
```bash
# Remove corrupted venv
rm -rf venv
# Reinstall
sudo ./install.sh
```

### Issue: Ollama Not Running
```bash
systemctl start ollama
systemctl enable ollama
```

### Issue: Model Not Found
```bash
ollama pull huihui_ai/dolphin3-abliterated:8b
```

### Issue: Permission Denied
```bash
# Run with sudo
sudo clai "your objective"
```

### Issue: Tool Not Found
```bash
# Install missing tools
sudo apt update
sudo apt install nmap masscan nikto sqlmap
```

---

## 📋 Production Deployment

### For Team Use

1. **Centralized Ollama Server**
```yaml
# config.yaml on each workstation
llm:
  server:
    host: ollama-server.local
    port: 11434
```

2. **Shared Configuration**
```bash
# Create team config
cp config.yaml /etc/kali-ai-agent/config.yaml
# Point to it
clai --config /etc/kali-ai-agent/config.yaml "objective"
```

3. **Centralized Logging**
```yaml
logging:
  file: /var/log/kali-ai-agent/team.log
```

### For Individual Use

1. **Local Installation** (default)
2. **Personal Configuration**
3. **Local Logging**

---

## ✅ Deployment Complete

Once all checks pass:

- [x] System installed
- [x] Configuration reviewed
- [x] Tests passed
- [x] Documentation read
- [x] Safety understood
- [x] Authorization obtained

**You're ready to use CLAI!**

```bash
clai "your first objective"
```

---

## 📞 Support

- **Issues**: https://github.com/Dleifnesor/CLAI/issues
- **Documentation**: See docs/ directory
- **Examples**: See examples/ directory

---

**Remember: Only use on authorized targets!**