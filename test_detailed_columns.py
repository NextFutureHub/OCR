#!/usr/bin/env python3
"""
Детальный тест для проверки определения столбцов
"""

import requests
import json
from PIL import Image, ImageDraw, ImageFont
import io

def create_detailed_test_image():
    """Создает детальное тестовое изображение с четко разделенными столбцами"""
    # Создаем большое изображение
    img = Image.new('RGB', (1200, 800), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    # Левый столбец (русский) - четко слева
    russian_text = [
        "РАМОЧНЫЙ ДОГОВОР",
        "№ IC-45-2022",
        "От 1 Сентября 2022 г.",
        "Москва",
        "",
        "COREX LOGISTICS LIMITED",
        "Юридическое лицо",
        "зарегистрированное в Ирландии",
        "регистрационный номер 540725",
        "Адрес: Дублин 8",
        "Представлен Директором",
        "Андреем Таракановым",
        "именуемое в дальнейшем",
        "«ИСПОЛНИТЕЛЬ»"
    ]
    
    # Правый столбец (английский) - четко справа
    english_text = [
        "MASTER AGREEMENT",
        "No. IC-45-2022",
        "Dated September 01, 2022",
        "Moscow",
        "",
        "COREX LOGISTICS LIMITED",
        "Legal entity",
        "registered in Ireland",
        "registration number 540725",
        "Address: Dublin 8",
        "Represented by Director",
        "Andrey Tarakanov",
        "hereinafter referred to as",
        "\"CONTRACTOR\""
    ]
    
    # Рисуем левый столбец (левая половина)
    y_pos = 50
    for line in russian_text:
        draw.text((50, y_pos), line, fill='black', font=font)
        y_pos += 30
    
    # Рисуем правый столбец (правая половина)
    y_pos = 50
    for line in english_text:
        draw.text((650, y_pos), line, fill='black', font=font)
        y_pos += 30
    
    # Добавляем разделительную линию
    draw.line([(600, 0), (600, 800)], fill='gray', width=2)
    
    # Сохраняем в байты
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def test_detailed_ocr():
    """Детальное тестирование OCR"""
    print("🔍 Детальное тестирование OCR с анализом столбцов...")
    
    # Создаем тестовое изображение
    image_data = create_detailed_test_image()
    
    # Сохраняем изображение для просмотра
    with open('test_columns_image.png', 'wb') as f:
        f.write(image_data)
    print("💾 Тестовое изображение сохранено как 'test_columns_image.png'")
    
    # Отправляем на API
    files = {'file': ('test_columns.png', image_data, 'image/png')}
    
    try:
        response = requests.post('http://127.0.0.1:8000/ocr/process', files=files)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ OCR обработка успешна!")
            print(f"📄 Извлеченный текст: {len(result['extracted_text'])} символов")
            print(f"📊 Столбцов обнаружено: {result.get('columns_count', 0)}")
            print(f"📑 Страниц: {result.get('total_pages', 1)}")
            print(f"🌐 Многоязычный документ: {result.get('has_multiple_columns', False)}")
            
            print(f"\n📝 Полный текст:")
            print(result['extracted_text'])
            
            if result.get('columns'):
                print(f"\n📋 Детальный анализ столбцов:")
                for i, column in enumerate(result['columns']):
                    print(f"  Столбец {i+1} ({column['side']}):")
                    print(f"    Язык: {column['language']}")
                    print(f"    Элементов: {column['items_count']}")
                    print(f"    Уверенность: {column['confidence_avg']:.2f}")
                    print(f"    Текст: {column['text']}")
                    print()
            else:
                print("⚠️  Столбцы не обнаружены")
            
            return True
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🔬 Детальное тестирование определения столбцов")
    print("=" * 50)
    
    test_detailed_ocr()
