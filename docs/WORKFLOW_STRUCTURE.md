# GitHub Actions Workflow Structure

This document explains the new workflow structure that separates concerns and provides better error handling.

## Workflow Files

### 1. `data_pipeline.yml` - Oracle AI Pipeline CI/CD
**Purpose**: Handles the data processing and model training pipeline
**Triggers**: 
- Push to main branch
- Pull requests to main branch

**Jobs**:
- `test`: Runs unit tests
- `preprocess`: Processes data and creates artifacts
- `train`: Trains models and creates model artifacts

**Output**: Creates artifacts that can be used by deployment workflows

### 2. `deploy.yml` - Deploy to Oracle Server
**Purpose**: Simple deployment without artifacts
**Triggers**:
- Push to main branch
- Manual trigger (workflow_dispatch)

**Jobs**:
- `deploy`: Deploys code and restarts services

**Features**:
- Handles apt locks with retry mechanism
- Verifies deployment success
- Includes health checks

### 3. `deploy-with-artifacts.yml` - Deploy with Data Pipeline Artifacts
**Purpose**: Deploys with artifacts from the data pipeline
**Triggers**:
- Automatic after successful data pipeline completion
- Manual trigger (workflow_dispatch)

**Jobs**:
- `deploy-with-artifacts`: Downloads artifacts and deploys

**Features**:
- Downloads model artifacts from data pipeline
- Downloads processed data artifacts
- Enhanced error handling with retries
- Verifies artifact deployment

### 4. `server-maintenance.yml` - Server Maintenance
**Purpose**: Fix server issues and perform maintenance
**Triggers**: Manual trigger only (workflow_dispatch)

**Actions Available**:
- `fix-locks`: Fix apt locks
- `restart-services`: Restart application services
- `check-status`: Check server status
- `full-maintenance`: Complete system maintenance

## Usage Guide

### For Normal Development
1. **Data Pipeline**: Automatically runs on push/PR to main
2. **Deployment**: Use `deploy.yml` for simple deployments
3. **Deployment with Models**: Use `deploy-with-artifacts.yml` after data pipeline completes

### For Server Issues
1. **Apt Locks**: Use `server-maintenance.yml` with `fix-locks` action
2. **Service Issues**: Use `server-maintenance.yml` with `restart-services` action
3. **System Issues**: Use `server-maintenance.yml` with `full-maintenance` action

### Manual Triggers
- Go to Actions tab in GitHub
- Select the desired workflow
- Click "Run workflow"
- Choose appropriate options

## Error Handling

### Apt Lock Issues
The workflows now include robust handling of apt locks:
- Kills running apt processes
- Removes lock files
- Implements retry mechanisms
- Provides detailed logging

### Deployment Verification
All deployment workflows include:
- SSH connection testing
- Service status verification
- Health endpoint checks
- Artifact verification (where applicable)

## Best Practices

1. **Use the right workflow for your needs**:
   - Simple code changes: `deploy.yml`
   - Model updates: `deploy-with-artifacts.yml`
   - Server issues: `server-maintenance.yml`

2. **Monitor workflow logs** for detailed error information

3. **Use manual triggers** when automatic workflows fail

4. **Check server status** before and after deployments

## Troubleshooting

### Common Issues

1. **Apt Lock Errors**:
   - Use `server-maintenance.yml` → `fix-locks`
   - Check for running apt processes
   - Use `test-deployment.yml` to verify apt functionality

2. **SSH Connection Issues**:
   - Verify SSH key in GitHub secrets
   - Check server accessibility
   - Use `test-deployment.yml` to test connection

3. **Service Not Starting**:
   - Use `server-maintenance.yml` → `check-status`
   - Check logs with `sudo journalctl -u aiapp`
   - Use `server-maintenance.yml` → `restart-services`

4. **Artifact Download Issues**:
   - Ensure data pipeline completed successfully
   - Check artifact retention settings

5. **rsync Command Not Found**:
   - Fixed: All deployment workflows now install rsync on the runner
   - This was a GitHub Actions runner issue, not a server issue

### Step-by-Step Troubleshooting

1. **First, test basic connectivity**:
   - Run `test-deployment.yml` workflow
   - This will check SSH connection and server status

2. **If apt locks are the issue**:
   - Run `server-maintenance.yml` → `fix-locks`
   - Then run `test-deployment.yml` again to verify

3. **If services are not running**:
   - Run `server-maintenance.yml` → `check-status`
   - Then run `server-maintenance.yml` → `restart-services`

4. **For deployment issues**:
   - Use `deploy.yml` for simple deployments
   - Use `deploy-with-artifacts.yml` for deployments with models
   - Check logs for specific error messages 