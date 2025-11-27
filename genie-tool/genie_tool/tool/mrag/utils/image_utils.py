"""
图像处理工具模块

该模块提供图像处理相关的工具函数：
- 图像预处理
- 图像格式转换
- 图像质量评估
- OCR辅助工具

主要功能：
1. 图像尺寸调整和裁剪
2. 图像格式标准化转换
3. 图像质量检测和评估
4. 图像噪声去除和增强
5. OCR前预处理优化
6. 批量图像处理工具
"""
from PIL import Image


def image_path_to_base64(image_path: str) -> str:
    import base64
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def image_to_base64(image: Image.Image) -> str:
    import base64
    import io
    image = image.convert("RGB")
    with io.BytesIO() as buffer:
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")


def resize_image(
        pil_image: Image.Image, max_size: int = 512, make_square=False,
        fill_color=(255, 255, 255)
) -> Image.Image:
    """
    调整PIL图片大小，长边缩放到指定阈值，短边等比缩放

    Args:
        pil_image (PIL.Image): PIL图片对象
        max_size (int): 长边的最大尺寸阈值，默认512
        make_square (bool): 是否用白边填补成正方形，默认False
        fill_color (tuple): 填充颜色，默认白色(255, 255, 255)

    Returns:
        PIL.Image: 处理后的图片对象
    """
    pil_image = pil_image.convert("RGB")
    if not isinstance(pil_image, Image.Image):
        raise ValueError("输入必须是PIL.Image对象")

    # 获取原始尺寸
    original_width, original_height = pil_image.size

    if original_width < max_size and original_height < max_size:
        return pil_image

    # 计算缩放比例（以长边为准）
    max_dimension = max(original_width, original_height)
    if max_dimension > max_size:
        scale_ratio = max_size / max_dimension
        new_width = int(original_width * scale_ratio)
        new_height = int(original_height * scale_ratio)
    else:
        new_width = original_width
        new_height = original_height

    # 等比缩放
    resized_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # 如果需要填补成正方形
    if make_square:
        # 创建正方形画布（以长边为准）
        square_size = max(new_width, new_height)

        # 处理不同的图片模式
        if pil_image.mode in ("RGBA", "LA"):
            # 对于有透明通道的图片，创建RGBA画布
            square_image = Image.new(
                "RGBA", (square_size, square_size), fill_color + (255,)
            )
        else:
            # 对于普通图片，创建RGB画布
            square_image = Image.new("RGB", (square_size, square_size), fill_color)

        # 计算居中位置
        x_offset = (square_size - new_width) // 2
        y_offset = (square_size - new_height) // 2

        # 将缩放后的图片粘贴到正方形画布中央
        if resized_image.mode == "RGBA":
            square_image.paste(resized_image, (x_offset, y_offset), resized_image)
        else:
            square_image.paste(resized_image, (x_offset, y_offset))

        print(f"最终尺寸: {square_size} x {square_size} (正方形)")
        return square_image

    return resized_image


def resize_local_image(local_path, resize):
    image = Image.open(local_path)
    image = resize_image(image, resize)
    image.save(local_path)
