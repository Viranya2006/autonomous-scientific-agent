# 🔑 API Setup Guide - Autonomous Scientific Agent

This guide walks you through obtaining API keys for all three required services. **Total time: ~15 minutes**.

---

## 📋 Quick Overview

| API                   | Time  | Difficulty  | Cost | Quota                    |
| --------------------- | ----- | ----------- | ---- | ------------------------ |
| **Google Gemini**     | 5 min | ⭐ Easy     | FREE | 1,500 req/day            |
| **Hugging Face**      | 3 min | ⭐ Easy     | FREE | Unlimited (rate limited) |
| **Materials Project** | 5 min | ⭐⭐ Medium | FREE | 50,000 req/month         |

---

## 1️⃣ Google Gemini API (Priority 1)

**Why needed:** Primary LLM for understanding papers, generating hypotheses, and scientific reasoning.

### Step-by-Step Instructions

#### **Step 1: Visit Google AI Studio**

- Open your browser and go to: **https://makersuite.google.com/app/apikey**
- Or search "Google AI Studio API key"

#### **Step 2: Sign In**

- Click **"Sign in"** in the top right
- Use your personal Google account (Gmail works great)
- No credit card required!

#### **Step 3: Get Your API Key**

- You'll see a page titled **"Get API key"**
- Click the blue **"Create API key"** button
- Choose **"Create API key in new project"** (recommended for new users)
- Your key will appear: something like `AIzaSyA...` (37 characters)

#### **Step 4: Copy Your Key**

- Click the **Copy** icon next to your key
- Paste it somewhere safe temporarily (Notepad, TextEdit, etc.)
- You'll add it to `.env` later

### ✅ How to Verify It Works

```python
# Quick test (after setup)
from src.api.gemini_client import GeminiClient
client = GeminiClient(api_key="YOUR_KEY_HERE")
response = client.generate_text("Say hello!")
print(response)
```

### Rate Limits & Quotas

- **Free tier:** 1,500 requests per day
- **Tokens:** 32k input + 8k output per request
- **Rate:** ~15 requests per minute
- **Reset:** Daily at midnight PST

### Common Issues

| Problem               | Solution                                                 |
| --------------------- | -------------------------------------------------------- |
| "API key not valid"   | Make sure you copied the entire key (starts with `AIza`) |
| "Quota exceeded"      | Wait until next day, or use different Google account     |
| "Model not available" | Check that you're using `gemini-2.0-flash-exp`           |

---

## 2️⃣ Hugging Face API (Priority 2)

**Why needed:** Alternative models for specialized tasks, embeddings, and redundancy.

### Step-by-Step Instructions

#### **Step 1: Create Account**

- Go to: **https://huggingface.co/join**
- Enter your email, username, and password
- Check your email for verification link and click it
- **OR** sign up with Google/GitHub (faster!)

#### **Step 2: Access Token Settings**

- Once logged in, click your profile picture (top right)
- Click **"Settings"** from dropdown menu
- In left sidebar, click **"Access Tokens"**
- Or go directly to: **https://huggingface.co/settings/tokens**

#### **Step 3: Create New Token**

- Click **"New token"** button
- Give it a name: `autonomous-scientist` or similar
- Choose role: **"Read"** (sufficient for API access)
- Click **"Generate token"**

#### **Step 4: Copy Your Token**

- Your token appears: `hf_...` (starts with `hf_`)
- Click **"Copy"** button
- Store it safely (you can only see it once!)
- If lost, create a new token

### ✅ How to Verify It Works

```python
# Quick test (after setup)
from src.api.huggingface_client import HuggingFaceClient
client = HuggingFaceClient(token="YOUR_TOKEN_HERE")
response = client.generate_text("Hello!", model="gpt2", max_length=20)
print(response)
```

### Rate Limits & Quotas

- **Free tier:** Unlimited requests (yes, really!)
- **Rate limit:** ~100 requests/hour per model
- **Caveat:** Models may take 20-30s to load if cold
- **Models:** Access to 400k+ models

### Common Issues

| Problem               | Solution                                      |
| --------------------- | --------------------------------------------- |
| "Invalid token"       | Regenerate token, ensure it starts with `hf_` |
| "Model loading" (503) | Wait 20-30s, client auto-retries              |
| "Rate limit"          | Use different model or wait ~hour             |

---

## 3️⃣ Materials Project API (Priority 3)

**Why needed:** Access to materials science database for validation and property lookup.

### Step-by-Step Instructions

#### **Step 1: Create Account**

- Go to: **https://next-gen.materialsproject.org/**
- Click **"Sign Up"** in top right
- Fill in:
  - Email address
  - Username
  - Password
  - Organization (can put "Personal" or university)
  - Country
- Check "I agree to Terms of Service"
- Click **"Create Account"**

#### **Step 2: Verify Email**

- Check your email inbox
- Click verification link in email from Materials Project
- You'll be redirected to the website

#### **Step 3: Get API Key**

- Log in to: **https://next-gen.materialsproject.org/**
- Click your username (top right)
- Select **"API"** from dropdown
- Or go directly to: **https://next-gen.materialsproject.org/api**

#### **Step 4: Generate Key**

- You'll see a section **"API Key"**
- Click **"Generate API Key"** button
- Your key appears (long alphanumeric string)
- Click **"Copy"** button
- Store it safely

### ✅ How to Verify It Works

```python
# Quick test (after setup)
from src.api.materials_project_client import MaterialsProjectClient
client = MaterialsProjectClient(api_key="YOUR_KEY_HERE")
results = client.search_by_formula("Si")
print(f"Found {len(results)} materials")
```

