import aiohttp

from loader import CRYPTO_PAY_TOKEN

API_URL = "https://pay.send.tg/api"

async def create_invoice(amount: float, currency: str = "USD"):
    headers = {"Crypto-Pay-API-Token": CRYPTO_PAY_TOKEN}
    payload = {
        "amount": str(amount),
        "currency_type": "fiat",
        "fiat": currency,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/createInvoice", json=payload, headers=headers) as resp:
            try:
                return await resp.json()
            except Exception:
                return {"ok": False}

async def get_invoice(invoice_id: int):
    headers = {"Crypto-Pay-API-Token": CRYPTO_PAY_TOKEN}
    params = {"invoice_ids": invoice_id}
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/getInvoices", params=params, headers=headers) as resp:
            try:
                data = await resp.json()
            except Exception:
                return None
            if not data.get("ok"):
                return None
            items = data.get("result", {}).get("items", [])
            return items[0] if items else None
