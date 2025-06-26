
# Code Step Guide

## Overview

This document is your step-by-step guide to completing the Capstone Project: a fully functional weather dashboard built in Python. You will work individually on your app, and later contribute to a team-based collaborative feature. Follow the weekly instructions to stay on track and submit a project you can be proud of.

---

## Starter Kit Setup: Your Capstone Foundation

### 🛠 Initial Setup Checklist

Before you write any code, set up your project like this:

1. **Create a GitHub repository**  
    - Use GitHub UI or `git init` and `git remote add origin`  
    - Name it something like `weather-dashboard-[yourname]`  

2. **Create your project folder with this structure:**

```
weather-dashboard-[yourname]/
├── main.py            # Main app logic
├── config.py          # Your API keys
├── features/          # Feature modules
│   └── (empty for now)
├── data/              # For saved CSV or text files
├── docs/              # README and user_guide.md
├── requirements.txt   # Will be added in Week 16
└── screenshots/       # Add images for your README
```

3. **Make your first commit**

```bash
git add .
git commit -m "Initial folder structure"
git push origin main
```

✅ You’ve now scaffolded your app from scratch — each week will build on this.

---

## Visual Timeline: How Your App Grows Week by Week

| Week | Focus                  | App Functionality                          |
|------|------------------------|--------------------------------------------|
| W11  | Planning & Setup       | Feature selection, timeline, GitHub repo created |
| W12  | Core Build             | Weather API fetcher, GUI window, basic display |
| W13  | Feature #1             | Add 1 self-contained feature (e.g., graph or journal) |
| W14  | Feature #2             | Add 2nd feature + export data for team     |
| W15  | Feature #3             | Complete 3rd feature + begin team plugin   |
| W16  | Enhancement & Docs     | Personalize app + create README + polish GUI |
| W17  | Presentation           | Demo solo app + team feature               |

🧱 You’re laying one brick per week — not building Rome overnight.

---

## Mini Walkthrough: Blank Repo to Weather App in 10 Minutes

Here’s a tiny example to help you get your app off the ground.

### 1. Create `main.py` with a basic GUI window:

```python
import tkinter as tk

root = tk.Tk()
root.title("Weather App")
root.geometry("400x300")

label = tk.Label(root, text="Welcome to my Weather App")
label.pack(pady=20)

root.mainloop()
```

Run it → a blank app window appears ✅

### 2. Add a button to simulate a weather fetch:

```python
def fake_fetch_weather():
    label.config(text="Portland: 72°F, Sunny")

button = tk.Button(root, text="Get Weather", command=fake_fetch_weather)
button.pack()
```

### 3. Commit your progress:

```bash
git add main.py
git commit -m "Added basic GUI with fake weather fetch"
git push
```

✅ You’ve now got:
- A working interface  
- A clickable button  
- A functional commit history  

Now imagine swapping `fake_fetch_weather()` with your real API call in **Week 12**.
