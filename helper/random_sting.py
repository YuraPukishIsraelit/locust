import string, random


# use random string function
def random_string(kind_of_string, string_len):
    return ''.join(random.choice(kind_of_string) for i in range(string_len))


"""This function generate random (valid) email"""


def random_email():
    email = random_string((string.ascii_letters + string.digits), random.randint(2, 63)) + "@" + "gmail.com"

    return email


"""This function generate password between 8-32 characters according to the COOKZ password rules.
    You could set a length of the password by using random_password(10) -> password will include 10 characters
"""


def random_password(len=random.randint(8, 32)):
    password_len = len
    password = random_string((string.ascii_letters + string.digits), password_len)
    upper_case = any(character.isupper() for character in password)
    lower_case = any(character.islower() for character in password)
    digit = any(character.isdigit() for character in password)

    if upper_case and lower_case and digit:
        return password
    else:
        return random_password(password_len)


"""This function generate random_phone between 8-15 digits """


def random_phone():
    phone = "+" + random_string(string.digits, random.randint(8, 15))
    return phone


def random_name(len=random.randint(3, 30)):
    name = random_string(string.ascii_lowercase, len)
    return name


"""This function generate random_username between 2-32 characters according to the COOKZ username rules.
    You could set a length of the password by using random_username(10) -> username will include 10 characters
"""


def random_username(len=random.randint(2, 32)):
    name = random_string((string.ascii_letters + string.digits + "." + '_' + '-'), len)
    return name


'''
Helpers for using random string function

random.choice() is used to generate strings in which characters may repeat, 
while random.sample() is used for non-repeating characters.

Method	Description
string.ascii_uppercase	Returns a string with uppercase characters
string.ascii_lowercase	Returns a string with lowercase characters
string.ascii_letters	Returns a string with both lowercase and uppercase characters
string.digits	Returns a string with numeric characters
string.punctuation	Returns a string with punctuation characters

random.randint(0, 9)	Returns any random integer from 0 to 9
random.randrange(2, 20, 2)	Returns any random integer from 2 to 20 with step 2
random.randrange(100, 1000, 3)	Returns any random integer of specific length 3
random.randrange(-50, -5)	Returns any random negative integer between -50 to -6.
random.sample(range(0, 1000), 10)	Returns a list of random numbers
secrets.randbelow(10)	Returns a secure random number
'''
