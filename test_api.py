import requests
import json
import os
from typing import Dict, Any

class OCRAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def test_health(self) -> bool:
        """Тест проверки состояния сервиса"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            print(f"Ошибка при проверке здоровья сервиса: {e}")
            return False
    
    def test_ocr_process(self, image_path: str, ground_truth: str = None) -> Dict[str, Any]:
        """Тест обработки документа"""
        try:
            if not os.path.exists(image_path):
                print(f"Файл {image_path} не найден")
                return {}
            
            with open(image_path, 'rb') as f:
                files = {'file': f}
                data = {}
                if ground_truth:
                    data['ground_truth'] = ground_truth
                
                response = requests.post(f"{self.base_url}/ocr/process", files=files, data=data)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Ошибка API: {response.status_code} - {response.text}")
                    return {}
                    
        except Exception as e:
            print(f"Ошибка при тестировании OCR: {e}")
            return {}
    
    def test_metrics_calculation(self, extracted_text: str, ground_truth: str) -> Dict[str, Any]:
        """Тест расчета метрик"""
        try:
            data = {
                'extracted_text': extracted_text,
                'ground_truth': ground_truth
            }
            
            response = requests.post(f"{self.base_url}/metrics/calculate", json=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Ошибка API: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            print(f"Ошибка при тестировании метрик: {e}")
            return {}
    
    def test_noise_processing(self, image_path: str, ground_truth: str = None) -> Dict[str, Any]:
        """Тест обработки зашумленного документа"""
        try:
            if not os.path.exists(image_path):
                print(f"Файл {image_path} не найден")
                return {}
            
            with open(image_path, 'rb') as f:
                files = {'file': f}
                data = {}
                if ground_truth:
                    data['ground_truth'] = ground_truth
                
                response = requests.post(f"{self.base_url}/noise/process", files=files, data=data)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Ошибка API: {response.status_code} - {response.text}")
                    return {}
                    
        except Exception as e:
            print(f"Ошибка при тестировании обработки шума: {e}")
            return {}
    
    def run_comprehensive_test(self):
        """Запуск комплексного тестирования"""
        print("=== Тестирование OCR Quality Assessment API ===\n")
        
        # 1. Тест здоровья сервиса
        print("1. Проверка состояния сервиса...")
        if self.test_health():
            print("✓ Сервис работает корректно\n")
        else:
            print("✗ Сервис недоступен\n")
            return
        
        # 2. Тест расчета метрик
        print("2. Тестирование расчета метрик...")
        extracted_text = "Иван Иванов 01.01.2023"
        ground_truth = "Иван Иванов 01.01.2023"
        
        metrics = self.test_metrics_calculation(extracted_text, ground_truth)
        if metrics:
            print("✓ Метрики рассчитаны успешно:")
            print(f"  CER: {metrics.get('cer', 'N/A')}")
            print(f"  WER: {metrics.get('wer', 'N/A')}")
            print(f"  Normalized Levenshtein: {metrics.get('normalized_levenshtein', 'N/A')}")
            print(f"  Exact Match: {metrics.get('exact_match', 'N/A')}")
        else:
            print("✗ Ошибка при расчете метрик")
        print()
        
        # 3. Тест с ошибками в тексте
        print("3. Тестирование с ошибками в тексте...")
        extracted_text_with_errors = "Ивн Ивнов 01.01.202"
        ground_truth = "Иван Иванов 01.01.2023"
        
        metrics_with_errors = self.test_metrics_calculation(extracted_text_with_errors, ground_truth)
        if metrics_with_errors:
            print("✓ Метрики с ошибками рассчитаны:")
            print(f"  CER: {metrics_with_errors.get('cer', 'N/A')}")
            print(f"  WER: {metrics_with_errors.get('wer', 'N/A')}")
            print(f"  Exact Match: {metrics_with_errors.get('exact_match', 'N/A')}")
        else:
            print("✗ Ошибка при расчете метрик с ошибками")
        print()
        
        # 4. Тест извлечения полей
        print("4. Тестирование извлечения полей...")
        test_text = "Имя: Иван Иванов, Дата: 01.01.2023, Телефон: +7(999)123-45-67"
        expected_fields = ["name", "date", "phone"]
        
        # Создаем временный файл для тестирования
        test_image_path = "test_image.txt"
        with open(test_image_path, 'w', encoding='utf-8') as f:
            f.write(test_text)
        
        # Тест обработки (в реальном случае нужен файл изображения)
        print("  Примечание: Для полного тестирования нужны файлы изображений")
        print("  Создан тестовый файл для демонстрации")
        
        # Очистка
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        
        print("\n=== Тестирование завершено ===")

def create_sample_test_data():
    """Создание примеров тестовых данных"""
    print("Создание примеров тестовых данных...")
    
    # Примеры текстов для тестирования
    test_cases = [
        {
            "name": "Идеальное совпадение",
            "extracted": "Иван Иванов 01.01.2023",
            "ground_truth": "Иван Иванов 01.01.2023"
        },
        {
            "name": "Ошибки в символах",
            "extracted": "Ивн Ивнов 01.01.202",
            "ground_truth": "Иван Иванов 01.01.2023"
        },
        {
            "name": "Ошибки в словах",
            "extracted": "Иван Петров 01.01.2023",
            "ground_truth": "Иван Иванов 01.01.2023"
        },
        {
            "name": "Пропущенные слова",
            "extracted": "Иван 01.01.2023",
            "ground_truth": "Иван Иванов 01.01.2023"
        },
        {
            "name": "Лишние слова",
            "extracted": "Иван Иванов Петрович 01.01.2023",
            "ground_truth": "Иван Иванов 01.01.2023"
        }
    ]
    
    print("Примеры тестовых случаев:")
    for i, case in enumerate(test_cases, 1):
        print(f"{i}. {case['name']}")
        print(f"   Извлеченный: '{case['extracted']}'")
        print(f"   Эталонный:   '{case['ground_truth']}'")
        print()

if __name__ == "__main__":
    # Создание тестовых данных
    create_sample_test_data()
    
    # Запуск тестирования
    tester = OCRAPITester()
    tester.run_comprehensive_test()
