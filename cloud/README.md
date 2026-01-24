# Cloud GPU Setup Guide

## Overview
This guide explains how to deploy the Cyno Resume Parser on Google Colab's free T4 GPU to achieve **18x faster** resume parsing (90s → <5s).

---

## Step 1: Deploy to Google Colab

### 1.1 Open Colab
- Go to: https://colab.research.google.com
- Click **New Notebook**

### 1.2 Enable GPU
- Click **Runtime** → **Change runtime type**
- Set **Hardware accelerator** to **T4 GPU**
- Click **Save**

### 1.3 Deploy Server
Paste this into the first cell and run:

```python
# Clone repository (if needed) or upload colab_server.py directly
!wget https://raw.githubusercontent.com/<YOUR_REPO>/job-agent-production/cloud/colab_server.py

# Run server
from colab_server import start_server
start_server()  # Uses free ngrok tier
```

**Alternative:** Copy-paste the entire contents of `cloud/colab_server.py` into a cell and run.

### 1.4 Get Public URL
After 2-3 minutes, you'll see:
```
✅ SERVER READY
🌐 Public URL: https://abc123.ngrok.io
```

**Copy this URL** — you'll need it for local configuration.

---

## Step 2: Configure Local Client

### 2.1 Set Environment Variable (Recommended)
Add to your `.env` file:
```env
COLAB_SERVER_URL=https://abc123.ngrok.io
```

Or set temporarily in terminal:
```bash
# Windows (CMD)
set COLAB_SERVER_URL=https://abc123.ngrok.io

# Windows (PowerShell)
$env:COLAB_SERVER_URL="https://abc123.ngrok.io"

# Linux/Mac
export COLAB_SERVER_URL="https://abc123.ngrok.io"
```

### 2.2 Test Connection
Run this test script:

```python
from cloud.cloud_client import CloudClient

client = CloudClient()
health = client.health_check()

if health['cloud_available']:
    print(f"✅ Cloud GPU online! Response time: {health['response_time_ms']:.0f}ms")
    print(f"   GPU available: {health['gpu_available']}")
else:
    print(f"❌ Cloud offline: {health['error']}")
    print("   Will use local Ollama fallback")
```

---

## Step 3: Use in Production

Your existing code **already works** — no changes needed!

```python
from tools.resume_parser import ResumeParserTool

parser = ResumeParserTool()
resume = parser.execute(resume_text)
# Automatically uses cloud GPU if available, falls back to local Ollama
```

---

## Performance Benchmarks

| Method | Hardware | Time | Speedup |
|--------|----------|------|---------|
| Local Ollama | CPU (gemma2:2b) | 90s | 1x |
| **Cloud Colab** | **T4 GPU (Llama-3-8B)** | **~5s** | **18x** |

---

## Troubleshooting

### Issue: "No server URL configured"
**Fix:** Set `COLAB_SERVER_URL` environment variable (see Step 2.1)

### Issue: "Connection error: Name or service not known"
**Fix:** Check if ngrok URL is correct. Restart Colab server if needed.

### Issue: "Timeout after 30s"
**Fix:** 
1. Check Colab notebook is still running
2. Increase timeout: `CloudClient(timeout=60)`
3. Colab may be rate-limiting — wait 1 minute and retry

### Issue: Colab disconnected after 12 hours
**Fix:** This is expected. Free Colab sessions auto-terminate. Simply restart the server (Step 1.3).

---

## Advanced: Persistent URLs with ngrok Auth Token

Free ngrok gives you random URLs that change each restart. For persistent URLs:

1. Get free auth token: https://dashboard.ngrok.com/get-started/your-authtoken
2. Modify line in `colab_server.py`:
   ```python
   start_server(ngrok_token="YOUR_TOKEN_HERE")
   ```
3. Now you get a static subdomain (e.g., `https://cyno-parser.ngrok.io`)

---

## Cost Analysis

| Component | Cost |
|-----------|------|
| Google Colab T4 GPU | **$0** (15 hours/day free) |
| ngrok Tunneling | **$0** (40 hours/month free) |
| **Total** | **$0** |

**No credit card required.**

---

## Security Notes

1. **Data Privacy**: Resume data is sent to Colab (Google's servers) temporarily. Do NOT use for highly sensitive data.
2. **Public URLs**: ngrok URLs are publicly accessible. Do NOT share them publicly.
3. **Production Use**: For production, consider self-hosting on a cloud VM or upgrading to paid ngrok/Colab.

---

## Next Steps

- Monitor performance: `client.get_stats()`
- Test with multiple resumes
- Update `jan_roadmap.md` to mark Phase 6.2 complete
