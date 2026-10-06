VALID_FORM = {
    "name": "Rahul Sharma",
    "roll_no": "10A-01",
    "class_name": "10",
    "section": "A",
    "english": "82",
    "hindi": "75",
    "mathematics": "90",
    "science": "88",
    "social_science": "70",
}


def add_result(client, **overrides):
    data = {**VALID_FORM, **overrides}
    return client.post("/students/new", data=data, follow_redirects=True)


def test_add_result(auth_client):
    rv = add_result(auth_client)
    assert rv.status_code == 200
    assert b"Rahul Sharma" in rv.data
    assert b"Result added" in rv.data


def test_add_result_requires_all_subjects_or_one(auth_client):
    rv = add_result(auth_client, english="", hindi="", mathematics="", science="", social_science="")
    assert b"at least one subject" in rv.data


def test_add_result_rejects_bad_marks(auth_client):
    rv = add_result(auth_client, mathematics="150")
    assert b"between 0 and 100" in rv.data


def test_add_result_rejects_non_numeric_marks(auth_client):
    rv = add_result(auth_client, english="abc")
    assert b"must be a number" in rv.data


def test_duplicate_roll_number(auth_client):
    add_result(auth_client)
    rv = add_result(auth_client, name="Someone Else")
    assert b"already exists" in rv.data


def test_missing_required_field(auth_client):
    rv = add_result(auth_client, name="")
    assert b"Name is required" in rv.data


def test_dashboard_lists_result(auth_client):
    add_result(auth_client)
    rv = auth_client.get("/")
    assert b"10A-01" in rv.data
    assert b"PASS" in rv.data


def test_search(auth_client):
    add_result(auth_client)
    rv = auth_client.get("/?q=Rahul")
    assert b"Rahul Sharma" in rv.data
    rv = auth_client.get("/?q=ZZZZ")
    assert b"Rahul Sharma" not in rv.data


def test_detail_page(auth_client):
    add_result(auth_client)
    rv = auth_client.get("/students/1")
    assert rv.status_code == 200
    assert b"Result Sheet" in rv.data
    assert b"Mathematics" in rv.data


def test_detail_404(auth_client):
    rv = auth_client.get("/students/999")
    assert rv.status_code == 404


def test_edit_result(auth_client):
    add_result(auth_client)
    rv = auth_client.post(
        "/students/1/edit",
        data={**VALID_FORM, "name": "Rahul Sharma Updated", "mathematics": "95"},
        follow_redirects=True,
    )
    assert b"Rahul Sharma Updated" in rv.data
    assert b"Result updated" in rv.data


def test_delete_result(auth_client):
    add_result(auth_client)
    rv = auth_client.post("/students/1/delete", follow_redirects=True)
    assert b"Deleted result" in rv.data
    rv = auth_client.get("/")
    assert b"Rahul Sharma" not in rv.data


def test_edit_prefills_form(auth_client):
    add_result(auth_client)
    rv = auth_client.get("/students/1/edit")
    assert b"Rahul Sharma" in rv.data
    assert b'value="82"' in rv.data
