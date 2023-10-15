'''
Password Validity
1. Minimum 8 characters.
2. The alphabet must be between [a-z]
3. At least one alphabet should be of Upper Case [A-Z]
4. At least 1 number or digit between [0-9].
5. At least 1 character from [ _ or @ or $ ].
'''
import re
from password_strength import PasswordStats

specialCharacters=re.compile('[@_!#$%^&*()<>?/\|}{~:]')


def validate_password(password):
    #check password length
    if(len(password)<=8):
        return False
    #check for lowercase character
    elif not re.search("[a-z]", password):
        return False
    #check for upper case character
    elif not re.search("[A-Z]", password):
        return False
    #check for number
    elif not re.search("[0-9]", password):
        return False
    #check for space, newline, return, tab
    elif re.search("\s", password):
        return False
    #check for special character
    elif not re.search(specialCharacters, password):
        return False
    else:
        return True
    
def strength(password):
    stats = PasswordStats(password)
    if(stats.strength()>0.5):
        return 2
    elif(stats.strength()<0.5 and stats.strength()>0.4):
        return 1
    else:
        return 0

def main(): 
    password = input("Input your password: ")
    valid = validate_password(password)
    strength2 = strength(password)

    not_valid = True

    while not_valid:
        if valid:
            print("Valid password")
            if strength2 == 2:
                print('password score: strong')
            not_valid = False
        else:
            print("Password does not meet the requirements, try again")
            if strength2 == 2:
                print('password score: strong')
            elif strength2 == 1:
                print('password score: weak')
            else:
                print('password score: very weak')
            password = input("Input your password: ")
            valid = validate_password(password)

main()