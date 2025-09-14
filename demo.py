#!/usr/bin/env python3
"""
Демонстрация работы OCR Quality Assessment API
"""

import requests
import json
import time
from typing import Dict, Any

class OCRDemo:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def demo_ocr_quality_assessment(self):
        """Демонстрация оценки качества OCR"""
        print("🔍 ДЕМОНСТРАЦИЯ ОЦЕНКИ КАЧЕСТВА OCR")
        print("=" * 50)
        
        # Тестовые случаи с разным качеством OCR
        test_cases = [
            {
                "name": "Идеальное качество",
                "extracted": "Иван Иванов 01.01.2023 +7(999)123-45-67",
                "ground_truth": "Иван Иванов 01.01.2023 +7(999)123-45-67",
                "expected_score": "100%"
            },
            {
                "name": "Хорошее качество",
                "extracted": "Иван Иванов 01.01.2023 +7(999)123-45-67",
                "ground_truth": "Иван Иванов 01.01.2023 +7(999)123-45-67",
                "expected_score": "95-99%"
            },
            {
                "name": "Среднее качество",
                "extracted": "Ивн Ивнов 01.01.202 +7(999)123-45-6",
                "ground_truth": "Иван Иванов 01.01.2023 +7(999)123-45-67",
                "expected_score": "70-85%"
            },
            {
                "name": "Плохое качество",
                "extracted": "Ив@н Ив#нов 01.01.2O23 +7(999)123-45-67",
                "ground_truth": "Иван Иванов 01.01.2023 +7(999)123-45-67",
                "expected_score": "50-70%"
            }
        ]
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n📄 Тест {i}: {case['name']}")
            print(f"   Ожидаемый балл: {case['expected_score']}")
            print(f"   Извлеченный текст: '{case['extracted']}'")
            print(f"   Эталонный текст:   '{case['ground_truth']}'")
            
            # Расчет метрик
            metrics = self._calculate_metrics(case['extracted'], case['ground_truth'])
            if metrics:
                self._display_metrics(metrics)
                score = self._calculate_overall_score(metrics)
                print(f"   🎯 Общий балл: {score:.1f}%")
            else:
                print("   ❌ Ошибка при расчете метрик")
    
    def demo_field_extraction(self):
        """Демонстрация извлечения полей"""
        print("\n\n📋 ДЕМОНСТРАЦИЯ ИЗВЛЕЧЕНИЯ ПОЛЕЙ")
        print("=" * 50)
        
        # Примеры документов
        documents = [
            {
                "name": "Паспорт",
                "text": "ФИО: Иванов Иван Иванович, Дата рождения: 01.01.1990, Паспорт: 1234 567890",
                "expected_fields": ["name", "date", "passport"]
            },
            {
                "name": "Договор",
                "text": "Заказчик: Петров Петр Петрович, Сумма: 100000 руб, Дата: 15.03.2023",
                "expected_fields": ["name", "amount", "date"]
            },
            {
                "name": "Контактная информация",
                "text": "Имя: Сидоров Сидор, Телефон: +7(999)123-45-67, Email: sidor@example.com",
                "expected_fields": ["name", "phone", "email"]
            }
        ]
        
        for doc in documents:
            print(f"\n📄 {doc['name']}:")
            print(f"   Текст: {doc['text']}")
            print(f"   Ожидаемые поля: {doc['expected_fields']}")
            
            # Симуляция извлечения полей
            extracted_fields = self._simulate_field_extraction(doc['text'], doc['expected_fields'])
            print(f"   Извлеченные поля: {extracted_fields}")
            
            # Расчет точности извлечения
            accuracy = self._calculate_field_accuracy(extracted_fields, doc['expected_fields'])
            print(f"   🎯 Точность извлечения: {accuracy:.1f}%")
    
    def demo_noise_handling(self):
        """Демонстрация обработки шума"""
        print("\n\n🔧 ДЕМОНСТРАЦИЯ ОБРАБОТКИ ШУМА")
        print("=" * 50)
        
        # Примеры зашумленных текстов
        noisy_texts = [
            {
                "name": "Солевой и перцовый шум",
                "original": "Иван Иванов 01.01.2023",
                "noisy": "Ив@н Ив#нов 01.01.2O23"
            },
            {
                "name": "Гауссов шум",
                "original": "Петр Петров 02.02.2023",
                "noisy": "Петр Петр0в 02.02.2023"
            },
            {
                "name": "Смешанный шум",
                "original": "Сидр Сидров 03.03.2023",
                "noisy": "Сидр С1др0в 03.03.2023"
            }
        ]
        
        for text_case in noisy_texts:
            print(f"\n📄 {text_case['name']}:")
            print(f"   Оригинал: '{text_case['original']}'")
            print(f"   Зашумленный: '{text_case['noisy']}'")
            
            # Расчет метрик для зашумленного текста
            metrics = self._calculate_metrics(text_case['noisy'], text_case['original'])
            if metrics:
                print(f"   📊 CER: {metrics.get('cer', 0):.3f}")
                print(f"   📊 WER: {metrics.get('wer', 0):.3f}")
                
                # Оценка качества восстановления
                recovery_score = (1 - metrics.get('cer', 1)) * 100
                print(f"   🎯 Качество восстановления: {recovery_score:.1f}%")
    
    def demo_json_validation(self):
        """Демонстрация валидации JSON"""
        print("\n\n✅ ДЕМОНСТРАЦИЯ ВАЛИДАЦИИ JSON")
        print("=" * 50)
        
        # Примеры JSON данных
        json_examples = [
            {
                "name": "Валидный JSON",
                "data": {
                    "name": "Иван Иванов",
                    "date": "01.01.2023",
                    "phone": "+7(999)123-45-67"
                },
                "valid": True
            },
            {
                "name": "JSON с отсутствующими полями",
                "data": {
                    "name": "Иван Иванов"
                    # Отсутствуют date и phone
                },
                "valid": True  # JSON валиден, но неполон
            },
            {
                "name": "JSON с неверными типами",
                "data": {
                    "name": 123,  # Должно быть строкой
                    "date": "01.01.2023",
                    "phone": "+7(999)123-45-67"
                },
                "valid": True  # JSON валиден синтаксически
            }
        ]
        
        for example in json_examples:
            print(f"\n📄 {example['name']}:")
            print(f"   Данные: {json.dumps(example['data'], ensure_ascii=False, indent=2)}")
            
            # Проверка валидности JSON
            is_valid = self._validate_json(example['data'])
            print(f"   ✅ JSON валиден: {'Да' if is_valid else 'Нет'}")
            
            # Проверка соответствия схеме
            schema_compliance = self._check_schema_compliance(example['data'])
            print(f"   📋 Соответствие схеме: {'Да' if schema_compliance else 'Нет'}")
    
    def demo_performance_metrics(self):
        """Демонстрация метрик производительности"""
        print("\n\n⚡ ДЕМОНСТРАЦИЯ МЕТРИК ПРОИЗВОДИТЕЛЬНОСТИ")
        print("=" * 50)
        
        # Тестирование производительности
        test_texts = [
            "Короткий текст",
            "Средний текст для тестирования производительности системы",
            "Длинный текст для тестирования производительности системы OCR с множеством символов и слов для оценки качества работы алгоритмов распознавания текста"
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n📄 Тест {i}: {text[:30]}...")
            
            # Измерение времени обработки
            start_time = time.time()
            metrics = self._calculate_metrics(text, text)  # Идеальное совпадение
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            print(f"   ⏱️  Время обработки: {processing_time:.3f} сек")
            print(f"   📊 Символов: {len(text)}")
            print(f"   📊 Слов: {len(text.split())}")
            print(f"   🎯 CER: {metrics.get('cer', 0):.3f}")
            print(f"   🎯 WER: {metrics.get('wer', 0):.3f}")
    
    def _calculate_metrics(self, extracted_text: str, ground_truth: str) -> Dict[str, Any]:
        """Расчет метрик качества"""
        try:
            response = requests.post(
                f"{self.base_url}/metrics/calculate",
                json={
                    "extracted_text": extracted_text,
                    "ground_truth": ground_truth
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception as e:
            print(f"Ошибка при расчете метрик: {e}")
            return {}
    
    def _display_metrics(self, metrics: Dict[str, Any]):
        """Отображение метрик"""
        print(f"   📊 CER: {metrics.get('cer', 0):.3f}")
        print(f"   📊 WER: {metrics.get('wer', 0):.3f}")
        print(f"   📊 Normalized Levenshtein: {metrics.get('normalized_levenshtein', 0):.3f}")
        print(f"   📊 Exact Match: {metrics.get('exact_match', 0)}")
        print(f"   📊 Char F1: {metrics.get('char_f1', 0):.3f}")
        print(f"   📊 Word F1: {metrics.get('word_f1', 0):.3f}")
    
    def _calculate_overall_score(self, metrics: Dict[str, Any]) -> float:
        """Расчет общего балла"""
        # Веса для разных метрик
        weights = {
            'cer': 0.4,
            'wer': 0.3,
            'levenshtein': 0.2,
            'exact_match': 0.1
        }
        
        score = 0
        score += (1 - metrics.get('cer', 1)) * weights['cer'] * 100
        score += (1 - metrics.get('wer', 1)) * weights['wer'] * 100
        score += (1 - metrics.get('normalized_levenshtein', 1)) * weights['levenshtein'] * 100
        score += metrics.get('exact_match', 0) * weights['exact_match'] * 100
        
        return score
    
    def _simulate_field_extraction(self, text: str, expected_fields: list) -> Dict[str, str]:
        """Симуляция извлечения полей"""
        # Простая симуляция извлечения полей
        extracted = {}
        
        for field in expected_fields:
            if field == "name" and "Иванов" in text:
                extracted[field] = "Иванов Иван Иванович"
            elif field == "date" and "01.01" in text:
                extracted[field] = "01.01.1990"
            elif field == "phone" and "+7" in text:
                extracted[field] = "+7(999)123-45-67"
            elif field == "email" and "@" in text:
                extracted[field] = "sidor@example.com"
            elif field == "amount" and "100000" in text:
                extracted[field] = "100000"
            elif field == "passport" and "1234" in text:
                extracted[field] = "1234 567890"
        
        return extracted
    
    def _calculate_field_accuracy(self, extracted: Dict[str, str], expected: list) -> float:
        """Расчет точности извлечения полей"""
        if not expected:
            return 0.0
        
        correct_fields = 0
        for field in expected:
            if field in extracted and extracted[field]:
                correct_fields += 1
        
        return (correct_fields / len(expected)) * 100
    
    def _validate_json(self, data: Dict[str, Any]) -> bool:
        """Проверка валидности JSON"""
        try:
            json.dumps(data, ensure_ascii=False)
            return True
        except (TypeError, ValueError):
            return False
    
    def _check_schema_compliance(self, data: Dict[str, Any]) -> bool:
        """Проверка соответствия схеме"""
        # Простая проверка наличия обязательных полей
        required_fields = ["name"]
        
        for field in required_fields:
            if field not in data or not data[field]:
                return False
        
        return True
    
    def run_demo(self):
        """Запуск полной демонстрации"""
        print("🚀 ЗАПУСК ДЕМОНСТРАЦИИ OCR QUALITY ASSESSMENT API")
        print("=" * 60)
        
        # Проверка доступности сервера
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code != 200:
                print("❌ Сервер недоступен. Убедитесь, что сервер запущен.")
                return
        except requests.exceptions.ConnectionError:
            print("❌ Не удается подключиться к серверу. Убедитесь, что сервер запущен.")
            return
        
        print("✅ Сервер доступен")
        
        # Запуск демонстраций
        self.demo_ocr_quality_assessment()
        self.demo_field_extraction()
        self.demo_noise_handling()
        self.demo_json_validation()
        self.demo_performance_metrics()
        
        print("\n\n🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
        print("=" * 60)
        print("Система готова к использованию для оценки качества OCR!")

def main():
    """Основная функция"""
    demo = OCRDemo()
    demo.run_demo()

if __name__ == "__main__":
    main()
