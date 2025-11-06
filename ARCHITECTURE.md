# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        WEB BROWSER                          │
│                    (User Interface)                         │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP Requests/Responses
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    FLASK APPLICATION                        │
│                         (app.py)                            │
├─────────────────────────────────────────────────────────────┤
│  Routes:                                                    │
│  • /               → Home Dashboard                         │
│  • /register       → Student Registration                   │
│  • /students       → List Students                          │
│  • /match          → Run Matching Algorithm                 │
│  • /results        → Display Results                        │
│  • /student/<id>   → Student Profile                        │
└────────┬──────────────────────┬──────────────┬──────────────┘
         │                      │              │
         │                      │              │
    ┌────▼─────┐        ┌──────▼──────┐  ┌───▼──────────┐
    │ Database │        │ Similarity  │  │   Stable     │
    │  Models  │        │   Engine    │  │  Matching    │
    │          │        │             │  │  Algorithm   │
    │models.py │        │similarity_  │  │stable_       │
    │          │        │engine.py    │  │matching.py   │
    └────┬─────┘        └──────┬──────┘  └───┬──────────┘
         │                     │             │
         │                     │             │
    ┌────▼─────────────────────▼─────────────▼──────────┐
    │              SQLITE DATABASE                      │
    │          (roommate_matcher.db)                    │
    │                                                   │
    │  Tables: students, matches                        │
    └───────────────────────────────────────────────────┘
```

## Component Details

### 1. Flask Application (app.py)

**Responsibilities:**
- Handle HTTP requests
- Render HTML templates
- Coordinate between components
- Session management
- Error handling

**Key Routes:**
```python
GET  /              # Dashboard
GET  /register      # Registration form
POST /register      # Submit registration
GET  /students      # List all students
GET  /student/<id>  # View profile
GET  /match         # Match page
POST /match         # Execute matching
GET  /results       # View matches
POST /reset         # Clear database
```

### 2. Database Models (models.py)

**Student Model:**
```
┌──────────────────────────────┐
│         Student              │
├──────────────────────────────┤
│ id (PK)                      │
│ name                         │
│ email (unique)               │
│ age                          │
│ gender                       │
│ sleep_time (0-2)             │
│ study_time (0-3)             │
│ cleanliness (1-5)            │
│ noise_tolerance (1-5)        │
│ personality (0-2)            │
│ hobbies (text)               │
│ created_at                   │
└──────────────────────────────┘
```

**Match Model:**
```
┌──────────────────────────────┐
│          Match               │
├──────────────────────────────┤
│ id (PK)                      │
│ student1_id (FK)             │
│ student2_id (FK)             │
│ compatibility_score          │
│ reasons (text)               │
│ matched_at                   │
└──────────────────────────────┘
```

### 3. Similarity Engine (similarity_engine.py)

**Algorithm Flow:**

```
Input: Two student vectors
         │
         ▼
┌─────────────────────────────────────┐
│  Calculate Weighted Distance        │
│  ─────────────────────────────      │
│  • Sleep time difference            │
│  • Study time difference            │
│  • Cleanliness difference           │
│  • Noise tolerance difference       │
│  • Personality difference           │
│  • Hobby overlap (Jaccard)          │
└─────────────────┬───────────────────┘
                  │
                  ▼
         Normalize to 0-1 scale
                  │
                  ▼
┌─────────────────────────────────────┐
│  Apply Weights & Calculate Score    │
│  ─────────────────────────────      │
│  Score = (1 - distance) × 100       │
│  If hobby_overlap > 0.5:            │
│    Score × 1.2 (bonus)              │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Generate Match Reasons             │
│  ─────────────────────────────      │
│  • Same sleep schedule?             │
│  • Same study time?                 │
│  • Similar cleanliness?             │
│  • Common hobbies?                  │
└─────────────────┬───────────────────┘
                  │
                  ▼
Output: (score, reasons)
```

### 4. Stable Matching Algorithm (stable_matching.py)

**Algorithm Flow:**

```
Input: All students + Similarity scores
         │
         ▼
