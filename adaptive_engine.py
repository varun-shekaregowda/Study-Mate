import json
import math
from collections import defaultdict, deque
import google.generativeai as genai

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

def generate_ai_study_plan(sequenced_weighted_plan, student_meta, api_key=None):
    if not api_key:
        return _offline_fallback_generator(sequenced_weighted_plan, student_meta)
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        
        prompt = f"""
Act as an expert academic scheduler and mentor. I am providing a sequenced and mathematically weighted list of topics.
Student Profile: {json.dumps(student_meta, indent=2)}
Sequenced Plan (Completed topics have 0 allocated_hours): {json.dumps(sequenced_weighted_plan, indent=2)}

First, evaluate the student's progress. If they have completed topics, congratulate them. If they have missed topics, provide highly motivational encouragement to get them back on track. 
Next, provide advice on the order they should study the *remaining* topics (allocated_hours > 0) based on complexity and prerequisites.
Then, generate a refined, detailed day-by-day study timetable ONLY for the remaining topics. Allocate the total hours intelligently.
For each day, include a clear description of what exactly should be studied, along with active recall tasks, hands-on activities, and evaluation checkpoints.
Respond in clear, structured Markdown format without any markdown code block enclosures like ```markdown. 
Just return the markdown text directly.
"""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"### AI Generation Failed\nAn error occurred: {str(e)}\n\n" + _offline_fallback_generator(sequenced_weighted_plan, student_meta)
        
def _offline_fallback_generator(sequenced_weighted_plan, student_meta):
    output = []
    output.append(f"## Offline Mock Schedule for {student_meta.get('name', 'Student')}")
    output.append(f"Total Target Days: {student_meta.get('target_days', 7)} | Daily Hours: {student_meta.get('daily_available_hours', 2)}")
    
    day = 1
    current_day_hours = 0
    max_daily = student_meta.get('daily_available_hours', 2)
    
    if max_daily <= 0:
        return "Error: Daily available hours must be greater than 0."

    output.append(f"### Day {day}")
    
    for topic in sequenced_weighted_plan:
        topic_hours = topic["allocated_hours"]
        while topic_hours > 0.01:
            if current_day_hours >= max_daily:
                day += 1
                current_day_hours = 0
                if day > student_meta.get('target_days', 7) * 2:
                    break
                output.append(f"\n### Day {day}")
                
            chunk = min(topic_hours, max_daily - current_day_hours)
            output.append(f"- **{topic['name']}**: {chunk:.1f} hours ({', '.join(topic['recommended_activities'])})")
            topic_hours -= chunk
            current_day_hours += chunk

    output.append("\n#### Checkpoints")
    output.append("- Daily: Active recall quiz.")
    output.append("- End of Plan: Comprehensive evaluation.")
            
    return "\n".join(output)
