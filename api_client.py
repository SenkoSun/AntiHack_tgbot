import aiohttp
from typing import Optional, Dict, Any

class BarAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.tokens: Dict[int, str] = {}  # user_id -> token

    async def register(self, user_id: int) -> Dict[str, Any]:
        """Регистрация нового аккаунта"""
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/register") as resp:
                data = await resp.json()
                if data.get("status") == "ok":
                    self.tokens[user_id] = data["token"]
                return data

    async def _request(self, user_id: int, method: str, endpoint: str, 
                       headers: Optional[Dict] = None, json: Optional[Dict] = None) -> Dict:
        token = self.tokens.get(user_id)
        if not token:
            return {"status": "error", "error": "not_registered"}

        default_headers = {
            "Authorization": f"Bearer {token}",
            "X-Time": "20:00"  # Вечернее время для атмосферы
        }
        if headers:
            default_headers.update(headers)

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, 
                f"{self.base_url}{endpoint}",
                headers=default_headers,
                json=json
            ) as resp:
                if resp.status == 401:
                    return {"status": "error", "error": "unauthorized"}
                return await resp.json()

    async def reset(self, user_id: int) -> Dict:
        return await self._request(user_id, "POST", "/reset")

    async def get_menu(self, user_id: int) -> Dict:
        return await self._request(user_id, "GET", "/menu")

    async def order(self, user_id: int, drink_name: str) -> Dict:
        return await self._request(user_id, "POST", "/order", json={"name": drink_name})

    async def mix(self, user_id: int, ingredients: list) -> Dict:
        return await self._request(user_id, "POST", "/mix", json={"ingredients": ingredients})

    async def get_balance(self, user_id: int) -> Dict:
        return await self._request(user_id, "GET", "/balance")

    async def tip(self, user_id: int, amount: int) -> Dict:
        return await self._request(user_id, "POST", "/tip", json={"amount": amount})

    async def get_history(self, user_id: int) -> Dict:
        return await self._request(user_id, "GET", "/history")

    async def get_profile(self, user_id: int) -> Dict:
        return await self._request(user_id, "GET", "/profile")