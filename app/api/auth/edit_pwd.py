# from fastapi import APIRouter
# from app.core.dependencies import badresponse, okresp
# from app.models.db_source.db_adapter import adapter
# from app.models.db_source.db_tables import User

# router = APIRouter()


# @router.put("/change-password")
# async def change_pwd(email: str, password: str):
#     user = await adapter.get_by_value(User, "email", email)
#     if not user:
#         return badresponse("User not found", 404)
