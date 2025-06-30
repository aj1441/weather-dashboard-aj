# 🔖 Section 0: Fellow Details

Fill out the table below:

| Field                  | Your Entry                                                                                       |
|------------------------|--------------------------------------------------------------------------------------------------|
| Name                   |   Aj Smith                                                                                       |
| GitHub Username        |   aj1441                                                                                         |
| Preferred Feature Track|  All- Data / Visual / Interactive / Smart                                                        |
| Team Interest          |  Yes: Project Owner or Contributors Thomas Hunt, Tiffanimay Noel, Anyone Else                    |
| Team Interest Cont ..  |  I'd be open to having anyone on my team. I am up to any challenge at this point                 |
| Team Interest Cont ..  |  I believe I will be an valuble asset to any team. I do want to be challenged                    |
| Team Interest Cont ..  |  not just with my leadership and people skill, but more importantly my skills as a developer     |

---

# ✍️ Section 1: Week 11 Reflection

Answer each prompt with 3–5 bullet points:

### Key Takeaways  
* What did you learn about capstone goals and expectations?
    * I learned that a large part of the project will be done independently. 
    * I am expected to complete at a minimun of 3 features of my choosing.
    * I learned the first feature is due week 13.

### Concept Connections  
* Which Week 1–10 skills feel strongest?  
    * SQL
    * Basic python syntax
    * Using jupyter to analyze data and clean data
* Which need more practice?
    * Machine Learning 
    * Algorithms
    * GUI Development

### Early Challenges  
* Any blockers (e.g., API keys, folder setup)?
    * Figuring out what will work best on my Macbook for GUI appearence: tkinter, ttk, bootstrapTkinter, customerTkinter. I've learned that I believe I can inter mix the three. I've played around with all 4 seperately. But next week I want to work on integrating them.
    * Slowing down to make my code more modularized and using classes and ensuring low coupling and high cohesion.
    * Trying to get a good grasp on what features that I really want to include. What will be the best way for me to be able to include icons or images in my gui.

### Support Strategies  
* Which office hours or resources can help you move forward?
    * I can review some of the before class resources
    * I can review my inclass notes
    * I can use GPT to help answer some of the questions I have and compare available options, to see what will work, might work and can work based on what I have and where I want to go. The challenging part is narrowing down what I really want to do. Weather as a whole, based on the amount of data that I can use and store is not that intersting. I have a few ok, ideas. But, I really want some thing that will challenge me and holds so true value. I don't know what that is yet.

---

# 🧠 Section 2: Feature Selection Rationale

List three features + one enhancement you plan to build:

| #   | Feature Name                     | Difficulty (1–3) | Why You Chose It / Learning Goal |
|-----|----------------------------------|------------------|----------------------------------|
| 1   | City Comparison w/hist & forcast |       1-2        | I want the user to be able to compare current temperatures and future forcast for different cities for move or travel planning.                              |
| 2   | Theme Switcher                   |     2            | I like the user to have the ability to change from light to dark based on prefences. But also love the idea of night/day mode default to be set based on the sunrise/set and the location of the ip address                                 |
| 3   | Tomorrow's Guess                |      3            |    I'd love to predict more than 1 day     |
| Enhancement | Animation based on current weather.                         | –                |    Sounds fun!               |

🧩 *Tip: Pick at least one “level 3” feature to stretch your skills!*

---

# 🗂️ Section 3: High-Level Architecture Sketch

## Core Modules and Folders
```
weather-dashboard-aj/
├── core/                    # Core business logic (low coupling)
│   ├── api.py              # Weather API client (OpenWeatherMap)
│   ├── data_handler.py     # Data persistence & saved cities
│   ├── icon_manager.py     # Centralized icon/image management
│   └── utils.py            # Theme management & user settings
├── gui/                     # User interface layer
│   ├── components/         # Reusable UI components (high cohesion)
│   │   ├── theme_component.py
│   │   ├── weather_input_component.py
│   │   ├── weather_display_component.py
│   │   └── saved_cities_component.py
│   └── tabbed_main_window.py
├── features/               # Feature-specific modules
│   ├── city_comparison.py  # Feature 1: Multi-city comparison
│   ├── theme_switcher.py   # Feature 2: Advanced theming
│   └── weather_prediction.py # Feature 3: Tomorrow's guess
├── data/                   # Data storage
│   ├── user_settings.json  # Theme preferences
│   └── saved_locations.json # Saved cities
└── assets/                 # Static resources
    ├── icons/              # Weather condition icons
    └── images/             # UI images
```

## Feature Modules
* **City Comparison** - Compare weather across multiple cities with historical data
* **Theme Switcher** - Dynamic light/dark themes based on time/location
* **Weather Prediction** - ML-based next-day weather prediction
* **Animation Enhancement** - Weather-based UI animations

## Data Flow Between Components
```
[User Input] → [WeatherInputComponent] → [WeatherAPI] → [Data Handler]
     ↓                                                        ↓
[Weather Display] ← [Icon Manager] ← [Processing] ← [Raw Weather Data]
     ↓
[Save City Button] → [SavedCitiesComponent] → [JSON Storage]
     ↓
[Theme Component] → [User Settings] → [Persistent Storage]
```

**Flow Description:**
1. User enters city/state in input component
2. API fetches weather data from OpenWeatherMap
3. Data handler processes and optionally saves data
4. Icon manager provides appropriate weather icons
5. Display component shows formatted weather info
6. User can save cities for quick access
7. Theme preferences persist across sessions

---

# 📊 Section 4: Data Model Plan

Fill in your planned data files or tables:

| File/Table Name      | Format (txt, json, csv, other) | Example Row                         |
|----------------------|-------------------------------|-------------------------------------|
| weather_history.txt  | txt                           | 2025-06-09,New Brunswick,78,Sunny   |

---

# 📆 Section 5: Personal Project Timeline (Weeks 12–17)

Customize based on your availability:

| Week | Monday         | Tuesday        | Wednesday      | Thursday        | Key Milestone             |
|------|----------------|----------------|----------------|------------------|----------------------------|
| 12   | API setup      | Error handling | Tkinter shell  | Buffer day       | Basic working app         |
| 13   | Feature 1      |                |                | Integrate        | Feature 1 complete        |
| 14   | Feature 2 start|                | Review & test  | Finish           | Feature 2 complete        |
| 15   | Feature 3      | Polish UI      | Error passing  | Refactor         | All features complete     |
| 16   | Enhancement    | Docs           | Tests          | Packaging        | Ready-to-ship app         |
| 17   | Rehearse       | Buffer         | Showcase       | –                | Demo Day                  |

---

# ⚠️ Section 6: Risk Assessment

Identify at least 3 potential risks and how you’ll handle them:

| Risk             | Likelihood (High/Med/Low)  | Impact (High/Med/Low)    | Mitigation Plan                    |
|------------------|----------------------------|-------------------------|-------------------------------------|
| API Rate Limit   | Medium                     | Medium                  | Add delays or cache recent results  |
| Team Cohesion.   | Medium                     | High                    | Draft 1st meet outline 10 min slots |
| working animation | Medium                    | Low                     | Use still Image instead             |

---

# 🤝 Section 7: Support Requests

What specific help will you ask for in office hours or on Slack?
- I will ask for clarifying questions on timelines, instructions, and listen to other's questions.

---

# ✅ Section 8: Before Monday (Start of Week 12)

Complete these setup steps before Monday:

- [ ] Push `main.py`, `config.py`, and a `/data/` folder to your repo  
- [ ] Add OpenWeatherMap key to `.env` (**⚠️ Do not commit the key**)  
- [ ] Create files for the chosen feature in `/features/`

Example feature file:

```python
# weather_journal.py
"""
Feature: Weather Journal
- Stores daily mood and notes alongside weather data
"""
def add_journal_entry(date, mood, notes):
    # your code goes here
    pass
