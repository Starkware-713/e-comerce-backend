from fastapi import HTTPException, Depends
from app.utils import get_current_user
from app.models.user import User
from typing import List

#Verifica que el usuario tenga uno de los roles permitidos para acceder a la ruta
def check_rol(allowed_roles: List[str]):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if not current_user.rol or current_user.rol not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"No tienes permisos para realizar esta acción. Roles permitidos: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker