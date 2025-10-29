#!/bin/bash

# Kali AI Command Chaining System - Installation Script
# This script installs dependencies, configures Ollama, and sets up the system

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}     Kali AI Command Chaining System - Installer      ${BLUE}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_warning "This script should be run as root for full functionality"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Check system requirements
check_requirements() {
    print_info "Checking system requirements..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    REQUIRED_VERSION="3.10"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        print_error "Python 3.10 or higher is required (found $PYTHON_VERSION)"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION found"
    
    # Check if pip is installed
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed"
        exit 1
    fi
    
    print_success "pip3 found"
}

# Install Python dependencies
install_python_deps() {
    print_info "Installing Python dependencies..."
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    print_success "Python dependencies installed"
}

# Check and install Ollama
install_ollama() {
    print_info "Checking Ollama installation..."
    
    if command -v ollama &> /dev/null; then
        print_success "Ollama is already installed"
        return 0
    fi
    
    print_info "Ollama not found. Installing..."
    
    # Install Ollama
    curl -fsSL https://ollama.ai/install.sh | sh
    
    if [ $? -eq 0 ]; then
        print_success "Ollama installed successfully"
    else
        print_error "Failed to install Ollama"
        exit 1
    fi
}

# Configure Ollama server
configure_ollama() {
    print_info "Configuring Ollama..."
    
    # Ask for server configuration
    echo ""
    echo "Ollama Server Configuration:"
    echo "  - Leave blank for local installation"
    echo "  - Enter IP address for remote server"
    echo ""
    read -p "Ollama server IP (or press Enter for localhost): " OLLAMA_HOST
    
    if [ -z "$OLLAMA_HOST" ]; then
        OLLAMA_HOST="localhost"
        print_info "Using local Ollama server"
        
        # Start Ollama service if local
        if command -v systemctl &> /dev/null; then
            print_info "Starting Ollama service..."
            systemctl start ollama 2>/dev/null || true
            systemctl enable ollama 2>/dev/null || true
        fi
    else
        print_info "Using remote Ollama server at $OLLAMA_HOST"
    fi
    
    # Update config.yaml with server address
    if [ -f "config.yaml" ]; then
        sed -i "s/host: localhost/host: $OLLAMA_HOST/" config.yaml
        print_success "Configuration updated"
    fi
}

# Pull the LLM model
pull_model() {
    print_info "Checking for dolphin3-abliterated:8b model..."
    
    # Check if model exists
    if ollama list | grep -q "huihui_ai/dolphin3-abliterated:8b"; then
        print_success "Model already downloaded"
        return 0
    fi
    
    print_info "Downloading dolphin3-abliterated:8b model..."
    print_warning "This may take a while depending on your connection..."
    
    ollama pull huihui_ai/dolphin3-abliterated:8b
    
    if [ $? -eq 0 ]; then
        print_success "Model downloaded successfully"
    else
        print_error "Failed to download model"
        print_info "You can download it later with: ollama pull huihui_ai/dolphin3-abliterated:8b"
    fi
}

# Verify tool availability
verify_tools() {
    print_info "Verifying Kali Linux tools..."
    
    TOOLS=(
        "nmap"
        "masscan"
        "nikto"
        "sqlmap"
        "hydra"
        "john"
        "hashcat"
        "aircrack-ng"
        "msfconsole"
    )
    
    MISSING_TOOLS=()
    
    for tool in "${TOOLS[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            MISSING_TOOLS+=("$tool")
        fi
    done
    
    if [ ${#MISSING_TOOLS[@]} -eq 0 ]; then
        print_success "All core tools are available"
    else
        print_warning "Some tools are missing: ${MISSING_TOOLS[*]}"
        print_info "Install them with: apt install ${MISSING_TOOLS[*]}"
    fi
}

# Create necessary directories
create_directories() {
    print_info "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p logs/sessions
    mkdir -p /tmp/kali-ai-agent
    
    print_success "Directories created"
}

# Set up permissions
setup_permissions() {
    print_info "Setting up permissions..."
    
    chmod +x install.sh
    chmod -R 755 src/
    
    print_success "Permissions configured"
}

# Create launcher script
create_launcher() {
    print_info "Creating launcher script..."
    
    cat > kali-ai-agent << 'EOF'
#!/bin/bash
# Kali AI Agent Launcher

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Run the application
python3 -m src.main "$@"
EOF
    
    chmod +x kali-ai-agent
    
    print_success "Launcher script created"
}

# Install global command
install_global_command() {
    print_info "Installing global 'clai' command..."
    
    INSTALL_DIR=$(pwd)
    
    # Create global wrapper script
    cat > /usr/local/bin/clai << EOF
#!/bin/bash
# CLAI - Kali AI Command Chaining System Global Launcher

# Installation directory
INSTALL_DIR="$INSTALL_DIR"

# Change to installation directory
cd "\$INSTALL_DIR"

# Activate virtual environment
source venv/bin/activate

# Run the application with all arguments
python3 -m src.main "\$@"
EOF
    
    chmod +x /usr/local/bin/clai
    
    # Verify installation
    if command -v clai &> /dev/null; then
        print_success "Global 'clai' command installed successfully"
        print_info "You can now use: clai \"your objective\""
    else
        print_error "Failed to install global command"
        print_info "You can still use: ./kali-ai-agent run \"your objective\""
    fi
}

# Run tests
run_tests() {
    print_info "Running basic tests..."
    
    # Test configuration loading
    python3 -c "from src.utils.config import ConfigLoader; c = ConfigLoader(); c.validate()" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        print_success "Configuration test passed"
    else
        print_warning "Configuration test failed - please check config.yaml"
    fi
}

# Print completion message
print_completion() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}              Installation Complete!                    ${GREEN}║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Usage Examples:"
    echo "  ${BLUE}clai \"perform smb vulnerability check on 10.5.0.0/24\"${NC}"
    echo "  ${BLUE}clai \"scan network 192.168.1.0/24 for open ports\"${NC}"
    echo "  ${BLUE}clai \"test web application at https://target.com\"${NC}"
    echo ""
    echo "Additional Commands:"
    echo "  clai --help              Show help information"
    echo "  clai --list-sessions     List all saved sessions"
    echo "  clai --resume <id>       Resume a previous session"
    echo ""
    echo "Configuration:"
    echo "  - Edit config.yaml to customize settings"
    echo "  - Logs stored in: logs/"
    echo "  - Sessions saved in: logs/sessions/"
    echo ""
    echo "Documentation:"
    echo "  - README.md - Quick start guide"
    echo "  - ARCHITECTURE.md - System architecture"
    echo "  - docs/ - Detailed documentation"
    echo ""
    print_warning "Remember: Only use on authorized targets!"
    echo ""
}

# Main installation flow
main() {
    print_header
    
    check_root
    check_requirements
    install_python_deps
    install_ollama
    configure_ollama
    pull_model
    verify_tools
    create_directories
    setup_permissions
    create_launcher
    install_global_command
    run_tests
    print_completion
}

# Run main installation
main