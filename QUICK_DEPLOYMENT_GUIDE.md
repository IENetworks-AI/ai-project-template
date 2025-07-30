# Quick Deployment Guide

## 🚀 Immediate Actions

### For the Current rsync Error
The error you encountered was because `rsync` wasn't installed on the GitHub Actions runner. This has been fixed in all deployment workflows. The workflow now properly installs rsync on the runner before using it.

### Current Workflow Status
✅ **Fixed Issues**:
- Merge conflict resolved
- rsync installation added to GitHub Actions runners
- Separate workflow files created
- Enhanced error handling with retries

## 📋 Available Workflows

### 1. **Test Deployment** (`test-deployment.yml`)
**Use this first** to check server status and connectivity
- Manual trigger only
- Tests SSH connection
- Checks server status
- Tests apt functionality

### 2. **Server Maintenance** (`server-maintenance.yml`)
**Use this for server issues**
- Manual trigger only
- Options: `fix-locks`, `restart-services`, `check-status`, `full-maintenance`

### 3. **Simple Deploy** (`deploy.yml`)
**Use this for code-only deployments**
- Triggers on push to main
- Manual trigger available
- Includes apt lock handling

### 4. **Deploy with Artifacts** (`deploy-with-artifacts.yml`)
**Use this for deployments with models**
- Triggers after successful data pipeline
- Manual trigger available
- Downloads model artifacts

## 🔧 Immediate Steps

### Step 1: Test Server Status
1. Go to GitHub Actions
2. Run `test-deployment.yml` workflow
3. Check the logs for any issues

### Step 2: Fix Any Issues Found
If the test shows issues:
- **Apt locks**: Run `server-maintenance.yml` → `fix-locks`
- **Service issues**: Run `server-maintenance.yml` → `restart-services`
- **General issues**: Run `server-maintenance.yml` → `check-status`

### Step 3: Deploy
- **Simple deployment**: Run `deploy.yml`
- **Deployment with models**: Run `deploy-with-artifacts.yml`

## 🚨 Common Commands

### On the Server (if you have direct access)
```bash
# Fix apt locks
sudo killall apt apt-get || true
sudo rm -f /var/lib/apt/lists/lock /var/cache/apt/archives/lock /var/lib/dpkg/lock* /var/lib/dpkg/lock-frontend || true

# Check service status
sudo systemctl status aiapp

# Restart service
sudo systemctl restart aiapp

# Check logs
sudo journalctl -u aiapp -f
```

### Using GitHub Actions
1. Go to Actions tab
2. Select workflow
3. Click "Run workflow"
4. Choose options if prompted

## ✅ Success Indicators

- SSH connection successful
- Apt working properly
- Service status shows "active (running)"
- Application responds on port 5000
- No error messages in logs

## 🆘 If Something Goes Wrong

1. **Check the logs** in the GitHub Actions workflow
2. **Run test-deployment.yml** to diagnose issues
3. **Use server-maintenance.yml** to fix server issues
4. **Check the documentation** in `docs/WORKFLOW_STRUCTURE.md`

## 📞 Quick Reference

| Issue | Solution |
|-------|----------|
| rsync not found | ✅ Fixed - workflows now install rsync on runner |
| apt locks | Run `server-maintenance.yml` → `fix-locks` |
| service not starting | Run `server-maintenance.yml` → `restart-services` |
| SSH connection failed | Check SSH key in GitHub secrets |
| deployment failed | Check logs and run `test-deployment.yml` |
| quick test | Run `quick-test.yml` to verify basic functionality | 