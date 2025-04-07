#!/bin/bash
set -e
set -o pipefail

# --- tdd-macos-setup: Prerequisites ---

# This script checks for and installs necessary tools for a TDD environment on macOS.

echo "Starting prerequisites setup..."

# Function to check if a command exists
command_exists() {
    command -v "$1" &>/dev/null
}

# Function to check and install a Homebrew package
install_brew_package() {
    local package_name="$1"
    local command_name="${2:-$1}" # Optional: command name might differ from package name

    echo "Checking for $package_name..."
    if ! command_exists "$command_name"; then
        echo "Installing $package_name..."
        if brew install "$package_name"; then
            echo "$package_name installed successfully."
        else
            echo "ERROR: Failed to install $package_name. Please check Homebrew output."
            exit 1
        fi
    else
        echo "$package_name is already installed."
    fi

    echo "Verifying $command_name installation..."
    if command_exists "$command_name"; then
        echo "$command_name found: $(command -v "$command_name")"
    else
        echo "ERROR: $command_name verification failed after installation attempt."
        exit 1
    fi
    echo "---" # Separator
}

# Function to check and install a Homebrew Cask package
install_brew_cask() {
    local cask_name="$1"
    local app_name="$2" # e.g., "Visual Studio Code"
    local app_path="/Applications/$app_name.app"

    echo "Checking for $app_name..."
    if [ ! -d "$app_path" ]; then
        echo "Installing $cask_name..."
        if brew install --cask "$cask_name"; then
            echo "$cask_name installed successfully."
        else
            echo "ERROR: Failed to install $cask_name. Please check Homebrew output."
            exit 1
        fi
    else
        echo "$app_name is already installed."
    fi

    echo "Verifying $app_name installation..."
    if [ -d "$app_path" ]; then
        echo "$app_name found at $app_path"
    else
        echo "ERROR: $app_name verification failed after installation attempt."
        exit 1
    fi
    echo "---" # Separator
}

# 1. Check/Install Homebrew
echo "Checking for Homebrew..."
if ! command_exists brew; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Add brew to PATH for the current script execution (needed on Apple Silicon)
    if [[ "$(uname -m)" == "arm64" ]]; then
        # Attempt to add to common shell profiles if they exist
        if [ -f "$HOME/.zshrc" ]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >>"$HOME/.zshrc"
            echo "Added Homebrew setup to ~/.zshrc"
        fi
        if [ -f "$HOME/.bash_profile" ]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >>"$HOME/.bash_profile"
            echo "Added Homebrew setup to ~/.bash_profile"
        fi
        # Evaluate for the current script session
        eval "$(/opt/homebrew/bin/brew shellenv)"
        echo "Configured Homebrew environment for this session (Apple Silicon)."
    fi
    echo "Verifying Homebrew installation..."
    if command_exists brew; then
        echo "Homebrew installed successfully: $(command -v brew)"
    else
        echo "ERROR: Homebrew installation failed. Please check the output above and ensure it's added to your PATH."
        exit 1
    fi
else
    echo "Homebrew is already installed: $(command -v brew)"
    echo "Updating Homebrew..."
    brew update
fi
echo "---" # Separator

# 2. Check/Install Git
install_brew_package "git"

# 3. Check/Install Python
install_brew_package "python" "python3" # Command is python3

# 4. Check/Install Node.js
install_brew_package "node"

# 5. Check/Install uv (Python package manager)
install_brew_package "uv"

# 6. Check/Install Visual Studio Code
install_brew_cask "visual-studio-code" "Visual Studio Code"

# 7. Check 'code' command in PATH
echo "Checking for 'code' command in PATH..."
if ! command_exists code; then
    echo "----------------------------------------------------------------------"
    echo "WARNING: The 'code' command is not available in your PATH."
    echo "         This command allows you to open files and folders in VS Code"
    echo "         directly from the terminal."
    echo ""
    echo "To install it:"
    echo "1. Open Visual Studio Code."
    echo "2. Open the Command Palette (Cmd+Shift+P or F1)."
    echo "3. Type 'Shell Command: Install 'code' command in PATH' and select it."
    echo "4. You MUST restart your terminal or source your profile file"
    echo "   (e.g., 'source ~/.zshrc' or 'source ~/.bash_profile')"
    echo "   for the change to take effect."
    echo ""
    echo "See VS Code documentation for more details:"
    echo "https://code.visualstudio.com/docs/setup/mac#_launching-from-the-command-line"
    echo "----------------------------------------------------------------------"
else
    echo "'code' command found: $(command -v code)"
fi
echo "---" # Separator

echo "Prerequisites setup script finished successfully."
echo "IMPORTANT: If VS Code was installed or updated, please reload the VS Code window"
echo "           (Cmd+Shift+P or F1 -> 'Developer: Reload Window')"
echo "           to ensure all changes and extensions are recognized."
