from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer


security_key="some_key123"
algorithm="HS256"

access_token_time_min=10
auth_scheme=OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(auth_scheme)):
    try:
        payload = jwt.decode(token, security_key, algorithms=[algorithm])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
