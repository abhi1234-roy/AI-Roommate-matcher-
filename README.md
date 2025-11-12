🏠 Roommate Matcher

A smart web-based application that helps users find compatible roommates by matching their preferences using data-driven algorithms.

🚀 Overview

Roommate Matcher is designed to simplify the process of finding a compatible roommate.
The system collects user preferences such as lifestyle, budget, location, and interests, then applies pairwise matching and A* (A-star) algorithm logic to suggest the most compatible roommate combinations.

It also includes a clean interface, backend database, and visualization of results using interactive components.

🧠 Features

🔍 Smart Matching Algorithm – Matches users based on preference compatibility.

🧩 A* Algorithm Integration – Optimizes the best roommate pair using heuristic evaluation.

🗄️ SQL Database Integration – Stores user profiles and preferences securely.

🌐 Flask Backend – Handles routing, user data, and algorithmic processing.

📊 Interactive Visualization – Displays matching results or path visualization (in A* or Dijkstra demo).

💬 User-Friendly Interface – Simple and intuitive web UI for registration and results.

🏗️ Tech Stack
Component	Technology Used
Frontend	HTML, CSS, JavaScript / Streamlit
Backend	Flask (Python Framework)
Database	MySQL / SQLite
Algorithms	Pairwise Matching, A*, Dijkstra
Visualization	Matplotlib / Streamlit
Tools	Python, VS Code, GitHub
⚙️ How It Works

User Registration: Each user enters their preferences (budget, cleanliness, habits, etc.).

Data Storage: User details are stored in a SQL database.

Matching Process:

Pairwise comparison calculates compatibility scores.

A* algorithm finds the best roommate match based on minimal difference.

Result Display: The system outputs the most compatible roommate pairs and visualizes the result.

📂 Project Structure
Roommate-Matcher/
│
├── app.py                 # Main Flask application
├── static/                # CSS, JS, and image files
├── templates/             # HTML templates
├── database/
│   └── roommate_data.sql  # Database schema and tables
├── algorithms/
│   ├── a_star.py          # A* implementation
│   ├── pairwise_match.py  # Compatibility logic
│   └── dijkstra.py        # (Optional) Dijkstra path demo
├── routes_visualizer.py   # Visualization module
├── requirements.txt       # Dependencies
└── README.md              # Project documentation
