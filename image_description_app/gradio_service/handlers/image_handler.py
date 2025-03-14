import aiohttp
import io
from PIL import Image

async def describe_image(API_GATEWAY_URL, image, model_name):
    try:
        # Конвертируем изображение в WebP
        img_pil = Image.fromarray(image)
        webp_buffer = io.BytesIO()
        img_pil.save(webp_buffer, "webp", lossless=True)
        webp_buffer.seek(0)
        image_bytes = webp_buffer.getvalue()

        del img_pil  # Явное удаление img_pil

        data = aiohttp.FormData()
        data.add_field('file',
                       image_bytes,
                       filename='image.webp',
                       content_type='image/webp')

        data.add_field('model_name', model_name)

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{API_GATEWAY_URL}/api/images/upload", data=data) as response:
                response.raise_for_status()
                return "Изображение отправлено на обработку."
    except Exception as e:
        return f"Ошибка: {e}"