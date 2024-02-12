from datetime import datetime

# Calculate new user's age based off of their form input
def calculate_age(birthday):
    birthday = datetime.strptime(birthday, "%Y-%m-%d")
    today = datetime.today()

    age = today.year - birthday.year
    
    if ((today.month < birthday.month) or 
       (today.month == birthday.month) and (today.day < birthday.day)):
        age -= 1

    return age
