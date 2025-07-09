import jwt


def generate_jwt_token(payload, algo, key):
    return jwt.encode(
        payload,
        key,
        algorithm=algo
    )


def decode_jwt_token(token, algo, key):
    return jwt.decode(
        token,
        key,
        algorithms=[algo]
    )
