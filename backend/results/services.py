def calculate_grade(percentage: float, rules: list) -> str:
    for rule in sorted(rules, key=lambda r: r.get('min', 0), reverse=True):
        if percentage >= rule.get('min', 0):
            return rule.get('grade', 'F')
    return 'F'


def calculate_gpa(marks_entries) -> float:
    grade_points = {'A+': 4.0, 'A': 3.7, 'B+': 3.3, 'B': 3.0, 'C+': 2.7, 'C': 2.3, 'D': 2.0, 'F': 0}
    total = 0
    count = 0
    for entry in marks_entries:
        gp = grade_points.get(entry.grade, 0)
        total += gp
        count += 1
    return round(total / count, 2) if count else 0.0
