"""
Flask Application - Roommate Matching System
Main application entry point with routes
"""
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Student, Match
from similarity_engine import SimilarityEngine, AStarMatcher
from config import Config
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    """Home page with navigation"""
    student_count = Student.query.count()
    match_count = Match.query.count()
    return render_template('index.html', 
                         student_count=student_count,
                         match_count=match_count)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Student registration form"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            email = request.form.get('email')
            age = int(request.form.get('age'))
            gender = request.form.get('gender')
            sleep_time = int(request.form.get('sleep_time'))
            study_time = int(request.form.get('study_time'))
            cleanliness = int(request.form.get('cleanliness'))
            noise_tolerance = int(request.form.get('noise_tolerance'))
            personality = int(request.form.get('personality'))
            hobbies = request.form.get('hobbies')
            
            # Check if email already exists
            existing_student = Student.query.filter_by(email=email).first()
            if existing_student:
                flash('Email already registered!', 'error')
                return redirect(url_for('register'))
            
            # Create new student
            student = Student(
                name=name,
                email=email,
                age=age,
                gender=gender,
                sleep_time=sleep_time,
                study_time=study_time,
                cleanliness=cleanliness,
                noise_tolerance=noise_tolerance,
                personality=personality,
                hobbies=hobbies
            )
            
            db.session.add(student)
            db.session.commit()
            
            flash(f'Successfully registered {name}!', 'success')
            return redirect(url_for('students'))
            
        except Exception as e:
            flash(f'Error during registration: {str(e)}', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')


@app.route('/students')
def students():
    """Display all registered students"""
    all_students = Student.query.order_by(Student.created_at.desc()).all()
    return render_template('students.html', students=all_students)


@app.route('/match', methods=['GET', 'POST'])
def match():
    """Run the matching algorithm on selected students"""
    if request.method == 'POST':
        try:
            # Get selected student IDs from form
            selected_ids = request.form.getlist('selected_students')
            matching_mode = request.form.get('matching_mode', 'pairwise')
            
            # Clear ALL previous matches
            Match.query.delete()
            db.session.commit()
            
            if matching_mode == 'astar':
                # A* Search for optimal batch matching
                if len(selected_ids) < 2:
                    flash('Please select at least 2 students for A* matching!', 'error')
                    return redirect(url_for('match'))
                
                # Get all selected students
                students = [Student.query.get(int(sid)) for sid in selected_ids]
                students = [s for s in students if s is not None]
                
                if len(students) < 2:
                    flash('Invalid student selection!', 'error')
                    return redirect(url_for('match'))
                
                # Convert to vectors
                student_vectors = [s.to_vector() for s in students]
                
                # Run A* Search algorithm
                astar_matcher = AStarMatcher()
                result = astar_matcher.match_students(student_vectors)
                
                # Save matches to database
                for match_tuple in result['matches']:
                    student1_id, student2_id, score, reasons = match_tuple
                    match = Match(
                        student1_id=student1_id,
                        student2_id=student2_id,
                        compatibility_score=score,
                        reasons=', '.join(reasons)
                    )
                    db.session.add(match)
                
                db.session.commit()
                
                flash(f'A* Search completed! {len(result["matches"])} optimal pairs found. '
                      f'Nodes explored: {result["nodes_explored"]}. '
                      f'Average compatibility: {result["average_score"]:.2f}%', 'success')
                
                if result['unmatched']:
                    flash(f'Unmatched students (odd number): {len(result["unmatched"])}', 'info')
                
                return redirect(url_for('results'))
            
            else:
                # Original pairwise matching (for comparison)
                if len(selected_ids) != 2:
                    flash('Please select exactly 2 students for pairwise matching!', 'error')
                    return redirect(url_for('match'))
                
                # Convert to integers
                student1_id = int(selected_ids[0])
                student2_id = int(selected_ids[1])
                
                # Get the two selected students
                student1 = Student.query.get(student1_id)
                student2 = Student.query.get(student2_id)
                
                if not student1 or not student2:
                    flash('Selected students not found!', 'error')
                    return redirect(url_for('match'))
                
                # Convert students to vectors
                vec1 = student1.to_vector()
                vec2 = student2.to_vector()
                
                # Calculate similarity score
                similarity_engine = SimilarityEngine()
                score, reasons = similarity_engine.calculate_similarity_score(vec1, vec2)
                
                # Save match to database
                match = Match(
                    student1_id=student1_id,
                    student2_id=student2_id,
                    compatibility_score=score,
                    reasons=', '.join(reasons)
                )
                db.session.add(match)
                db.session.commit()
                
                flash(f'Pairwise compatibility calculated: {score:.2f}%', 'success')
                return redirect(url_for('results'))
            
        except Exception as e:
            flash(f'Error during matching: {str(e)}', 'error')
            return redirect(url_for('match'))
    
    # GET request - show student selection page
    all_students = Student.query.order_by(Student.name).all()
    student_count = len(all_students)
    return render_template('match.html', student_count=student_count, students=all_students)


@app.route('/results')
def results():
    """Display matching results"""
    matches = Match.query.order_by(Match.compatibility_score.desc()).all()
    
    if not matches:
        flash('No matches found. Please run the matching algorithm first.', 'info')
        return redirect(url_for('match'))
    
    # Calculate statistics
    scores = [match.compatibility_score for match in matches]
    stats = {
        'total_pairs': len(matches),
        'average_score': round(sum(scores) / len(scores), 2) if scores else 0,
        'min_score': round(min(scores), 2) if scores else 0,
        'max_score': round(max(scores), 2) if scores else 0
    }
    
    return render_template('results.html', 
                         matches=matches, 
                         stats=stats)


@app.route('/student/<int:student_id>')
def student_profile(student_id):
    """Display individual student profile"""
    student = Student.query.get_or_404(student_id)
    
    # Get student's match if exists
    match = Match.query.filter(
        (Match.student1_id == student_id) | (Match.student2_id == student_id)
    ).first()
    
    return render_template('profile.html', student=student, match=match)


@app.route('/reset', methods=['POST'])
def reset():
    """Reset all data (for testing purposes)"""
    try:
        Match.query.delete()
        Student.query.delete()
        db.session.commit()
        flash('All data has been reset!', 'success')
    except Exception as e:
        flash(f'Error during reset: {str(e)}', 'error')
    
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
