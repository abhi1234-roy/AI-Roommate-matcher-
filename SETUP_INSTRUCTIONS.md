# Quick Setup Instructions

## For First-Time Setup

### 1. Create Virtual Environment

```bash
cd /home/neeraj/Documents/Code/college_minor_projects/roommate_matcher
python3 -m venv venv
```

### 2. Activate Virtual Environment

```bash
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

### 5. Open in Browser

Navigate to: `http://localhost:5000`

---

## Step-by-Step Usage

### Register Students (Minimum 2)

1. Go to: `http://localhost:5000/register`
2. Fill the form completely
3. Click "Register Student"
4. Repeat for more students

### Run Matching

1. Go to: `http://localhost:5000/match`
2. Click "Start Matching"
3. Wait for processing

### View Results

1. Go to: `http://localhost:5000/results`
2. See matched pairs with compatibility scores
3. Read match reasons

---

## Sample Test Data

You can register these test students to see the system in action:

**Student 1: Alice Johnson**
- Email: alice@example.com
- Age: 20, Gender: Female
- Sleep: Early Bird, Study: Morning
- Cleanliness: 5, Noise: 2, Personality: Introvert
- Hobbies: reading, meditation, yoga

**Student 2: Bob Smith**
- Email: bob@example.com
- Age: 21, Gender: Male
- Sleep: Early Bird, Study: Morning
- Cleanliness: 4, Noise: 2, Personality: Introvert
- Hobbies: reading, chess, coding

**Student 3: Charlie Davis**
- Email: charlie@example.com
- Age: 19, Gender: Male
- Sleep: Night Owl, Study: Night
- Cleanliness: 2, Noise: 5, Personality: Extrovert
- Hobbies: gaming, music, partying

**Student 4: Diana Wilson**
- Email: diana@example.com
- Age: 20, Gender: Female
- Sleep: Night Owl, Study: Night
- Cleanliness: 3, Noise: 4, Personality: Extrovert
- Hobbies: gaming, movies, socializing

Expected matches:
- Alice ↔ Bob (High compatibility ~85-90%)
- Charlie ↔ Diana (High compatibility ~80-85%)

---

## Troubleshooting

**Error: Port 5000 already in use**
```bash
# Kill existing process
lsof -ti:5000 | xargs kill -9
# Or change port in app.py to 5001
```

**Error: Module not found**
```bash
pip install --upgrade -r requirements.txt
```

**Database issues**
```bash
# Delete and recreate database
rm roommate_matcher.db
python app.py
```

---

## Reset All Data

Visit the home page and look for the "Reset" option, or delete the database file:
```bash
rm roommate_matcher.db
```

---

## Configuration

Edit `config.py` to adjust:
- Feature weights (importance of each attribute)
- Hobby overlap bonus multiplier
- Database settings

Default weights:
- Sleep Time: 25%
- Study Time: 20%
- Cleanliness: 20%
- Noise Tolerance: 15%
- Personality: 10%
- Hobbies: 10%
