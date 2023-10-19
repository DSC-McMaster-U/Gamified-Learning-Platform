'''
Password Validity
1. Minimum 8 characters.
2. The alphabet must be between [a-z]
3. At least one alphabet should be of Upper Case [A-Z]
4. At least 1 number or digit between [0-9].
5. At least 1 character from [ _ or @ or $ ].
'''


from password_strength import PasswordPolicy


# Define password policy
policy = PasswordPolicy.from_names(
    length=8,  # Minimum length
    uppercase=1,  # At least 1 uppercase letter
    numbers=1,  # At least 1 digit
    special=1,  # At least 1 special character
)

def check_password_strength(password):
    result = policy.test(password)
    if not result:
        return None #password is strong enough
    return result #return a list of suggestions

'''
To add to feature/register function (after getting email, username, password):
result = check_password_strength(password)

if not result:
    flash("Password is not strong enough")
else:
    flash("Password is not strong enough. Here are some suggestions: " + ", ".join(result))
    return redirect(url_for("register"))

'''