### Rate Limits & Quotas

- **Free tier:** 50,000 requests per month
- **Rate:** ~10 requests per second
- **Data:** Full database access
- **Reset:** Monthly on day you signed up

### Common Issues

| Problem              | Solution                                     |
| -------------------- | -------------------------------------------- |
| "Invalid API key"    | Regenerate from dashboard                    |
| "Quota exceeded"     | Wait until next month, or create new account |
| "Material not found" | Check formula spelling (case sensitive)      |

---

## 4️⃣ arXiv API (No Key Needed! 🎉)

**Why needed:** Downloading scientific papers for analysis.

### Good News!

- **No API key required**
- **No registration needed**
- **Free forever**
- Just use the `arxiv` Python package

### Rate Limits

- **Rate:** Max 1 request per 3 seconds
- **Bulk:** Max 1,000 papers per request
- Be respectful of their servers!

---

## 5️⃣ PubChem API (No Key Needed! 🎉)

**Why needed:** Chemical compound information and validation.

### Good News!

- **No API key required**
- **No registration needed**
- **Free forever**
- Simple REST API

### Rate Limits

- **Rate:** Max 5 requests per second
- **Bulk:** Up to 10,000 compounds per request
- Very generous limits!

---

## 🔐 Adding Keys to Your Project

Once you have all three keys:

### Step 1: Find Your .env File

```powershell
# In your project folder
notepad .env  # Windows
# or
code .env     # If using VS Code
```

### Step 2: Replace Placeholders

```bash
# Before:
GEMINI_API_KEY=your_gemini_key_here

# After:
GEMINI_API_KEY=AIzaSyA1234567890abcdefGHIJKLMNOPQRSTUV
```

Do this for all three keys:

- `GEMINI_API_KEY`
- `HF_TOKEN`
- `MP_API_KEY`

### Step 3: Save the File

Make sure to **save** (Ctrl+S / Cmd+S)!

### Step 4: Test Everything

```powershell
# In your activated virtual environment
python scripts/test_all_apis.py
```

You should see:

```
✅ PASS | Gemini API                   |   2.34s | Text generation working
✅ PASS | Hugging Face API             |   5.67s | Inference working
✅ PASS | Materials Project API        |   1.23s | Found 12 materials...

🎉 All tests passed! Your APIs are ready to use.
```

---

## 🚨 Troubleshooting

### "Configuration validation failed"

**Problem:** `.env` file not found or API keys not set.

**Solution:**

```powershell
# 1. Check if .env exists
Get-Item .env

# 2. If not, copy from template
Copy-Item .env.example .env

# 3. Edit and add your keys
notepad .env
```

### "GEMINI_API_KEY not set in .env file"

**Problem:** Key is still the placeholder value.

**Solution:** Replace `your_gemini_key_here` with your actual key from Google AI Studio.

### "Failed to load configuration"

**Problem:** `.env` file has syntax errors.

**Solution:**

- Make sure each line follows: `KEY=value`
- No spaces around `=`
- No quotes around values
- Save as plain text (not .env.txt)

### API Test Fails But Key is Correct

**Problem:** Network issue or temporary API outage.

**Solution:**

```powershell
# 1. Check internet connection
Test-Connection google.com

# 2. Try again (APIs sometimes have brief hiccups)
python scripts/test_all_apis.py

# 3. Check API status pages:
# - Gemini: https://status.cloud.google.com/
# - HuggingFace: https://status.huggingface.co/
# - Materials Project: Check their main site
```

---

## 💡 Pro Tips

### Keep Keys Secret! 🔒

**Never:**

- ❌ Commit `.env` to git
- ❌ Share keys in Discord/Slack
- ❌ Post keys in screenshots
- ❌ Include in blog posts

**Good to know:**

- ✅ `.env` is in `.gitignore` (safe!)
- ✅ Keys can be regenerated if leaked
- ✅ Use separate keys for different projects

### Manage Your Quotas 📊

**Google Gemini:**

- Track usage at: https://makersuite.google.com/app/apikey
- Consider multiple accounts if needed (totally fine!)

**Hugging Face:**

- Be patient with model loading (first request can be slow)
- Stick to popular models (they stay "warm")

**Materials Project:**

- Enable caching (already done in code!)
- Cache saves ~90% of API calls

### Test Individual APIs

If one API fails, test it separately:

```python
# Test just Gemini
from src.config.settings import Settings
from src.api.gemini_client import GeminiClient

settings = Settings()
client = GeminiClient(settings.gemini_api_key)
print(client.test_connection())
```

---

## ✅ Success Checklist

Before moving to Phase 2, make sure:

- [ ] Google Gemini key obtained and added to `.env`
- [ ] Hugging Face token obtained and added to `.env`
- [ ] Materials Project key obtained and added to `.env`
- [ ] `test_all_apis.py` runs successfully
- [ ] All three APIs return ✅ PASS
- [ ] No error messages in output

---

## 🎉 You're Ready!

All API keys configured? Awesome! You're now ready for **Phase 2: Paper Collection & Analysis**.

### What's Next?

```powershell
# Explore the testing notebook
jupyter notebook notebooks/01_phase1_testing.ipynb

# Or wait for Phase 2 prompt!
```

---

## 📚 Additional Resources

- **Google Gemini Docs:** https://ai.google.dev/docs
- **Hugging Face Docs:** https://huggingface.co/docs/api-inference
- **Materials Project Docs:** https://docs.materialsproject.org/
- **Project Issues:** Check GitHub issues or README.md

---

**Questions?** Open an issue or check the troubleshooting section above!
