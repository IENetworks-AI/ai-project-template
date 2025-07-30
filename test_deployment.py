#!/usr/bin/env python3
"""
Deployment Test Script
Tests SSH connectivity and deployment readiness
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def check_ssh_key():
    """Check if SSH key is available"""
    print("\n🔑 Checking SSH Key...")
    
    # Check if we're in a GitHub Actions environment
    if os.getenv('GITHUB_ACTIONS'):
        print("✅ Running in GitHub Actions environment")
        ssh_key = os.getenv('ORACLE_SSH_KEY')
        if ssh_key:
            print("✅ ORACLE_SSH_KEY secret is available")
            return True
        else:
            print("❌ ORACLE_SSH_KEY secret is not available")
            return False
    else:
        print("⚠️  Not in GitHub Actions environment")
        print("   This script is designed for CI/CD testing")
        return False

def test_ssh_connection():
    """Test SSH connection to the server"""
    print("\n🌐 Testing SSH Connection...")
    
    # Test basic connectivity
    ping_result = run_command(
        "ping -c 1 139.185.33.139",
        "Ping server"
    )
    
    if not ping_result:
        print("❌ Cannot reach server - check network connectivity")
        return False
    
    # Test SSH connection (if we have the key)
    if check_ssh_key():
        ssh_result = run_command(
            "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -i ~/.ssh/oracle.key ubuntu@139.185.33.139 'echo \"SSH connection successful\"'",
            "SSH connection test"
        )
        return ssh_result
    
    return True

def check_deployment_files():
    """Check if deployment files exist"""
    print("\n📁 Checking Deployment Files...")
    
    required_files = [
        "deploy.sh",
        "start.sh", 
        "aiapp.service",
        "app.py",
        "requirements.txt",
        "config/config.yaml"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} required files for deployment")
        return False
    else:
        print("\n✅ All deployment files are present")
        return True

def check_python_environment():
    """Check Python environment"""
    print("\n🐍 Checking Python Environment...")
    
    # Check Python version
    python_result = run_command(
        "python --version",
        "Python version check"
    )
    
    # Check if requirements.txt exists and can be parsed
    if os.path.exists("requirements.txt"):
        print("✅ requirements.txt exists")
        
        # Try to install dependencies (dry run)
        pip_result = run_command(
            "pip install --dry-run -r requirements.txt",
            "Dependencies check"
        )
    else:
        print("❌ requirements.txt missing")
        return False
    
    return python_result

def main():
    """Main deployment test function"""
    print("🚀 Deployment Readiness Test")
    print("=" * 50)
    
    tests = [
        ("Deployment Files", check_deployment_files),
        ("Python Environment", check_python_environment),
        ("SSH Connectivity", test_ssh_connection)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Deployment Test Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Deployment should work.")
        print("\n🚀 Next Steps:")
        print("1. Push to main branch to trigger deployment")
        print("2. Monitor GitHub Actions workflow")
        print("3. Check server status after deployment")
    else:
        print("⚠️  Some tests failed. Please fix issues before deployment.")
        print("\n🔧 Common fixes:")
        print("1. Ensure ORACLE_SSH_KEY secret is configured in GitHub")
        print("2. Check server connectivity (139.185.33.139)")
        print("3. Verify all required files are present")
        print("4. Test SSH connection manually")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 