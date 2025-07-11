from PIL import Image, ImageEnhance
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 辅助函数
def evaluate_extraction(extracted_wm):
    # 评估水印提取成功率（假设理想水印黑白像素各占50%）
    wm_array = np.array(extracted_wm)
    if wm_array.size == 0:
        return 0.0
    expected_ratio = 0.5  # 理想黑白比例
    actual_ratio = np.mean(wm_array < 128)  # 实际黑色像素比例
    return 1 - abs(actual_ratio - expected_ratio) / expected_ratio


def lsb_decoder(img):
    # 从图像提取LSB水印（读取R通道最低有效位）
    arr = np.array(img.convert("RGB"))
    extracted = (arr[:, :, 0] % 2) * 255  # 提取R通道LSB，转为黑白图像
    return Image.fromarray(extracted.astype(np.uint8))


def translate_image(img, dx=0, dy=0):
    # 平移图像（dx：水平偏移，dy：垂直偏移，空白填充白色）
    width, height = img.size
    translated = Image.new("RGB", (width, height), color="white")
    translated.paste(img, (dx, dy))  # 偏移粘贴原图
    return translated


def robustness_test(watermarked_img_path):
    # 加载含水印图像
    watermarked_img = Image.open(watermarked_img_path)

    # 进行鲁棒性测试，包括翻转、平移、截取、调对比度
    test_cases = [
        {"name": "水平翻转", "func": lambda img: img.transpose(Image.FLIP_LEFT_RIGHT)},
        {"name": "垂直翻转", "func": lambda img: img.transpose(Image.FLIP_TOP_BOTTOM)},
        {"name": "平移(右移50，下移30)", "func": lambda img: translate_image(img, dx=50, dy=30)},
        {"name": "截取中心50%区域", "func": lambda img: img.crop((
            int(img.width * 0.25),
            int(img.height * 0.25),
            int(img.width * 0.75),
            int(img.height * 0.75)))},  # 保留中心50%
        {"name": "对比度增强1.5倍", "func": lambda img: ImageEnhance.Contrast(img).enhance(1.5)},
        {"name": "对比度减弱0.5倍", "func": lambda img: ImageEnhance.Contrast(img).enhance(0.5)}
    ]

    # 执行测试
    results = []
    for case in test_cases:
        print(f"执行测试：{case['name']}")

        # 应用攻击
        attacked_img = case['func'](watermarked_img.copy())

        # 提取水印
        extracted_wm = lsb_decoder(attacked_img)

        # 评估成功率
        success_rate = evaluate_extraction(extracted_wm)
        results.append((case['name'], success_rate))

        # 可视化结果
        plt.figure(figsize=(12, 4))
        plt.subplot(131), plt.imshow(watermarked_img), plt.title("原始含水印图像")
        plt.subplot(132), plt.imshow(attacked_img), plt.title(f"攻击类型：{case['name']}")
        plt.subplot(133), plt.imshow(extracted_wm, cmap='gray'), plt.title(f"提取的水印（成功率：{success_rate:.1%}）")
        plt.show()

    # 汇总结果
    print("\n=== 测试结果汇总 ===")
    for name, rate in results:
        print(f"{name:<15}：水印提取成功率 {rate:.1%}")


if __name__ == "__main__":
    robustness_test("Watermarked_Result.png")  # 替换为你的含水印图像路径