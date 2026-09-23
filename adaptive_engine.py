import json
import math
import requests
from collections import defaultdict, deque
from rag_engine import retrieve_context, retrieve_context_for_topic

def topological_sort(curriculum):
    adj = defaultdict(list)
    in_degree = defaultdict(int)
    nodes = {topic["id"]: topic for topic in curriculum}
    
    for topic in curriculum:
        if topic["id"] not in in_degree:
            in_degree[topic["id"]] = 0
        for prereq in topic["prerequisites"]:
            adj[prereq].append(topic["id"])
            in_degree[topic["id"]] += 1
            if prereq not in in_degree:
                in_degree[prereq] = 0

    queue = deque([node for node in in_degree if in_degree[node] == 0])
    sorted_order = []
    
    while queue:
        current = queue.popleft()
        if current in nodes:
            sorted_order.append(nodes[current])
        for neighbor in adj[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
                
    if len(sorted_order) != len(nodes):
        missing = set(nodes.keys()) - set(t["id"] for t in sorted_order)
        for m in missing:
            sorted_order.append(nodes[m])
            
    return sorted_order

def calculate_adaptive_schedule(curriculum, student_inputs):
    sorted_topics = topological_sort(curriculum)
    
    total_available_hours = student_inputs["daily_available_hours"] * student_inputs["target_days"]
    
    weighted_topics = []
    total_weight = 0
    confidence = student_inputs.get("baseline_confidence", {})
    progress = student_inputs.get("progress", {})
    
    for topic in sorted_topics:
        status = progress.get(topic["id"], "Pending")
        
        if status == "Completed":
            weight = 0
        else:
            conf_level = confidence.get(topic["id"], 0.5)
            deficiency_multiplier = 1.0 + 0.5 * (1.0 - conf_level)
            if status == "Missed":
                deficiency_multiplier *= 1.2  # prioritize missed topics
            weight = topic["complexity"] * deficiency_multiplier
            
        topic_copy = dict(topic)
        topic_copy["weight"] = weight
        weighted_topics.append(topic_copy)
        total_weight += weight
        
    for topic in weighted_topics:
        allocated = (topic["weight"] / total_weight) * total_available_hours if total_weight > 0 else 0
        topic["allocated_hours"] = round(allocated, 2)
        
    return weighted_topics

def generate_ai_study_plan(sequenced_weighted_plan, student_meta, model_name="qwen3:8b"):
    # Extract topics that actually need studying
    remaining_topics = [t for t in sequenced_weighted_plan if t["allocated_hours"] > 0]
    
    prompt = f"""
Act as an expert academic mentor. A student ({student_meta.get('name', 'Student')}) is preparing to study the following topics: {', '.join([t['name'] for t in remaining_topics])}.
Student Profile: {json.dumps(student_meta, indent=2)}

Please provide a highly motivational, encouraging 2-3 sentence introduction to their study plan. 
Acknowledge their progress (if they missed topics, encourage them; if they completed some, congratulate them) and give them a quick tip on how to tackle these topics.
Do NOT generate the timetable itself, only the short introduction.
Respond in clear Markdown format without code blocks.
"""

    intro = ""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False
            },
            timeout=15 # Fast timeout since we only ask for 3 sentences
        )
        response.raise_for_status()
        data = response.json()
        intro = data.get("response", "Welcome to your study plan!")
    except Exception as e:
        intro = f"### Mentor Intro\nWelcome {student_meta.get('name', 'Student')}! Let's get to work on your personalized schedule. (Offline mode active)"
        
    schedule_md = _deterministic_schedule_generator(sequenced_weighted_plan, student_meta)
    
    return f"{intro}\n\n---\n\n{schedule_md}"
        
def _deterministic_schedule_generator(sequenced_weighted_plan, student_meta):
    output = []
    output.append(f"## Your Adaptive Day-by-Day Schedule")
    output.append(f"*Total Target Days: {student_meta.get('target_days', 7)} | Daily Hours: {student_meta.get('daily_available_hours', 2)}*")
    
    day = 1
    current_day_hours = 0
    max_daily = student_meta.get('daily_available_hours', 2)
    
    if max_daily <= 0:
        return "Error: Daily available hours must be greater than 0."

    output.append(f"\n### 📅 Day {day}")
    
    for topic in sequenced_weighted_plan:
        topic_hours = topic["allocated_hours"]
        is_new_topic = True
        
        while topic_hours > 0.01:
            if current_day_hours >= max_daily:
                day += 1
                current_day_hours = 0
                if day > student_meta.get('target_days', 7) * 2: # Failsafe
                    break
                output.append(f"\n### 📅 Day {day}")
                
            remaining_in_day = max_daily - current_day_hours
            
            # Smart Anti-Fragmentation Logic:
            # If we are starting a NEW topic, and there is very little time left today (< 0.6 hrs or < 25% of daily max)
            # and the topic is heavier than the time remaining, push it to the next day to prevent meaningless cognitive splitting.
            if current_day_hours > 0 and is_new_topic and remaining_in_day < max(0.6, max_daily * 0.25) and topic_hours > remaining_in_day:
                day += 1
                current_day_hours = 0
                if day > student_meta.get('target_days', 7) * 2:
                    break
                output.append(f"\n### 📅 Day {day} *(Focus Shift)*")
                remaining_in_day = max_daily
                
            chunk = min(topic_hours, remaining_in_day)
            output.append(f"- **{topic['name']}**: {chunk:.1f} hours")
            
            # Fetch specific topic details from RAG Knowledge Base
            topic_details = retrieve_context_for_topic(topic['name'])
            output.append(f"  - 📝 **Focus:** {topic_details}")
            
            # Add recommended activities as sub-bullets
            if topic.get('recommended_activities'):
                acts = ", ".join(topic['recommended_activities'])
                output.append(f"  - 🔹 **Activities:** {acts}")
                    
            topic_hours -= chunk
            current_day_hours += chunk
            is_new_topic = False

    output.append("\n#### 🎯 Daily Checkpoints")
    output.append("- Test yourself using active recall quizzes at the end of each day.")
    output.append("- If you miss a topic, don't panic—update your progress on the dashboard and regenerate the plan tomorrow!")
            
    return "\n".join(output)
