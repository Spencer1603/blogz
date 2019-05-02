import hashlib
import random
import string

#generates a random string to apend to the hash 
def make_salt():
    return ''.join([random.choice(string.ascii_letters) for x in range(7)])


#generates a hashed version of the password given and adds the salt
#before returning to the database
def make_pw_hash(password, salt=None):
    if not salt:
        salt = make_salt()
    hash = hashlib.sha256(str.encode(password + salt)).hexdigest()
    return '{0},{1}'.format(hash, salt)

#checks to see if the hash created from the password given matches the
#hash stored in the database
def check_pw_hash(password, hash):
    salt = hash.split(',')[1]
    if make_pw_hash(password, salt) == hash:
        return True

    return False