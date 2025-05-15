import httpx
from fastapi import HTTPException, status, Request
from jose import JWTError
from app.config import settings

class SupabaseAuth:
    def __init__(self):
        self.project_id = settings.SUPABASE_PROJECT_ID
        self.jwks_url = settings.SUPABASE_AUTH_JWKS_URL
        self.supabasekey = settings.SUPABASE_KEY
        self._jwks_cache = None

    async def get_jwks(self, user_token=None):
        if self._jwks_cache is None:
            headers = {"apikey": self.supabasekey}
            if user_token:
                headers["Authorization"] = f"Bearer {user_token}"
            async with httpx.AsyncClient() as client:
                resp = await client.get(self.jwks_url, headers=headers)
                resp.raise_for_status()
                self._jwks_cache = resp.json()
        return self._jwks_cache

    async def get_current_user(self, request: Request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid Authorization header"
            )
        token = auth_header.split(" ")[1]
        try:
            jwks = await self.get_jwks(user_token=token)         
            return jwks
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )


supabaseauth=SupabaseAuth()