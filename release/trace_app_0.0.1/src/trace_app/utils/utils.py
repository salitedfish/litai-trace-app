from datetime import datetime, timedelta
from io import BytesIO

import qrcode
from mg_app_framework import log_exception
from reportlab.lib.utils import ImageReader

from trace_app.utils.db import get_collection_handler


def generate_qr(data, filename=None, box_size=10, border=1):
    """生成二维码图片

    Args:
        data: 二维码数据
        filename: 可选，如果提供则保存到文件
        box_size: 二维码方块大小
        border: 边框大小

    Returns:
        ImageReader对象，可直接用于ReportLab的drawImage
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    if filename:
        img.save(filename)

    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return ImageReader(img_buffer)


async def generate_print_id() -> str:
    """
    生成打印单号 MES+YYMMDD+0000001
    使用MongoDB原子操作确保并发场景下的唯一性
    """
    try:
        today = datetime.now().strftime("%y%m%d")
        prefix = f"MES{today}"

        counter_collection = await get_collection_handler("print_counters")

        result = await counter_collection.find_one_and_update(
            {
                "prefix": "MES",
                "date": today
            },
            {
                "$inc": {"sequence": 1},
                "$setOnInsert": {"created_at": datetime.now()}
            },
            upsert=True,
            return_document=True
        )

        sequence = str(result["sequence"]).zfill(7)
        new_order_id = f"{prefix}{sequence}"

        return new_order_id

    except Exception as e:
        log_exception(e, '生成打印单号失败')
        raise Exception("生成打印单号失败")


async def generate_finish_tag_id() -> str:
    """
    生成成品码时间序列号 YYMMDDHHMMSS+001
    """
    try:
        now_time = datetime.now().strftime('%y%m%d%H%M%S')
        prefix = f"{now_time}"

        counter_collection = await get_collection_handler("print_counters")

        result = await counter_collection.find_one_and_update(
            {
                "prefix": "",
                "date": now_time
            },
            {
                "$inc": {"sequence": 1},
                "$setOnInsert": {"created_at": datetime.now()}
            },
            upsert=True,
            return_document=True
        )

        sequence = str(result["sequence"]).zfill(3)
        new_serial_id = f"{prefix}{sequence}"

        one_day_ago = datetime.now() - timedelta(days=1)
        await counter_collection.delete_many({
            "prefix": "",
            "created_at": {"$lt": one_day_ago}
        })

        return new_serial_id

    except Exception as e:
        log_exception(e, '生成打印序列号失败')
        raise Exception("生成打印序列号失败")


async def generate_other_serial_id() -> str:
    """
    生成其他码时间序列号 YYMMDD+000001
    """
    try:
        now_time = datetime.now().strftime('%y%m%d')
        prefix = f"{now_time}"

        counter_collection = await get_collection_handler("print_counters")

        result = await counter_collection.find_one_and_update(
            {
                "prefix": "",
                "date": now_time
            },
            {
                "$inc": {"sequence": 1},
                "$setOnInsert": {"created_at": datetime.now()}
            },
            upsert=True,
            return_document=True
        )

        sequence = str(result["sequence"]).zfill(6)
        new_serial_id = f"{prefix}{sequence}"

        one_day_ago = datetime.now() - timedelta(days=1)
        await counter_collection.delete_many({
            "prefix": "",
            "created_at": {"lt": one_day_ago}
        })

        return new_serial_id

    except Exception as e:
        log_exception(e, '生成打印序列号失败')
        raise Exception("生成打印序列号失败")
