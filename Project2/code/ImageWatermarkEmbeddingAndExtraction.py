import numpy as np
from PIL import Image, ImageEnhance
import random
import os


def lsb_encoder(copyright_image_path, original_image_path):
    # 将图片嵌入水印

    # 打开水印图片，需要嵌入水印的原始图片
    copyright_image = Image.open(copyright_image_path).convert("L")  # 转换为灰度图像
    original_image = Image.open(original_image_path).convert("RGB")

    # 调整水印图片尺寸与原始图片一致
    copyright_image = copyright_image.resize(original_image.size)

    # 将PIL图转换为NumPy数组
    original_array = np.array(original_image, dtype=np.uint8)
    copyright_array = np.array(copyright_image, dtype=np.uint8)

    # 创建水印图的副本
    watermark = original_array.copy()

    # 将copyright二值化 (0或1)
    copyright_binary = np.where(copyright_array < 128, 1, 0)

    # 将watermark的R通道的最后1bit置零
    watermark_r = watermark[:, :, 0]
    watermark_r = (watermark_r // 2) * 2  # 清除最低位

    # 确保尺寸完全一致
    assert watermark_r.shape == copyright_binary.shape, "尺寸不匹配"

    # 添加水印信息到R通道的最后1bit
    watermark_r = watermark_r + copyright_binary

    # 确保值在0-255范围内并转换回uint8
    watermark_r = np.clip(watermark_r, 0, 255).astype(np.uint8)

    # 更新水印图的R通道
    watermark[:, :, 0] = watermark_r

    # 转换回PIL图像
    watermarked_image = Image.fromarray(watermark)

    return watermarked_image


def lsb_decoder(watermarked_image_path):

    # 图片水印提取

    watermarked_image = Image.open(watermarked_image_path).convert("RGB")
    watermarked_array = np.array(watermarked_image)

    # 提取R通道的最后1bit
    extracted = (watermarked_array[:, :, 0] % 2) * 255

    # 转换为二值图像
    extracted_image = Image.fromarray(extracted.astype(np.uint8))

    return extracted_image


if __name__ == "__main__":
    # 嵌入水印
    watermarked_img = lsb_encoder("Copyright_Image.png", "Original_Image.png")
    watermarked_img.save("Watermarked_Result.png")
    watermarked_img.show()

    # 提取水印
    extracted_img = lsb_decoder("Watermarked_Result.png")
    extracted_img.save("Extracted_Watermark.png")
    extracted_img.show()