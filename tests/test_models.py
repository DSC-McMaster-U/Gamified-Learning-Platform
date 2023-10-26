import pytest
from app.src.models import User, GradeEnum

# Sample model
james = User(name="James Smith",username="jsmith", email="jsmith99@gmail.com", age=18, grade=GradeEnum.SOPHMORE, favorite_subject="Computer Science")
james.set_password("jsmith123")

def test_models():
    
    # Checking everything is correct
    assert james.name == "James Smith"
    assert james.username == "jsmith"
    assert james.email == "jsmith99@gmail.com"
    assert james.age == 18
    assert james.grade == GradeEnum.SOPHMORE
    assert james.favorite_subject == "Computer Science"
    assert james.check_password("jsmith123")


@pytest.mark.xfail(reason="Invalid passwords and incorrect fields. Pytest should return an 'x', meaning expected fail")
def test_intentional_failure():
    assert james.check_password("password")
    assert james.check_password("Jsmith123")
    assert james.check_password("jsmith12")
    assert james.check_password("")
    assert james.name == "James"
    assert james.name == "JamesSmith"
    assert james.username == "jSmith"
    assert james.username == "jamessmith"
    assert james.email == "jamessmith99@gmail.com"
    assert james.email == "Jsmith99@gmail.com"
    assert james.age == 10
    assert james.age == 180
    assert james.grade == GradeEnum.FRESHMAN
    assert james.grade == GradeEnum.JUNIOR
    assert james.favorite_subject == "COMPUTER SCIENCE"
    assert james.favorite_subject == "Mathematics"