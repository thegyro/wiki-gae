import re

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)
    

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def valid_email(email):
    return not email or EMAIL_RE.match(email)


def validate(username,password,verify,email):
    params = dict(username=username,email=email)
    have_error = False

    if not valid_username(username):
        params['err_uname'] = "That's not a valid username"
        have_error = True
        
    if not valid_password(password):
        params['err_pass']  = "That's not a valid password"
        have_error = True

    elif password != verify:
        params['err_verify'] = "Your passwords didn't match"
        have_error = True
        
    if not valid_email(email):
        params['err_email'] = "That's not a valid email"
        have_error = True

    return params,have_error
