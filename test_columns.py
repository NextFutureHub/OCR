#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности столбцов и страниц
"""

import requests
import json
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_image_with_columns():
    """Создает тестовое изображение с двумя столбцами (русский и английский)"""
    # Создаем изображение
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        # Пытаемся использовать системный шрифт
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    # Левый столбец (русский)
    russian_text = [
        "РАМОЧНЫЙ ДОГОВОР № IC-45-2022",
        "От 1 Сентября 2022 г., Москва",
        "",
        "COREX LOGISTICS LIMITED",
        "Юридическое лицо, зарегистрированное",
        "в Ирландии (регистрационный номер 540725)",
        "Адрес: Дублин 8",
        "Представлен Директором Андреем Таракановым",
        "именуемое в дальнейшем «ИСПОЛНИТЕЛЬ»"
    ]
    
    # Правый столбец (английский)
    english_text = [
        "MASTER AGREEMENT No. IC-45-2022",
        "Dated September 01, 2022, Moscow",
        "",
        "COREX LOGISTICS LIMITED",
        "Legal entity registered in Ireland",
        "(registration number 540725)",
        "Address: Dublin 8",
        "Represented by Director Andrey Tarakanov",
        "hereinafter referred to as \"CONTRACTOR\""
    ]
    
    # Рисуем левый столбец
    y_pos = 50
    for line in russian_text:
        draw.text((50, y_pos), line, fill='black', font=font)
        y_pos += 25
    
    # Рисуем правый столбец
    y_pos = 50
    for line in english_text:
        draw.text((450, y_pos), line, fill='black', font=font)
        y_pos += 25
    
    # Сохраняем в байты
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def test_ocr_with_columns():
    """Тестирует OCR с анализом столбцов"""
    print("🧪 Тестирование OCR с анализом столбцов...")
    
    # Создаем тестовое изображение
    image_data = create_test_image_with_columns()
    
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
            
            if result.get('columns'):
                print("\n📋 Анализ столбцов:")
                for i, column in enumerate(result['columns']):
                    print(f"  Столбец {i+1} ({column['side']}):")
                    print(f"    Язык: {column['language']}")
                    print(f"    Элементов: {column['items_count']}")
                    print(f"    Уверенность: {column['confidence_avg']:.2f}")
                    print(f"    Текст: {column['text'][:100]}...")
                    print()
            
            if result.get('pages'):
                print(f"\n📄 Анализ страниц ({len(result['pages'])} страниц):")
                for page in result['pages']:
                    print(f"  Страница {page['page_number']}:")
                    print(f"    Столбцов: {page['columns_count']}")
                    print(f"    Многоязычная: {page['has_multiple_columns']}")
                    print(f"    Текст: {page['text'][:100]}...")
                    print()
            
            return True
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_health():
    """Тестирует состояние API"""
    print("🏥 Проверка состояния API...")
    
    try:
        response = requests.get('http://127.0.0.1:8000/health')
        if response.status_code == 200:
            print("✅ API работает корректно")
            return True
        else:
            print(f"❌ API недоступен: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к API: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестов OCR с поддержкой столбцов и страниц")
    print("=" * 60)
    
    # Проверяем API
    if not test_health():
        print("❌ API недоступен, завершаем тестирование")
        exit(1)
    
    print()
    
    # Тестируем OCR с столбцами
    if test_ocr_with_columns():
        print("🎉 Все тесты пройдены успешно!")
    else:
        print("❌ Тесты не пройдены")
        exit(1)
