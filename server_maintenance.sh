#!/bin/bash
set -e

echo "🔧 Server Maintenance Script"
echo "============================"

# Function to handle apt locks
handle_apt_locks() {
    echo "🔧 Checking for apt locks..."
    
    # Kill any running apt processes
    if pgrep -x "apt" > /dev/null || pgrep -x "apt-get" > /dev/null; then
        echo "🛑 Killing apt processes..."
        sudo killall apt apt-get || true
        sleep 2
    fi
    
    # Remove lock files
    echo "🗑️  Removing lock files..."
    sudo rm -f /var/lib/apt/lists/lock || true
    sudo rm -f /var/cache/apt/archives/lock || true
    sudo rm -f /var/lib/dpkg/lock* || true
    sudo rm -f /var/lib/dpkg/lock-frontend || true
    
    echo "✅ Apt locks cleared"
}

# Function to update system packages
update_system() {
    echo "📦 Updating system packages..."
    handle_apt_locks
    sudo apt-get update
    sudo apt-get upgrade -y
    echo "✅ System updated"
}

# Function to install required packages
install_packages() {
    echo "📦 Installing required packages..."
    handle_apt_locks
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv rsync git curl wget
    echo "✅ Required packages installed"
}

# Function to check disk space
check_disk_space() {
    echo "💾 Checking disk space..."
    df -h
    echo ""
    echo "📁 Checking largest directories in /home/ubuntu:"
    du -h --max-depth=1 /home/ubuntu 2>/dev/null | sort -hr | head -10
}

# Function to check system resources
check_system_resources() {
    echo "🖥️  Checking system resources..."
    echo "Memory usage:"
    free -h
    echo ""
    echo "CPU usage:"
    top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1
    echo ""
    echo "Load average:"
    uptime
}

# Function to restart services
restart_services() {
    echo "🔄 Restarting services..."
    
    if [ -f "/etc/systemd/system/aiapp.service" ]; then
        echo "🔄 Restarting aiapp service..."
        sudo systemctl restart aiapp
        sudo systemctl status aiapp --no-pager -l
    else
        echo "⚠️  aiapp service not found"
    fi
}

# Function to clean up logs
cleanup_logs() {
    echo "🧹 Cleaning up logs..."
    
    # Clean up old log files
    sudo find /var/log -name "*.log" -mtime +7 -delete 2>/dev/null || true
    sudo find /var/log -name "*.gz" -mtime +30 -delete 2>/dev/null || true
    
    # Clean up journal logs
    sudo journalctl --vacuum-time=7d
    
    echo "✅ Logs cleaned up"
}

# Function to check project status
check_project_status() {
    echo "📁 Checking project status..."
    
    if [ -d "/home/ubuntu/ai-project-template" ]; then
        cd /home/ubuntu/ai-project-template
        
        echo "📍 Current directory: $(pwd)"
        echo "📦 Git status:"
        git status --porcelain || echo "Not a git repository"
        
        echo "🐍 Python environment:"
        if [ -d "venv" ]; then
            echo "✅ Virtual environment exists"
            source venv/bin/activate
            python --version
        else
            echo "❌ Virtual environment not found"
        fi
        
        echo "📋 Project files:"
        ls -la | head -10
        
    else
        echo "❌ Project directory not found"
    fi
}

# Main menu
show_menu() {
    echo ""
    echo "🔧 Server Maintenance Options:"
    echo "1. Handle apt locks"
    echo "2. Update system packages"
    echo "3. Install required packages"
    echo "4. Check disk space"
    echo "5. Check system resources"
    echo "6. Restart services"
    echo "7. Clean up logs"
    echo "8. Check project status"
    echo "9. Run all maintenance tasks"
    echo "0. Exit"
    echo ""
    read -p "Enter your choice (0-9): " choice
}

# Main execution
main() {
    case $1 in
        "locks")
            handle_apt_locks
            ;;
        "update")
            update_system
            ;;
        "install")
            install_packages
            ;;
        "disk")
            check_disk_space
            ;;
        "resources")
            check_system_resources
            ;;
        "restart")
            restart_services
            ;;
        "cleanup")
            cleanup_logs
            ;;
        "status")
            check_project_status
            ;;
        "all")
            handle_apt_locks
            update_system
            install_packages
            check_disk_space
            check_system_resources
            restart_services
            cleanup_logs
            check_project_status
            ;;
        *)
            # Interactive mode
            while true; do
                show_menu
                case $choice in
                    1) handle_apt_locks ;;
                    2) update_system ;;
                    3) install_packages ;;
                    4) check_disk_space ;;
                    5) check_system_resources ;;
                    6) restart_services ;;
                    7) cleanup_logs ;;
                    8) check_project_status ;;
                    9) 
                        handle_apt_locks
                        update_system
                        install_packages
                        check_disk_space
                        check_system_resources
                        restart_services
                        cleanup_logs
                        check_project_status
                        ;;
                    0) echo "👋 Goodbye!"; exit 0 ;;
                    *) echo "❌ Invalid choice. Please try again." ;;
                esac
            done
            ;;
    esac
}

# Run main function with arguments
main "$@" 