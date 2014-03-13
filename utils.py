import hashlib
import random
import hmac
from string import letters

def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name,pw,salt = None):
    if not salt:
        salt = make_salt()

    hex_pw = hashlib.sha256(name + pw + salt).hexdigest()

    return '%s|%s'%(salt,hex_pw)

def valid_pw(name,password,h):
    salt = h.split('|')[0]
    return h == make_pw_hash(name,password,salt)

secret = 'fart'
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret,val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val
