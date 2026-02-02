# 🚀 Cloud GPU Deployment Guide (with zrok)

## Quick Start (3 Minutes)

### Step 1: Get Your Free zrok Token
1. Go to: https://api.zrok.io/
2. Click **"Sign Up"** (100% free, no credit card)
3. Verify email and log in
4. Copy your **zrok token** (shown on dashboard)

### Step 2: Deploy to Google Colab
1. Open Google Colab: https://colab.research.google.com
2. Click **"New Notebook"**
3. Go to **Runtime** → **Change runtime type** → Select **T4 GPU** → **Save**
4. Copy the entire contents of `cloud/COLAB_DEPLOY_ZROK.py`
5. Paste into the first cell
6. **IMPORTANT**: Replace `YOUR_ZROK_TOKEN_HERE` with your actual token
7. Click **Run** (▶️ button)

### Step 3: Wait & Copy URL
- Wait 2-3 minutes for model loading
- You'll see:
  ```
  ✅ SERVER READY
  🌐 Public URL: https://yw52v5hhadw7.share.zrok.io
  ```
- **COPY THIS URL** — it's persistent and won't change!

### Step 4: Configure Local Client
Add to your `.env` file:
```env
COLAB_SERVER_URL=https://abc123.share.zrok.io
```

Or in terminal:
```bash
# Windows CMD
set COLAB_SERVER_URL=https://abc123.share.zrok.io

# Windows PowerShell
$env:COLAB_SERVER_URL="https://abc123.share.zrok.io"
```

### Step 5: Test It
```bash
python scripts/test_cloud.py
```

---

## Advantages of zrok vs ngrok

| Feature | zrok | ngrok |
|---------|------|-------|
| **URL Persistence** | ✅ Same URL every time | ❌ New random URL each restart |
| **Free Tier** | ✅ Unlimited | ⚠️ 40 hours/month |
| **Auth Required** | ✅ Simple token | ⚠️ More complex setup |
| **Cost** | **$0 forever** | **$0 (with limits)** |

---

## Usage in Your Code

**No changes needed!** Your existing code already works:

```python
from tools.resume_parser import ResumeParserTool

parser = ResumeParserTool()
resume = parser.execute(resume_text)
# Automatically uses cloud GPU if COLAB_SERVER_URL is set
```

---

## Performance

| Method | Hardware | Time |
|--------|----------|------|
| Local Ollama | CPU (gemma2:2b) | 4-5s |
| **Cloud Colab** | **T4 GPU (Llama-3-8B)** | **2-5s** |

**Real benefit**: Better extraction quality (Llama-3-8B >> gemma2:2b)

---

## Troubleshooting

### "zrok enable failed"
- Double-check your token (no extra spaces)
- Make sure you verified your email

### "Server offline" in health check
- Check Colab notebook is still running
- Restart the Colab cell if needed
- zrok URLs expire after 12 hours (just restart)

### "Timeout after 30s"
- Colab may be loading model — wait 1 minute and retry
- Check internet connection

---

## Important Notes

1. **Keep Colab Tab Open**: Colab disconnects if you close the tab
2. **12-Hour Limit**: Free Colab sessions auto-terminate after ~12 hours
3. **Persistent URL**: Your zrok URL stays the same, even if you restart
4. **No Credit Card**: 100% free, no payment info needed

---

##  Next Steps

After deployment:
1. Run `python scripts/cli_chat.py`
2. Parse a resume and see cloud acceleration
3. Check `client.get_stats()` to see performance metrics
