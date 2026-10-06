from portal.grades import grade_for, summarize


def test_grade_boundaries():
    assert grade_for(95) == "A+"
    assert grade_for(90) == "A+"
    assert grade_for(85) == "A"
    assert grade_for(75) == "B"
    assert grade_for(65) == "C"
    assert grade_for(55) == "D"
    assert grade_for(40) == "F"


def test_summarize_pass():
    marks = [
        {"subject": "English", "marks_obtained": 80},
        {"subject": "Mathematics", "marks_obtained": 70},
    ]
    result = summarize(marks)
    assert result["total"] == 150
    assert result["max_total"] == 200
    assert result["percentage"] == 75.0
    assert result["grade"] == "B"
    assert result["passed"] is True


def test_summarize_fail_on_low_subject():
    marks = [
        {"subject": "English", "marks_obtained": 90},
        {"subject": "Mathematics", "marks_obtained": 20},
    ]
    result = summarize(marks)
    assert result["passed"] is False


def test_summarize_empty():
    result = summarize([])
    assert result["total"] == 0
    assert result["percentage"] == 0.0
    assert result["grade"] == "-"
    assert result["passed"] is False
