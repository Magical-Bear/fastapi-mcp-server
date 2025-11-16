from dotenv import load_dotenv
load_dotenv()
import os
import base64
import aiohttp
import asyncio
from pathlib import Path
from fastapi import File, UploadFile

phone_api_key = os.getenv("PHONE_API_KEY")
ocr_api_key = os.getenv("OCR_API_KEY")
dify_api_key = os.getenv("DIFY_API_KEY")



async def query_mobile_info(phone: int):
    """
    使用 aiohttp 请求聚合数据手机归属地 API
    """
    url = "http://apis.juhe.cn/mobile/get"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    params = {
        "phone": phone,
        "key": phone_api_key
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as resp:
            # 聚合返回通常是 json
            return await resp.json()


async def ocr_image(image_path: str):
    """
    使用聚合数据 - 通用文字识别（高精度版）OCR
    自动读取图片并转换为 Base64

    :param image_path: 本地图片路径
    :param key: 聚合数据申请的 key
    :return: OCR JSON 结果
    """
    url = "http://v.juhe.cn/generalaccurateOcr/index"

    # 读取并转 Base64
    image_file = Path(image_path)
    if not image_file.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    image_base64 = base64.b64encode(image_file.read_bytes()).decode()


    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "key": ocr_api_key,
        "ImageBase64": image_base64
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as resp:
            return await resp.json()


async def upload_file(file_path: str):
    url = f"http://127.0.0.1:{int(os.getenv('SERVER_PORT'))}/server/upload"
    file = Path(file_path)
    if not file.exists():
        raise FileNotFoundError(file_path)

    async with aiohttp.ClientSession() as session:
        # multipart/form-data
        data = aiohttp.FormData()
        data.add_field(
            name="file",
            value=file.open("rb"),
            filename=file.name,
            content_type="application/octet-stream"
        )

        async with session.post(url, data=data) as resp:
            return await resp.json()


async def download_file(save_as: str):
    url = f"http://127.0.0.1:{int(os.getenv('SERVER_PORT'))}/server/download/{save_as}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:

            if resp.status != 200:
                raise RuntimeError(f"Download failed: {resp.status}")

            save_path = Path(save_as)

            # Streaming download
            with save_path.open("wb") as f:
                async for chunk in resp.content.iter_chunked(1024):
                    f.write(chunk)

            return f"Saved to {save_path}"

async def send_light_control(light_id: str, status: bool):
    url = f"http://127.0.0.1:{int(os.getenv('SERVER_PORT'))}/mqtt/light-control"

    payload = {
        "light_id": light_id,
        "status": status
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            result = await resp.json()
            return result


async def get_light_status():
    url = f"http://127.0.0.1:{int(os.getenv('SERVER_PORT'))}/mqtt/light-status"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            result = await resp.json()
            return result


async def chat_with_dify(query: str):
    url = f"http://127.0.0.1:8001/v1/chat-messages"
    header = {
        "Authorization": f"Bearer {dify_api_key}",
    }
    print(header)
    body = {
        "inputs": {
            "base_city": "硅谷山景城"
        },
        "query": query,
        "response_model": "blocking",
        "user": "bill"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=header, json=body) as resp:
            result = await resp.json()
    return result


async def file_upload(image: UploadFile) -> str | None:
    form_data = aiohttp.FormData()
    form_data.add_field(
        "file",
        await image.read(),  # 直接读取内存中的文件内容
        filename=image.filename,
        content_type=image.content_type
    )
    form_data.add_field("user", "bill")

    headers = {
        "Authorization": f"Bearer {dify_api_key}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"http://127.0.0.1:8001/v1/files/upload", data=form_data, headers=headers) as resp:
            try:
                result = await resp.json()
                return result.get("id", None)
            except Exception as e:
                return None




async def mqtt_main():
    print(await get_light_status())
    print(await send_light_control("123", True))
    print(await get_light_status())


# ===== 外部调用示例 =====
if __name__ == "__main__":
    # result = asyncio.run(query_mobile_info(18281593637))
    # print(result)

    # result = asyncio.run(ocr_image("1.jpg"))
    # print(result)

    # result = asyncio.run(upload_file(
    #     "1.jpg"
    # ))
    # print(result)
    # result = asyncio.run(download_file(
    #     "a5c5e61087394f2ca0c167d878c3cb0f.jpg"
    # ))
    # print(result)

    # asyncio.run(mqtt_main())
    result = asyncio.run(chat_with_dify("你总部在哪里,附近还有出名的企业"))
    print(result)
    pass
