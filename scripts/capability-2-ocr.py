#!/usr/bin/env python3
"""
能力 2: PDF/图片解析测试
测试 PyMuPDF、Tesseract OCR、百炼视觉模型
"""
import os
import sys
import base64
import io
import tempfile

def test_pymupdf_text_extract():
    """测试 2.1: PyMuPDF 纯文本 PDF 提取"""
    print("📄 测试 PyMuPDF 纯文本提取...")
    try:
        import fitz
        # Create a simple PDF for testing
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "这是一段测试文本。\nTest text for PyMuPDF extraction.", fontsize=12)
        test_pdf = "/tmp/test-pymupdf.pdf"
        doc.save(test_pdf)
        doc.close()
        
        # Re-open and extract
        doc = fitz.open(test_pdf)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        
        print(f"  提取文本: {text[:100]}...")
        assert "测试文本" in text or "Test text" in text
        print("  ✅ PyMuPDF 纯文本提取通过")
        return True
    except Exception as e:
        print(f"  ❌ PyMuPDF 失败: {e}")
        return False

def test_tesseract_ocr():
    """测试 2.2: Tesseract OCR"""
    print("\n🔍 测试 Tesseract OCR...")
    try:
        import pytesseract
        from pdf2image import convert_from_path
        import fitz
        
        # Create a PDF with text (as image)
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "OCR Test Text 你好世界", fontsize=24)
        test_pdf = "/tmp/test-ocr.pdf"
        doc.save(test_pdf)
        doc.close()
        
        # Convert PDF to image
        images = convert_from_path(test_pdf, dpi=150)
        if images:
            # Run OCR
            text = pytesseract.image_to_string(images[0], lang='eng+chi_sim')
            print(f"  OCR 识别结果: {text.strip()[:100]}")
            print("  ✅ Tesseract OCR 通过")
            return True
        else:
            print("  ⚠️ 无法转换 PDF 为图片")
            return False
    except Exception as e:
        print(f"  ❌ Tesseract OCR 失败: {e}")
        return False

def test_bailian_vision_ocr():
    """测试 2.3: 百炼视觉模型 OCR"""
    print("\n🤖 测试百炼视觉模型 OCR...")
    try:
        import requests
        import fitz
        
        # Create a test PDF with Chinese text
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "百炼视觉模型测试：这是一段中文测试文本。\n包含多行内容。", fontsize=16)
        test_pdf = "/tmp/test-bailian.pdf"
        doc.save(test_pdf)
        doc.close()
        
        # Convert first page to PNG
        doc = fitz.open(test_pdf)
        page = doc[0]
        pix = page.get_pixmap(dpi=150)
        img_path = "/tmp/test-bailian.png"
        pix.save(img_path)
        doc.close()
        
        # Read image as base64
        with open(img_path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # Call Bailian API
        api_key = "sk-sp-a68df77f47f04e1ca871300f7afa41f1"
        url = "https://coding.dashscope.aliyuncs.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "kimi-k2.5",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "请读取这张图片中的所有中文文字。"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                ]
            }],
            "max_tokens": 500
        }
        
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            text = result["choices"][0]["message"]["content"]
            print(f"  百炼 OCR 结果: {text[:100]}")
            print("  ✅ 百炼视觉模型 OCR 通过")
            return True
        else:
            print(f"  ❌ API 错误: {resp.status_code} - {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"  ❌ 百炼视觉模型失败: {e}")
        return False

def test_pdf2image():
    """测试 2.4: PDF 转图片"""
    print("\n🖼️ 测试 PDF 转图片...")
    try:
        from pdf2image import convert_from_path
        import fitz
        
        # Create test PDF
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Test PDF for image conversion", fontsize=16)
        test_pdf = "/tmp/test-pdf2image.pdf"
        doc.save(test_pdf)
        doc.close()
        
        images = convert_from_path(test_pdf, dpi=150)
        if images:
            img_path = "/tmp/test-pdf2image.png"
            images[0].save(img_path, "PNG")
            size = os.path.getsize(img_path)
            print(f"  图片大小: {size:,} bytes")
            print("  ✅ PDF 转图片通过")
            return True
        else:
            print("  ❌ 转换失败")
            return False
    except Exception as e:
        print(f"  ❌ PDF 转图片失败: {e}")
        return False

def main():
    print("=" * 50)
    print("能力 2: PDF/图片解析测试")
    print("=" * 50)
    
    results = {}
    results["test_2_1_pymupdf"] = "✅ 通过" if test_pymupdf_text_extract() else "❌ 失败"
    results["test_2_2_tesseract"] = "✅ 通过" if test_tesseract_ocr() else "❌ 失败"
    results["test_2_3_bailian"] = "✅ 通过" if test_bailian_vision_ocr() else "❌ 失败"
    results["test_2_4_pdf2image"] = "✅ 通过" if test_pdf2image() else "❌ 失败"
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    for k, v in results.items():
        print(f"  {k}: {v}")
    passed = sum(1 for v in results.values() if "✅" in v)
    print(f"  通过率: {passed}/{len(results)}")
    print("=" * 50)
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
