import bcrypt
import core.db as db
from core.models import User
import jwt
import os

jwt_secret = os.environ.get('JWT_SECRET')

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create(email, password):
    user = None

    with db.session() as session:
        user = User()
        user.email = email
        user.hashed_password = hash_password(password)
        db.save(user)

    return user

def update(user_id, data):
    user = find(user_id)
    if user is None:
        return None

    for key, val in data.items():
        setattr(user, key, val)

    with db.session() as session:
        db.save(user)

    return user

def update_password(email, password):
    user = None
    with db.session() as session:
        user = User.query.filter(User.email == email).first()

    if user is not None:
        user = update(user.id, { 'hashed_password': hash_password(password) })

    return user

def find(user_id):
    user = None
    with db.session() as session:
        user = User.query.filter(User.id == user_id).first()
    return user

def authenticate(email, password):
    user = None
    with db.session() as session:
        user = User.query.filter(User.email == email).first()

    if user is None:
        return None

    if bcrypt.checkpw(password.encode('utf8'), user.hashed_password.encode('utf-8')):
        return user
    else:
        return None

def encode_token(user):
    return jwt.encode({'user_id': user.id}, jwt_secret, algorithm='HS256').decode('utf-8')

def decode_token(token):
    try:
        data = jwt.decode(token, jwt_secret, algorithm='HS256')
        return find(data['user_id'])
    except jwt.exceptions.InvalidSignatureError:
        return None
    except jwt.exceptions.DecodeError:
        return None

if __name__ == '__main__':
    import argparse
    import settings

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    create_parser = subparsers.add_parser('create')
    create_parser.add_argument('--email', required=True)
    create_parser.add_argument('--password', required=True)

    update_parser = subparsers.add_parser('update')
    update_parser.add_argument('--email', required=True)
    update_parser.add_argument('--password', required=True)

    args = parser.parse_args()

    if args.command == 'create':
        user = create(args.email, args.password)
        print('ok')
    elif args.command == 'update':
        user = update_password(args.email, args.password)
        if user is not None:
            print('ok')
        else:
            print('no user')
    else:
        parser.print_help()
        exit(1)
