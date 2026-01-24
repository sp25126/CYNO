# 🛠️ CYNO SETUP GUIDE (From Scratch to Production)
**Level:** Beginner to Pro  
**Goal:** Get the Cyno Job Agent running on your machine in 5 minutes.

---

## 🏗️ Prerequisites
Before starting, ensure you have:
1.  **Python 3.10+** installed. (Open terminal and type `python --version`).
2.  **Git** installed. (Type `git --version`).
3.  **Google Account** (for free Cloud Brain GPU on Colab).

---

## 🚀 Step 1: Download the Agent
1.  Open your terminal or command prompt.
2.  Clone the repository:
    ```bash
    git clone https://github.com/sp25126/CYNO.git
    cd CYNO
    ```

---

## ⚙️ Step 2: Set Up the Environment
We will create an isolated space for the agent so it doesn't conflict with other apps.

### Windows
```bash
# 1. Create the environment
python -m venv venv

# 2. Activate it (You will see (venv) in your prompt)
venv\Scripts\activate

# 3. Install the Brain Requirements
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Mac/Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

## 🧠 Step 3: Connect the Cloud Brain (Optional but Recommended)
For high-precision Resume Parsing (OCR) and Smart Email generation, we use Google Colab (Free GPU).

1.  **Go to Google Colab**: [colab.research.google.com](https://colab.research.google.com)
2.  **Upload File**: Click `Upload` -> Select `cloud/COLAB_DEPLOY_OCR.py` from the `CYNO` folder you downloaded.
3.  **Run**: Click `Runtime` -> `Run all`.
4.  **Get URL**: Scroll to the bottom of the output. You will see a URL like `https://xxxx-xx-xx-xx.ngrok-free.app`.
5.  **Save URL**:
    -   Create a file named `.env` in the `CYNO` folder.
    -   Add this line:
        ```
        COLAB_SERVER_URL=https://your-ngrok-url-here.ngrok-free.app
        ```

## 🔒 Security Warning (Critical)
1.  **Never Upload Keys**: Keep your API keys in `.env` or `credentials_setup.env`.
2.  **Git Ignore**: The system is pre-configured to ignore `.env`, `credentials_setup.env`, and `google_token.json`. Do not force add them.
3.  **Local Only**: If you create new key files, add them to `.gitignore` immediately.

---

## 🏃 Step 4: Run Cyno
1.  In your terminal (make sure `(venv)` is active):
    ```bash
    python scripts/cli_chat.py
    ```
2.  You should see:
    > `[System] HR Chat Agent initialized...`  
    > `Cyno: Hello! I am Cyno...`

---

## 🎮 Step 5: Master the Commands
Here is everything you can do:

### 🔎 Search for Jobs
-   `find python jobs` (Searches Indeed, LinkedIn, Glassdoor)
-   `find remote marketing internships` (Saves to `internships/`)
-   `find graphic design freelance` (Saves to `freelance/`)

### 📩 Apply & Email
-   `draft email for job #1` (Reads your resume, reads the job, writes a cover letter)
-   `draft email for job #3`

### 🕵️ Genereate Leads (Direct Outreach)
-   `scrape leads for python` (Finds hiring posts on social media with emails)
-   `scrape leads for javascript`

---

## ❓ Troubleshooting
-   **"Module not found" error?** -> Did you run `pip install -r requirements.txt`? Did you activate `venv`?
-   **"Cloud Brain Offline"?** -> Check your Colab tab. Is it still running? Did the ngrok URL change? Update `.env`.
-   **"Permission Denied"?** -> Some sites block scrapers. Cyno handles this, but if you see many fails, try again in 1 hour.

---

**That's it! You are now running a production-grade AI Job Agent on your local machine.** 🚀
