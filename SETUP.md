# Setup Instructions

## Prerequisites
- GitHub account
- Gmail account (for email notifications)
- Docker (optional)

## Email Notifications Setup

### Step 1: Enable 2-Factor Authentication on Gmail
1. Go to https://myaccount.google.com/
2. Click "Security" in the left menu
3. Enable 2-Step Verification

### Step 2: Generate App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer" (or your device)
3. Google will generate a 16-character password
4. Copy this password

### Step 3: Add GitHub Secrets
1. Go to your repository settings
2. Click "Secrets and variables" → "Actions"
3. Add these secrets:

```
EMAIL_USERNAME: your-email@gmail.com
EMAIL_PASSWORD: your-16-character-app-password
EMAIL_RECIPIENT: recipient@example.com (or same as USERNAME)
```

### Step 4: Verify Setup
1. Push code to main or develop branch
2. Go to Actions tab
3. Check if workflow runs and sends emails

---

## Docker Setup

### Build Docker Image
```bash
docker build -t ai-sdn-monitor:latest .
```

### Run Container
```bash
docker run -it --rm \
  -v $(pwd)/reports:/app/reports \
  ai-sdn-monitor:latest
```

### Using Docker Compose
```bash
docker-compose up -d
```

### View Container Logs
```bash
docker logs -f ai-sdn-monitor
```

### Stop Container
```bash
docker-compose down
```

---

## Local Testing

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test
```bash
pytest tests/test_network_monitoring.py::TestNetworkSignalMonitor::test_monitor_initialization -v
```

### Run with Coverage
```bash
pytest tests/ --cov=network_signal_monitoring --cov=network_monitoring --cov-report=html
```

### Run Demonstrations
```bash
python run_all.py
```

---

## GitHub Actions Monitoring

### View Workflow Status
1. Go to repository
2. Click "Actions" tab
3. Select workflow run to view details

### View Artifacts
1. Click workflow run
2. Scroll to "Artifacts" section
3. Download test results

### Email Notifications
- ✅ Receives email on test failure
- ✅ Receives email on test success
- Check spam folder if emails don't appear

---

## Troubleshooting

### Tests Not Running
- Verify `.github/workflows/test.yml` exists
- Check repository settings allow Actions
- Ensure branch is main or develop

### Email Notifications Not Sent
- Verify secrets are set correctly
- Check Gmail app password is valid
- Allow less secure app access (if using Gmail)
- Check workflow logs for errors

### Docker Build Fails
- Ensure Docker is installed: `docker --version`
- Check internet connection
- Try: `docker build --no-cache -t ai-sdn-monitor .`

### Container Won't Start
- Check logs: `docker logs ai-sdn-monitor`
- Verify volumes are writable
- Check port 8080 is available

---

## Next Steps

1. ✅ Setup email notifications
2. ✅ Push code to trigger workflow
3. ✅ Monitor test results
4. ✅ Deploy with Docker
5. ✅ Add custom monitoring logic

---

## Support

For issues or questions:
1. Check GitHub Actions logs
2. Review error messages
3. Verify all secrets are configured
4. Test locally: `python run_all.py`
