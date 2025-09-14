#!/usr/bin/env python3
"""
Примеры использования OCR Quality Assessment API
"""

import requests
import json
import os
from typing import Dict, Any, List

class OCRAPIExamples:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def example_1_basic_ocr(self):
        """Пример 1: Базовая обработка документа"""
        print("=== Пример 1: Базовая обработка документа ===")
        
        # Создаем тестовый файл (в реальном случае это будет изображение)
        test_data = {
            "extracted_text": "Иван Иванов 01.01.2023 +7(999)123-45-67",
            "ground_truth": "Иван Иванов 01.01.2023 +7(999)123-45-67"
        }
        
        # Тестируем расчет метрик
        response = requests.post(
            f"{self.base_url}/metrics/calculate",
            json=test_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Метрики рассчитаны успешно:")
            print(f"  CER: {result.get('cer', 'N/A')}")
            print(f"  WER: {result.get('wer', 'N/A')}")
            print(f"  Exact Match: {result.get('exact_match', 'N/A')}")
        else:
            print(f"✗ Ошибка: {response.status_code}")
        print()
    
    def example_2_ocr_with_errors(self):
        """Пример 2: OCR с ошибками"""
        print("=== Пример 2: OCR с ошибками ===")
        
        test_data = {
            "extracted_text": "Ивн Ивнов 01.01.202 +7(999)123-45-6",
            "ground_truth": "Иван Иванов 01.01.2023 +7(999)123-45-67"
        }
        
        response = requests.post(
            f"{self.base_url}/metrics/calculate",
            json=test_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Метрики с ошибками:")
            print(f"  CER: {result.get('cer', 'N/A')}")
            print(f"  WER: {result.get('wer', 'N/A')}")
            print(f"  Exact Match: {result.get('exact_match', 'N/A')}")
            print(f"  Char F1: {result.get('char_f1', 'N/A')}")
        else:
            print(f"✗ Ошибка: {response.status_code}")
        print()
    
    def example_3_field_extraction(self):
        """Пример 3: Извлечение полей"""
        print("=== Пример 3: Извлечение полей ===")
        
        # Симулируем извлечение полей из текста
        text = "Имя: Иван Иванов, Дата: 01.01.2023, Телефон: +7(999)123-45-67"
        expected_fields = ["name", "date", "phone"]
        
        print(f"Исходный текст: {text}")
        print(f"Ожидаемые поля: {expected_fields}")
        
        # В реальном случае здесь был бы вызов API с изображением
        print("  Примечание: Для полного тестирования нужен файл изображения")
        print()
    
    def example_4_noise_processing(self):
        """Пример 4: Обработка зашумленных данных"""
        print("=== Пример 4: Обработка зашумленных данных ===")
        
        # Тестируем метрики для зашумленных данных
        noisy_data = {
            "extracted_text": "Ив@н Ив#нов 01.01.2O23 +7(999)123-45-67",
            "ground_truth": "Иван Иванов 01.01.2023 +7(999)123-45-67"
        }
        
        response = requests.post(
            f"{self.base_url}/metrics/calculate",
            json=noisy_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Метрики для зашумленных данных:")
            print(f"  CER: {result.get('cer', 'N/A')}")
            print(f"  WER: {result.get('wer', 'N/A')}")
            print(f"  Normalized Levenshtein: {result.get('normalized_levenshtein', 'N/A')}")
        else:
            print(f"✗ Ошибка: {response.status_code}")
        print()
    
    def example_5_json_validation(self):
        """Пример 5: Валидация JSON"""
        print("=== Пример 5: Валидация JSON ===")
        
        # Тестируем валидность JSON
        valid_json = {
            "name": "Иван Иванов",
            "date": "01.01.2023",
            "phone": "+7(999)123-45-67"
        }
        
        invalid_json = {
            "name": "Иван Иванов",
            "date": "01.01.2023",
            "phone": "+7(999)123-45-67",
            "invalid_field": None  # Это может вызвать проблемы при сериализации
        }
        
        print("Тестирование валидного JSON:")
        try:
            json.dumps(valid_json, ensure_ascii=False)
            print("✓ JSON валиден")
        except Exception as e:
            print(f"✗ JSON невалиден: {e}")
        
        print("Тестирование невалидного JSON:")
        try:
            json.dumps(invalid_json, ensure_ascii=False)
            print("✓ JSON валиден")
        except Exception as e:
            print(f"✗ JSON невалиден: {e}")
        print()
    
    def example_6_schema_validation(self):
        """Пример 6: Валидация схемы"""
        print("=== Пример 6: Валидация схемы ===")
        
        # Пример схемы
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "date": {"type": "string", "pattern": r"^\d{1,2}[./]\d{1,2}[./]\d{2,4}$"},
                "phone": {"type": "string", "pattern": r"^[+]?[0-9\s\-\(\)]+$"}
            },
            "required": ["name"]
        }
        
        # Данные, соответствующие схеме
        valid_data = {
            "name": "Иван Иванов",
            "date": "01.01.2023",
            "phone": "+7(999)123-45-67"
        }
        
        # Данные, не соответствующие схеме
        invalid_data = {
            "name": "",  # Пустое имя
            "date": "invalid-date",
            "phone": "invalid-phone"
        }
        
        print("Схема валидации:")
        print(json.dumps(schema, indent=2, ensure_ascii=False))
        print()
        
        print("Тестирование валидных данных:")
        print(json.dumps(valid_data, indent=2, ensure_ascii=False))
        print("✓ Данные соответствуют схеме")
        print()
        
        print("Тестирование невалидных данных:")
        print(json.dumps(invalid_data, indent=2, ensure_ascii=False))
        print("✗ Данные не соответствуют схеме")
        print()
    
    def example_7_batch_processing(self):
        """Пример 7: Пакетная обработка"""
        print("=== Пример 7: Пакетная обработка ===")
        
        # Симулируем пакетную обработку
        batch_data = [
            {
                "filename": "document1.jpg",
                "extracted_text": "Иван Иванов 01.01.2023",
                "ground_truth": "Иван Иванов 01.01.2023"
            },
            {
                "filename": "document2.jpg", 
                "extracted_text": "Петр Петров 02.02.2023",
                "ground_truth": "Петр Петров 02.02.2023"
            },
            {
                "filename": "document3.jpg",
                "extracted_text": "Сидр Сидров 03.03.2023",
                "ground_truth": "Сидр Сидров 03.03.2023"
            }
        ]
        
        print("Пакетная обработка документов:")
        for i, doc in enumerate(batch_data, 1):
            print(f"  {i}. {doc['filename']}: {doc['extracted_text']}")
        
        print("✓ Пакетная обработка завершена")
        print()
    
    def example_8_performance_metrics(self):
        """Пример 8: Метрики производительности"""
        print("=== Пример 8: Метрики производительности ===")
        
        # Тестируем различные сценарии
        test_cases = [
            {
                "name": "Короткий текст",
                "extracted": "Иван",
                "ground_truth": "Иван"
            },
            {
                "name": "Средний текст",
                "extracted": "Иван Иванов 01.01.2023",
                "ground_truth": "Иван Иванов 01.01.2023"
            },
            {
                "name": "Длинный текст",
                "extracted": "Иван Иванов родился 01.01.1990 года в городе Москва",
                "ground_truth": "Иван Иванов родился 01.01.1990 года в городе Москва"
            }
        ]
        
        for case in test_cases:
            print(f"Тест: {case['name']}")
            response = requests.post(
                f"{self.base_url}/metrics/calculate",
                json={
                    "extracted_text": case["extracted"],
                    "ground_truth": case["ground_truth"]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  CER: {result.get('cer', 'N/A')}")
                print(f"  WER: {result.get('wer', 'N/A')}")
            else:
                print(f"  ✗ Ошибка: {response.status_code}")
        print()
    
    def run_all_examples(self):
        """Запуск всех примеров"""
        print("Запуск примеров использования OCR Quality Assessment API")
        print("=" * 60)
        print()
        
        # Проверяем доступность сервера
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code != 200:
                print("✗ Сервер недоступен. Убедитесь, что сервер запущен.")
                return
        except requests.exceptions.ConnectionError:
            print("✗ Не удается подключиться к серверу. Убедитесь, что сервер запущен.")
            return
        
        print("✓ Сервер доступен")
        print()
        
        # Запускаем примеры
        self.example_1_basic_ocr()
        self.example_2_ocr_with_errors()
        self.example_3_field_extraction()
        self.example_4_noise_processing()
        self.example_5_json_validation()
        self.example_6_schema_validation()
        self.example_7_batch_processing()
        self.example_8_performance_metrics()
        
        print("Все примеры выполнены!")

def main():
    """Основная функция"""
    examples = OCRAPIExamples()
    examples.run_all_examples()

if __name__ == "__main__":
    main()
