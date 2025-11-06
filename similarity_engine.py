"""
Similarity Engine Module
Implements A* Search Algorithm for optimal roommate matching
Previously used KNN-style distance calculation, now upgraded to A* for optimal solutions
"""
from config import Config
import heapq
from typing import List, Dict, Tuple, Set

class SimilarityEngine:
    """Calculate similarity scores between students using weighted distance metrics"""
    
    def __init__(self, weights=None):
        """Initialize with feature weights"""
        self.weights = weights or Config.WEIGHTS
    
    def calculate_distance(self, student1_vector, student2_vector):
        """
        Calculate weighted Euclidean distance between two student vectors
        Lower distance = higher similarity
        """
        total_distance = 0.0
        
        # Sleep time distance (0-2 scale, normalized to 0-1)
        sleep_diff = abs(student1_vector['sleep_time'] - student2_vector['sleep_time']) / 2.0
        total_distance += self.weights['sleep_time'] * sleep_diff
        
        # Study time distance (0-3 scale, normalized to 0-1)
        study_diff = abs(student1_vector['study_time'] - student2_vector['study_time']) / 3.0
        total_distance += self.weights['study_time'] * study_diff
        
        # Cleanliness distance (1-5 scale, normalized to 0-1)
        clean_diff = abs(student1_vector['cleanliness'] - student2_vector['cleanliness']) / 4.0
        total_distance += self.weights['cleanliness'] * clean_diff
        
        # Noise tolerance distance (1-5 scale, normalized to 0-1)
        noise_diff = abs(student1_vector['noise_tolerance'] - student2_vector['noise_tolerance']) / 4.0
        total_distance += self.weights['noise_tolerance'] * noise_diff
        
        # Personality distance (0-2 scale, normalized to 0-1)
        personality_diff = abs(student1_vector['personality'] - student2_vector['personality']) / 2.0
        total_distance += self.weights['personality'] * personality_diff
        
        # Hobby overlap score (inverse - more overlap = less distance)
        hobby_overlap = self.calculate_hobby_overlap(
            student1_vector['hobbies'], 
            student2_vector['hobbies']
        )
        hobby_distance = 1.0 - hobby_overlap
        total_distance += self.weights['hobbies'] * hobby_distance
        
        return total_distance
    
    def calculate_hobby_overlap(self, hobbies1, hobbies2):
        """
        Calculate Jaccard similarity for hobbies
        Returns value between 0 and 1
        """
        if not hobbies1 and not hobbies2:
            return 0.5  # Neutral if both have no hobbies
        
        set1 = set(hobbies1)
        set2 = set(hobbies2)
        
        if not set1 or not set2:
            return 0.0  # No overlap if one is empty
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def calculate_similarity_score(self, student1_vector, student2_vector):
        """
        Convert distance to similarity score (0-100 scale)
        Also generate reasons for the match
        """
        distance = self.calculate_distance(student1_vector, student2_vector)
        
        # Convert distance (0-1) to similarity score (100-0)
        # Apply bonus for high hobby overlap
        base_score = (1.0 - distance) * 100
        
        hobby_overlap = self.calculate_hobby_overlap(
            student1_vector['hobbies'], 
            student2_vector['hobbies']
        )
        
        # Apply bonus multiplier if hobby overlap is high
        if hobby_overlap > 0.5:
            base_score *= Config.HOBBY_OVERLAP_BONUS
            base_score = min(base_score, 100)  # Cap at 100
        
        # Generate match reasons
        reasons = self.generate_match_reasons(student1_vector, student2_vector)
        
        return round(base_score, 2), reasons
    
    def generate_match_reasons(self, student1_vector, student2_vector):
        """Generate human-readable reasons for why two students are compatible"""
        reasons = []
        
        # Sleep time compatibility
        if student1_vector['sleep_time'] == student2_vector['sleep_time']:
            sleep_labels = {0: "early birds", 1: "moderate sleepers", 2: "night owls"}
            reasons.append(f"Both are {sleep_labels[student1_vector['sleep_time']]}")
        
        # Study time compatibility
        if student1_vector['study_time'] == student2_vector['study_time']:
            study_labels = {0: "morning studiers", 1: "afternoon studiers", 
                          2: "evening studiers", 3: "night studiers"}
            reasons.append(f"Both prefer {study_labels[student1_vector['study_time']]}")
        
        # Cleanliness compatibility
        clean_diff = abs(student1_vector['cleanliness'] - student2_vector['cleanliness'])
        if clean_diff <= 1:
            reasons.append("Similar cleanliness standards")
        
        # Noise tolerance compatibility
        noise_diff = abs(student1_vector['noise_tolerance'] - student2_vector['noise_tolerance'])
        if noise_diff <= 1:
            reasons.append("Compatible noise tolerance levels")
        
        # Personality compatibility
        personality_labels = {0: "introverted", 1: "balanced", 2: "extroverted"}
        if student1_vector['personality'] == student2_vector['personality']:
            reasons.append(f"Both have {personality_labels[student1_vector['personality']]} personality")
        
        # Hobby overlap
        hobby_overlap = self.calculate_hobby_overlap(
            student1_vector['hobbies'], 
            student2_vector['hobbies']
        )
        if hobby_overlap > 0:
            common_hobbies = set(student1_vector['hobbies']).intersection(
                set(student2_vector['hobbies'])
            )
            if len(common_hobbies) > 0:
                reasons.append(f"Share hobbies: {', '.join(list(common_hobbies)[:3])}")
        
        return reasons if reasons else ["Balanced overall compatibility"]
    
    def calculate_all_similarities(self, student_vectors):
        """
        Calculate similarity scores between all pairs of students
        Returns a dictionary: {(id1, id2): (score, reasons)}
        """
        similarities = {}
        n = len(student_vectors)
        
        for i in range(n):
            for j in range(i + 1, n):
                student1 = student_vectors[i]
                student2 = student_vectors[j]
                
                score, reasons = self.calculate_similarity_score(student1, student2)
                
                # Store bidirectionally for easy lookup
                similarities[(student1['id'], student2['id'])] = (score, reasons)
                similarities[(student2['id'], student1['id'])] = (score, reasons)
        
        return similarities


class AStarMatcher:
    """
    A* Search Algorithm for Optimal Roommate Matching
    
    State Space: Different matching arrangements of students
    Goal State: All students matched with maximum total compatibility
    Heuristic: Optimistic estimate of remaining compatibility potential
    Cost: Negative of total compatibility (to minimize cost = maximize compatibility)
    """
    
    def __init__(self, similarity_engine=None):
        """Initialize A* matcher with similarity engine"""
        self.similarity_engine = similarity_engine or SimilarityEngine()
        self.best_solution = None
        self.nodes_explored = 0
    
    class MatchingState:
        """Represents a state in the A* search space"""
        def __init__(self, matched_pairs, unmatched_students, total_score, g_cost, h_cost):
            self.matched_pairs = matched_pairs  # List of (student1_id, student2_id, score, reasons)
            self.unmatched_students = unmatched_students  # Set of unmatched student IDs
            self.total_score = total_score  # Total compatibility score so far
            self.g_cost = g_cost  # Actual cost (negative of total score)
            self.h_cost = h_cost  # Heuristic cost estimate
            self.f_cost = g_cost + h_cost  # Total estimated cost
        
        def __lt__(self, other):
            """For priority queue comparison"""
            return self.f_cost < other.f_cost
        
        def __eq__(self, other):
            """Check if two states are equal"""
            return (frozenset(self.matched_pairs) == frozenset(other.matched_pairs) and
                    self.unmatched_students == other.unmatched_students)
        
        def __hash__(self):
            """Make state hashable for visited set"""
            return hash((frozenset(self.matched_pairs), frozenset(self.unmatched_students)))
    
    def calculate_heuristic(self, unmatched_students, similarity_matrix):
        """
        Admissible heuristic: Optimistic estimate of best possible remaining score
        Takes maximum possible compatibility for each remaining student
        """
        if len(unmatched_students) <= 1:
            return 0.0
        
        # For each unmatched student, find their best possible match score
        max_possible_score = 0.0
        remaining = list(unmatched_students)
        
        for i, student_id in enumerate(remaining):
            best_score = 0.0
            for j, other_id in enumerate(remaining):
                if i != j and (student_id, other_id) in similarity_matrix:
                    score = similarity_matrix[(student_id, other_id)][0]
                    best_score = max(best_score, score)
            max_possible_score += best_score
        
        # Divide by 2 since each pair is counted twice
        max_possible_score /= 2
        
        # Return negative (since we minimize cost)
        return -max_possible_score
    
    def generate_successors(self, state, similarity_matrix):
        """Generate all possible next states by matching one more pair"""
        successors = []
        unmatched_list = list(state.unmatched_students)
        
        if len(unmatched_list) < 2:
            return successors
        
        # Try matching the first unmatched student with each other unmatched student
        first_student = unmatched_list[0]
        
        for i in range(1, len(unmatched_list)):
            second_student = unmatched_list[i]
            
            # Get compatibility score
            if (first_student, second_student) in similarity_matrix:
                score, reasons = similarity_matrix[(first_student, second_student)]
            else:
                score, reasons = 0.0, []
            
            # Create new state
            new_matched_pairs = state.matched_pairs + [(first_student, second_student, score, reasons)]
            new_unmatched = state.unmatched_students - {first_student, second_student}
            new_total_score = state.total_score + score
            new_g_cost = -new_total_score  # Negative because we minimize cost
            new_h_cost = self.calculate_heuristic(new_unmatched, similarity_matrix)
            
            new_state = self.MatchingState(
                matched_pairs=new_matched_pairs,
                unmatched_students=new_unmatched,
                total_score=new_total_score,
                g_cost=new_g_cost,
                h_cost=new_h_cost
            )
            
            successors.append(new_state)
        
        return successors
    
    def is_goal_state(self, state):
        """Check if all students are matched"""
        return len(state.unmatched_students) == 0
    
    def a_star_search(self, student_vectors):
        """
        A* Search to find optimal roommate matching
        
        Args:
            student_vectors: List of student vector dictionaries
        
        Returns:
            List of matched pairs with scores and reasons
        """
        self.nodes_explored = 0
        
        # Calculate all pairwise similarities first
        similarity_matrix = self.similarity_engine.calculate_all_similarities(student_vectors)
        
        # Initialize start state
        all_student_ids = {student['id'] for student in student_vectors}
        initial_state = self.MatchingState(
            matched_pairs=[],
            unmatched_students=all_student_ids,
            total_score=0.0,
            g_cost=0.0,
            h_cost=self.calculate_heuristic(all_student_ids, similarity_matrix)
        )
        
        # Priority queue (min-heap) for A* search
        open_list = []
        heapq.heappush(open_list, initial_state)
        
        # Closed set to track visited states
        closed_set = set()
        
        # A* search loop
        while open_list:
            # Get state with lowest f_cost
            current_state = heapq.heappop(open_list)
            self.nodes_explored += 1
            
            # Check if goal reached
            if self.is_goal_state(current_state):
                self.best_solution = current_state
                return current_state.matched_pairs
            
            # Skip if already visited
            if current_state in closed_set:
                continue
            
            closed_set.add(current_state)
            
            # Generate and explore successors
            successors = self.generate_successors(current_state, similarity_matrix)
            
            for successor in successors:
                if successor not in closed_set:
                    heapq.heappush(open_list, successor)
        
        # No solution found (shouldn't happen with even number of students)
        return []
    
    def match_students(self, student_vectors):
        """
        Main method to match students using A* algorithm
        
        Args:
            student_vectors: List of student vector dictionaries
        
        Returns:
            Dictionary with matches and statistics
        """
        if len(student_vectors) < 2:
            return {
                'matches': [],
                'total_score': 0.0,
                'average_score': 0.0,
                'nodes_explored': 0,
                'unmatched': [s['id'] for s in student_vectors]
            }
        
        # Handle odd number of students
        unmatched_students = []
        if len(student_vectors) % 2 == 1:
            # Leave out the last student
            unmatched_students = [student_vectors[-1]['id']]
            student_vectors = student_vectors[:-1]
        
        # Run A* search
        matched_pairs = self.a_star_search(student_vectors)
        
        # Calculate statistics
        total_score = sum(pair[2] for pair in matched_pairs)
        average_score = total_score / len(matched_pairs) if matched_pairs else 0.0
        
        return {
            'matches': matched_pairs,
            'total_score': round(total_score, 2),
            'average_score': round(average_score, 2),
            'nodes_explored': self.nodes_explored,
            'unmatched': unmatched_students
        }