┌─────────────────────────────────────┐
│  Build Preference Lists             │
│  ─────────────────────────────      │
│  For each student:                  │
│    Rank all others by score         │
│    Store sorted list                │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Sort Students by Top Preference    │
│  ─────────────────────────────      │
│  Priority = highest score they can  │
│  achieve                            │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Greedy Matching Loop               │
│  ─────────────────────────────      │
│  For each unmatched student:        │
│    Find top unmatched preference    │
│    Check stability                  │
│    If stable: create match          │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Stability Check                    │
│  ─────────────────────────────      │
│  Accept if:                         │
│  • Score >= 50%, OR                 │
│  • Both rank each other in top 50%  │
└─────────────────┬───────────────────┘
                  │
                  ▼
Output: List of (student1, student2, score, reasons)
```

## Data Flow

### Registration Flow:

```
User → Form → Flask → Validate → Database
                                    │
                                    ▼
                              Students Table
```

### Matching Flow:

```
User → Match Request → Flask
                         │
                         ▼
                  Get all students
                         │
                         ▼
                  Convert to vectors
                         │
                         ▼
              Calculate all similarities ─────┐
                         │                    │
                         │              Similarity
                         │                Engine
                         │                    │
                         ▼                    │
              Run stable matching ◄───────────┘
                         │
                         │
                         │              Stable
                         │              Matching
                         │                    │
                         ▼                    │
              Save to database ◄──────────────┘
                         │
                         ▼
              Display results
```

## Similarity Calculation Formula

```
For each attribute pair (student1, student2):

1. Sleep Time Distance:
   d_sleep = |sleep1 - sleep2| / 2
   
2. Study Time Distance:
   d_study = |study1 - study2| / 3
   
3. Cleanliness Distance:
   d_clean = |clean1 - clean2| / 4
   
4. Noise Tolerance Distance:
   d_noise = |noise1 - noise2| / 4
   
5. Personality Distance:
   d_personality = |personality1 - personality2| / 2
   
6. Hobby Similarity (Jaccard):
   hobbies_overlap = |hobbies1 ∩ hobbies2| / |hobbies1 ∪ hobbies2|
   d_hobbies = 1 - hobbies_overlap

Total Distance:
   D = w_sleep × d_sleep + 
       w_study × d_study + 
       w_clean × d_clean + 
       w_noise × d_noise + 
       w_personality × d_personality + 
       w_hobbies × d_hobbies

Similarity Score:
   S = (1 - D) × 100
   
   If hobbies_overlap > 0.5:
       S = S × 1.2  (capped at 100)
```

## Template Hierarchy

```
base.html (Navigation, CSS, Flash messages)
   │
   ├── index.html (Dashboard)
   │
   ├── register.html (Registration form)
   │
   ├── students.html (Student list)
   │
   ├── match.html (Run matching)
   │
   ├── results.html (Match results)
   │
   └── profile.html (Student details)
```

## Technology Stack

```
┌─────────────────────────────────────┐
│          PRESENTATION LAYER         │
│     HTML5 + CSS3 (Responsive)       │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│        APPLICATION LAYER            │
│        Flask 2.3.3 (Python)         │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│           DATA LAYER                │
│  SQLAlchemy ORM + SQLite Database   │
└─────────────────────────────────────┘
```

## Security Considerations

- ✓ SQL Injection: Protected by SQLAlchemy ORM
- ✓ XSS: Jinja2 auto-escaping enabled
- ✓ CSRF: Flask secret key for session security
- ✓ Email Validation: Unique constraint
- ✓ Input Validation: Server-side validation

## Performance

- **Matching Complexity**: O(n²)
- **Database Queries**: Optimized with eager loading
- **Suitable For**: Up to 500-1000 students
- **Response Time**: < 1 second for typical loads

## Scalability

For larger deployments:
1. Switch to PostgreSQL/MySQL
2. Add Redis caching
3. Implement async matching with Celery
4. Add pagination for student lists
5. Optimize with database indexing
