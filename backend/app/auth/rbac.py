from fastapi import HTTPException, status

# enforce role-based access control (RBAC) by checking if the user's role is in the list of allowed roles


def require_role(user_role: str, allowed_roles: list[str]) -> None:
    if user_role.lower() not in [role.lower() for role in allowed_roles]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )