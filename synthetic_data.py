import json
import os

def generate_data():
    curriculum = [
        {
            "id": "CS101",
            "name": "Introduction to Programming",
            "complexity": 1,
            "prerequisites": [],
            "estimated_base_hours": 10,
            "recommended_activities": ["theory", "coding", "quizzes"]
        },
        {
            "id": "CS102",
            "name": "Data Structures",
            "complexity": 3,
            "prerequisites": ["CS101"],
            "estimated_base_hours": 15,
            "recommended_activities": ["coding", "quizzes"]
        },
        {
            "id": "CS103",
            "name": "Algorithms",
            "complexity": 4,
            "prerequisites": ["CS102"],
            "estimated_base_hours": 20,
            "recommended_activities": ["theory", "coding"]
        },
        {
            "id": "CS201",
            "name": "Operating Systems",
            "complexity": 4,
            "prerequisites": ["CS102"],
            "estimated_base_hours": 25,
            "recommended_activities": ["theory", "coding"]
        },
        {
            "id": "CS202",
            "name": "Computer Networks",
            "complexity": 3,
            "prerequisites": ["CS101"],
            "estimated_base_hours": 15,
            "recommended_activities": ["theory", "quizzes"]
        },
        {
            "id": "CS301",
            "name": "Databases",
            "complexity": 3,
            "prerequisites": ["CS102"],
            "estimated_base_hours": 20,
            "recommended_activities": ["theory", "coding"]
        },
        {
            "id": "CS302",
            "name": "Machine Learning",
            "complexity": 5,
            "prerequisites": ["CS103"],
            "estimated_base_hours": 30,
            "recommended_activities": ["theory", "coding", "projects"]
        },
        {
            "id": "CS401",
            "name": "Deep Learning",
            "complexity": 5,
            "prerequisites": ["CS302"],
            "estimated_base_hours": 30,
            "recommended_activities": ["theory", "coding", "projects"]
        }
    ]

    student_profiles = [
        {
            "profile_id": "profile_1",
            "name": "Weekend Warrior",
            "daily_available_hours": 2.0,
            "target_days": 14,
            "baseline_confidence": {
                "CS101": 0.9,
                "CS102": 0.5,
                "CS103": 0.2,
                "CS201": 0.1,
                "CS202": 0.4,
                "CS301": 0.3,
                "CS302": 0.1,
                "CS401": 0.0
            }
        },
        {
            "profile_id": "profile_2",
            "name": "Full-Time Bootcamper",
            "daily_available_hours": 8.0,
            "target_days": 7,
            "baseline_confidence": {
                "CS101": 0.8,
                "CS102": 0.8,
                "CS103": 0.6,
                "CS201": 0.5,
                "CS202": 0.5,
                "CS301": 0.6,
                "CS302": 0.2,
                "CS401": 0.1
            }
        },
        {
            "profile_id": "profile_3",
            "name": "Casual Learner",
            "daily_available_hours": 1.5,
            "target_days": 30,
            "baseline_confidence": {
                "CS101": 1.0,
                "CS102": 0.7,
                "CS103": 0.4,
                "CS201": 0.2,
                "CS202": 0.2,
                "CS301": 0.2,
                "CS302": 0.0,
                "CS401": 0.0
            }
        }
    ]
    
    with open("curriculum.json", "w") as f:
        json.dump(curriculum, f, indent=4)
        
    with open("student_profiles.json", "w") as f:
        json.dump(student_profiles, f, indent=4)
        
if __name__ == "__main__":
    generate_data()
