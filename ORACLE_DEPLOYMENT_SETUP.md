# Oracle Deployment Setup Guide

This guide will help you set up the Oracle Cloud Infrastructure deployment for your ML pipeline using the proven rsync-based deployment method.

## 🔑 Required GitHub Secret

You only need to configure **ONE** secret in your GitHub repository:

### Step 1: Access GitHub Repository Settings

1. Go to your GitHub repository
2. Click on **Settings** tab
3. Click on **Secrets and variables** → **Actions** in the left sidebar
4. Click **New repository secret** to add the secret

### Step 2: Add the Required Secret

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `ORACLE_SSH_KEY` | Your SSH private key content | Your SSH private key (see instructions below) |

## 🔐 SSH Key Setup

### Option 1: Generate New SSH Key

```bash
# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# Copy the public key to Oracle server
ssh-copy-id ubuntu@139.185.33.139

# Copy the private key content for GitHub secret
cat ~/.ssh/id_rsa
```

### Option 2: Use Existing SSH Key

```bash
# Copy your existing private key content
cat ~/.ssh/id_rsa
```

**Important**: Copy the ENTIRE content of the private key file (including the `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----` lines).

## 🚀 Test SSH Connection

Before adding the secret, test your SSH connection:

```bash
ssh ubuntu@139.185.33.139
```

If successful, you should be able to connect to the Oracle server.

## 📋 Secret Value Summary

Here's the exact value to use:

- **ORACLE_SSH_KEY**: [Your private key content]

## ✅ Verification

After adding the secret:

1. Push a change to the `main` branch
2. Go to **Actions** tab in your repository
3. Check that the deployment job runs successfully
4. You should see "Oracle deployment secrets found - proceeding with deployment"

## 🚀 Deployment Process

The updated deployment process:

1. **SSH Setup**: Configures SSH connection to Oracle server
2. **rsync Installation**: Installs rsync on both runner and server
3. **Code Deployment**: Uses rsync to deploy all files to Oracle server
4. **Environment Setup**: Creates virtual environment and installs dependencies
5. **Service Configuration**: Sets up systemd service for ML pipeline
6. **Verification**: Checks that deployment was successful

## 🔧 Troubleshooting

### "missing server host" Error
- Make sure `ORACLE_SSH_KEY` secret is set correctly
- Check that the secret name is exactly `ORACLE_SSH_KEY` (case sensitive)

### SSH Connection Failed
- Verify your SSH key is added to the Oracle server
- Test SSH connection manually: `ssh ubuntu@139.185.33.139`
- Ensure the Oracle server is running and accessible

### rsync Installation Issues
- The deployment automatically handles apt locks and dpkg interruptions
- rsync is installed on both the GitHub Actions runner and Oracle server
- Full paths are used to ensure rsync is found

### Permission Denied
- Check that your SSH key has the correct permissions
- Ensure the target directory exists and is writable

## 📞 Support

If you encounter issues:
1. Check the GitHub Actions logs for detailed error messages
2. Verify the `ORACLE_SSH_KEY` secret is set correctly
3. Test SSH connection manually
4. Ensure Oracle server is running and accessible

## 🎯 Benefits of This Approach

- ✅ **Proven Method**: Uses the same deployment approach that works for you
- ✅ **Simplified Configuration**: Only one secret required
- ✅ **Robust Error Handling**: Handles apt locks and dpkg interruptions
- ✅ **Complete Deployment**: Deploys entire project with models
- ✅ **Service Management**: Sets up systemd service for ML pipeline
- ✅ **Verification**: Checks deployment success

---

**Note**: The pipeline will automatically skip Oracle deployment if the secret is not configured, so your ML pipeline will still work for local development and testing. 