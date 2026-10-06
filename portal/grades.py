PASS_MARK = 33


def grade_for(percentage):
    if percentage >= 90:
        return "A+"
    if percentage >= 80:
        return "A"
    if percentage >= 70:
        return "B"
    if percentage >= 60:
        return "C"
    if percentage >= 50:
        return "D"
    return "F"


def summarize(marks):
    if not marks:
        return {
            "total": 0,
            "max_total": 0,
            "percentage": 0.0,
            "grade": "-",
            "passed": False,
        }
    total = sum(m["marks_obtained"] for m in marks)
    max_total = 100 * len(marks)
    percentage = total / max_total * 100
    passed = all(m["marks_obtained"] >= PASS_MARK for m in marks)
    return {
        "total": round(total, 2),
        "max_total": max_total,
        "percentage": round(percentage, 2),
        "grade": grade_for(percentage),
        "passed": passed,
    }
