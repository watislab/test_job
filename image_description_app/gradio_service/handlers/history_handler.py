import aiohttp


async def load_history(API_GATEWAY_URL, offset=0):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_GATEWAY_URL}/api/results?offset={offset}&limit=10") as response:
                response.raise_for_status()
                results = await response.json()
                history_items = []
                for result in results:
                    history_items.append((result['description'], result['model_name']))
                return history_items
    except Exception as e:
        return [f"Ошибка: {e}"]

async def load_more(API_GATEWAY_URL, offset, gallery):
    try:
        new_offset = offset + 10
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_GATEWAY_URL}/api/results?offset={new_offset}&limit=10") as response:
                response.raise_for_status()
                results = await response.json()
                new_history_items = []
                for result in results:
                    new_history_items.append((result['description'], result['model_name']))
        # Append the new items to the existing gallery
        updated_gallery = gallery + new_history_items
        return new_offset, updated_gallery
    except Exception as e:
        return offset, gallery + [f"Ошибка: {e}"]