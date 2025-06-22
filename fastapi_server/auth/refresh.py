from fastapi import APIRouter, HTTPException, status, Security
from models.db_source.db_adapter import adapter
from models.tables.db_tables import User
from models.schemas.auth_schemas import UserResponse
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from models.tokens.token_manager import TokenManager
router = APIRouter()

Bear = HTTPBearer(auto_error=False)

@router.get('/refresh')
async def refresh(refresh_token: str = Security(Bear)):

    data = TokenManager.decode_token(refresh_token.credentials)


    if 'error' in data:
        return JSONResponse(content={"message": data['error'], "status":"error"}, status_code=401)
    if data['type'] != 'refresh':
        return JSONResponse(content={"message": "Invalid token type", "status":"error"}, status_code=401)
    

    user_db = adapter.get_by_value(User, 'username', data['username'])

    if user_db == []:
        return JSONResponse(content={"message": "Invalid token", "status":"error"}, status_code=401)

    user_db = user_db[0]

    new_access_token = TokenManager.create_token(
        {
            "username": user_db.username,
            "type": "access"
        },
        TokenManager.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    return {'new_access_token': new_access_token}