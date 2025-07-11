from PIL import Image, ImageEnhance
import numpy as np
import random
import matplotlib.pyplot as plt

# 辅助函数
def jpeg_compress(img, quality=90):
    # JPEG压缩模拟
    img.save("temp.jpg", quality=quality)
    return Image.open("temp.jpg")

def add_gaussian_noise(img, intensity=0.05):
    # 添加高斯噪声
    arr = np.array(img)
    noise = np.random.normal(0, intensity*255, arr.shape)
    return Image.fromarray(np.clip(arr + noise, 0, 255).astype(np.uint8))

def evaluate_extraction(extracted_wm):
    # 评估水印提取成功率
    wm_array = np.array(extracted_wm)
    if wm_array.size == 0:
        return 0.0
    # 假设理想水印应有50%黑色像素(根据实际情况调整)
    expected_ratio = 0.5
    actual_ratio = np.mean(wm_array < 128)
    return 1 - abs(actual_ratio - expected_ratio)/expected_ratio

def lsb_decoder(img):
    # 从PIL图像提取LSB水印
    if isinstance(img, str):
        img = Image.open(img)
    arr = np.array(img.convert("RGB"))
    extracted = (arr[:,:,0] % 2) * 255
    return Image.fromarray(extracted.astype(np.uint8))


def single_image_robustness_test(watermarked_img_path):
    # 单图像鲁棒性测试

    # 加载含水印图像
    watermarked_img = Image.open(watermarked_img_path)
    
    # 定义测试用例
    test_cases = [
        {"name": "Rotate 15 degrees", "func": lambda img: img.rotate(15, expand=True, fillcolor='white')},
        {"name": "Flip horizontally", "func": lambda img: img.transpose(Image.FLIP_LEFT_RIGHT)},
        {"name": "Crop 10%", "func": lambda img: img.crop((
            int(img.width * 0.1),
            int(img.height * 0.1),
            int(img.width * 0.9),
            int(img.height * 0.9)))},
        {"name": "JPEG Compression(50)", "func": lambda img: jpeg_compress(img, quality=50)},
        {"name": "Gaussian noise", "func": lambda img: add_gaussian_noise(img, intensity=0.05)},
        {"name": "The contrast ratio is enhanced by 1.5x", "func": lambda img: ImageEnhance.Contrast(img).enhance(1.5)}
    ]
    
    # 执行测试
    results = []
    for case in test_cases:
        print(f"\nPerform the test: {case['name']}")
        
        # 应用攻击
        attacked_img = case['func'](watermarked_img.copy())
        
        # 提取水印
        extracted_wm = lsb_decoder(attacked_img)
        
        # 评估并显示结果
        success_rate = evaluate_extraction(extracted_wm)
        results.append((case['name'], success_rate))
        
        # 可视化
        plt.figure(figsize=(12,4))
        plt.subplot(131), plt.imshow(watermarked_img), plt.title("Original watermarked image")
        plt.subplot(132), plt.imshow(attacked_img), plt.title(f"Type of attack: {case['name']}")
        plt.subplot(133), plt.imshow(extracted_wm, cmap='gray'), plt.title(f"Extract watermarks (success rate:{success_rate:.1%})")
        plt.show()
    
    # 打印汇总结果
    print("\n=== Summary of test results ===")
    for name, rate in results:
        print(f"{name:<15}: Watermark extraction success rate {rate:.1%}")


if __name__ == "__main__":
    single_image_robustness_test("Watermarked_Result.png")
