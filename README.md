# AI-Powered Hostel Roommate Matching System

A web-based application that intelligently matches hostel roommates based on lifestyle preferences, habits, and interests using a Stable Roommate Matching Algorithm with KNN-style similarity calculation.

## Features

- **Student Registration Form**: Collect comprehensive lifestyle data including:
  - Sleep schedule (early bird, moderate, night owl)
  - Study time preferences (morning, afternoon, evening, night)
  - Cleanliness level (1-5 scale)
  - Noise tolerance (1-5 scale)
  - Personality type (introvert, ambivert, extrovert)
  - Hobbies and interests

- **AI-Powered Matching Engine**:
  - KNN-style weighted distance calculation
  - Configurable feature weights
  - Hobby overlap bonus using Jaccard similarity
  - Normalized scoring across different attribute scales

- **Stable Roommate Matching Algorithm**:
  - O(n²) complexity
  - Preference list generation based on compatibility scores
  - Stability checking to ensure optimal matches
  - Prevents unstable pairings

- **Comprehensive Results Display**:
  - Matched pairs with compatibility percentages
  - Detailed match reasons (e.g., "both night owls", "high hobby similarity")
  - Match quality statistics (average, min, max scores)
  - Visual indicators for match quality

## Technology Stack

- **Backend**: Python 3.7+, Flask 2.3.3
- **Database**: SQLite (via SQLAlchemy)
- **Frontend**: HTML5, CSS3 (modern responsive design)
- **Libraries**: Flask-SQLAlchemy (no heavy ML packages)

## Project Structure

```
roommate_matcher/
├── app.py                  # Flask application with routes
├── models.py              # Database models (Student, Match)
├── similarity_engine.py   # KNN-style similarity calculation
├── stable_matching.py     # Stable Roommate Matching Algorithm
├── config.py              # Configuration and weights
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── base.html         # Base template with navbar and styling
│   ├── index.html        # Home page
│   ├── register.html     # Student registration form
│   ├── students.html     # List all students
│   ├── match.html        # Run matching algorithm
│   ├── results.html      # Display matched pairs
│   └── profile.html      # Individual student profile
└── README.md             # This file
```

## Installation & Setup

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Clone or Extract the Project

```bash
cd /home/neeraj/Documents/Code/college_minor_projects/roommate_matcher
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Step 5: Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage Guide

### 1. Register Students

1. Click "Register" in the navigation bar
2. Fill out the student registration form with all required fields:
   - Basic info: Name, email, age, gender
   - Lifestyle: Sleep time, study time, cleanliness, noise tolerance
   - Personality: Introvert/Ambivert/Extrovert
   - Hobbies: Comma-separated list
3. Submit the form
4. Repeat for multiple students (minimum 2 required)

### 2. View Registered Students

- Navigate to "Students" to see all registered students
- Click on any student to view their detailed profile

### 3. Run Matching Algorithm

1. Click "Match" in the navigation bar
2. Review the matching process information
3. Click "Start Matching" to run the algorithm
4. The system will:
   - Convert student data to numeric vectors
   - Calculate pairwise compatibility scores
   - Build preference lists
   - Execute stable matching algorithm
   - Generate final matches with reasons

### 4. View Results

- Navigate to "Results" to see matched pairs
- View compatibility scores (0-100%)
- Read detailed match reasons
- See overall statistics
- Check unmatched students (if any)

## Algorithm Details

### Similarity Calculation

The system uses weighted Euclidean distance with the following default weights:

| Feature | Weight | Range |
|---------|--------|-------|
| Sleep Time | 25% | 0-2 |
| Study Time | 20% | 0-3 |
| Cleanliness | 20% | 1-5 |
| Noise Tolerance | 15% | 1-5 |
| Personality | 10% | 0-2 |
| Hobbies | 10% | Jaccard similarity |

**Distance Formula**:
```
distance = Σ(weight_i × normalized_diff_i)
```

**Similarity Score**:
```
score = (1 - distance) × 100
score = score × bonus_multiplier (if hobby_overlap > 0.5)
```

### Stable Matching Process

1. **Preference List Generation**: Each student gets a ranked list of all other students based on compatibility scores

2. **Greedy Matching with Stability**: 
   - Students are processed in order of their top preference score
   - Each unmatched student tries to match with their highest-ranked available preference
   - Matches are accepted if they pass the stability check

3. **Stability Check**:
   - Compatibility score ≥ 50%, OR
   - Both students rank each other in the top 50% of their preference lists

## Configuration

Edit `config.py` to customize:

- **Feature Weights**: Adjust importance of each attribute
- **Hobby Overlap Bonus**: Multiplier for high hobby similarity (default: 1.2)
- **Database**: Change from SQLite to MySQL if needed

Example weight modification:
```python
WEIGHTS = {
    'sleep_time': 0.30,      # Increased importance
    'study_time': 0.25,
    'cleanliness': 0.15,
    'noise_tolerance': 0.15,
    'personality': 0.10,
    'hobbies': 0.05          # Decreased importance
}
```

## Database Schema

### Students Table
- `id`: Primary key
- `name`, `email`, `age`, `gender`: Basic info
- `sleep_time`, `study_time`, `cleanliness`, `noise_tolerance`, `personality`: Numeric preferences
- `hobbies`: Comma-separated string
- `created_at`: Timestamp

### Matches Table
- `id`: Primary key
- `student1_id`, `student2_id`: Foreign keys to students
- `compatibility_score`: Float (0-100)
- `reasons`: Text (comma-separated reasons)
- `matched_at`: Timestamp

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page |
| `/register` | GET/POST | Student registration form |
| `/students` | GET | List all students |
| `/student/<id>` | GET | Individual student profile |
| `/match` | GET/POST | Run matching algorithm |
| `/results` | GET | Display match results |
| `/reset` | POST | Clear all data (testing) |

## Testing

### Quick Test with Sample Data

1. Register at least 2-4 students with varying preferences
2. Example students:
   - **Student A**: Early bird, morning studier, very clean, introvert, hobbies: reading, chess
   - **Student B**: Early bird, morning studier, very clean, introvert, hobbies: reading, music
   - **Student C**: Night owl, night studier, moderate clean, extrovert, hobbies: gaming, sports
   - **Student D**: Night owl, night studier, moderate clean, extrovert, hobbies: gaming, movies

3. Run the matching algorithm
4. Expected: A-B pair (high match), C-D pair (high match)

## Troubleshooting

**Database not found**: The database is created automatically on first run. If issues persist, delete `roommate_matcher.db` and restart.

**Port already in use**: Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Module not found**: Ensure virtual environment is activated and dependencies are installed

## Future Enhancements

- Gender-based filtering options
- Room capacity preferences (single, double, triple)
- Import/Export student data (CSV)
- Email notifications for matches
- Admin dashboard for hostel management
- Historical match tracking and feedback
- Machine learning to improve weights based on successful matches

## License

This project is for educational purposes. Feel free to modify and use as needed.

## Author

Created as part of college minor project - Hostel Roommate Matching System

---

**Note**: This system uses no heavy ML packages - only Flask, SQLAlchemy, and standard Python libraries for math operations. The algorithm is transparent, explainable, and can be easily modified for specific institutional requirements.
