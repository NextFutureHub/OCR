import re
import json
import jsonschema
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class DataExtractor:
    def __init__(self):
        """Инициализация экстрактора данных"""
        self.field_patterns = {
            'name': [
                r'(?:имя|name|фио|ф\.и\.о\.?)\s*:?\s*([а-яё\s]+)',
                r'([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)'
            ],
            'date': [
                r'(?:дата|date)\s*:?\s*(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
                r'(\d{1,2}[./]\d{1,2}[./]\d{2,4})'
            ],
            'phone': [
                r'(?:телефон|phone|тел\.?)\s*:?\s*([+]?[0-9\s\-\(\)]+)',
                r'([+]?[0-9\s\-\(\)]{10,})'
            ],
            'email': [
                r'(?:email|почта|e-mail)\s*:?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            ],
            'address': [
                r'(?:адрес|address|адр\.?)\s*:?\s*([а-яё\s\d,.-]+)',
                r'(г\.\s*[а-яё\s]+,\s*[а-яё\s\d,.-]+)'
            ],
            'passport': [
                r'(?:паспорт|passport|пасп\.?)\s*:?\s*(\d{4}\s*\d{6})',
                r'(\d{4}\s*\d{6})'
            ],
            'inn': [
                r'(?:инн|inn)\s*:?\s*(\d{10,12})',
                r'(\d{10,12})'
            ],
            'amount': [
                r'(?:сумма|amount|сумм\.?)\s*:?\s*(\d+(?:[.,]\d+)?)',
                r'(\d+(?:[.,]\d+)?\s*(?:руб|р\.?|₽))'
            ]
        }
    
    def extract_fields(self, text: str, expected_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Извлечение структурированных данных из текста
        
        Args:
            text: Извлеченный OCR текст
            expected_fields: Список ожидаемых полей
            
        Returns:
            Словарь с извлеченными данными
        """
        try:
            extracted_data = {}
            
            # Если указаны ожидаемые поля, извлекаем только их
            if expected_fields:
                for field in expected_fields:
                    extracted_data[field] = self._extract_field(text, field)
            else:
                # Извлекаем все доступные поля
                for field_name, patterns in self.field_patterns.items():
                    extracted_data[field_name] = self._extract_field(text, field_name)
            
            # Очистка и валидация данных
            extracted_data = self._clean_extracted_data(extracted_data)
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении полей: {str(e)}")
            return {}
    
    def _extract_field(self, text: str, field_name: str) -> Optional[str]:
        """
        Извлечение конкретного поля из текста
        
        Args:
            text: Исходный текст
            field_name: Название поля
            
        Returns:
            Извлеченное значение поля или None
        """
        try:
            if field_name not in self.field_patterns:
                return None
            
            patterns = self.field_patterns[field_name]
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    # Возвращаем первое найденное значение
                    value = matches[0].strip()
                    if value:
                        return self._clean_field_value(value, field_name)
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении поля {field_name}: {str(e)}")
            return None
    
    def _clean_field_value(self, value: str, field_name: str) -> str:
        """
        Очистка и нормализация значения поля
        
        Args:
            value: Исходное значение
            field_name: Название поля
            
        Returns:
            Очищенное значение
        """
        try:
            # Базовая очистка
            cleaned = value.strip()
            
            # Специфичная очистка для разных типов полей
            if field_name == 'phone':
                # Удаление всех символов кроме цифр и +
                cleaned = re.sub(r'[^\d+]', '', cleaned)
            elif field_name == 'email':
                # Приведение к нижнему регистру
                cleaned = cleaned.lower()
            elif field_name == 'date':
                # Нормализация формата даты
                cleaned = self._normalize_date(cleaned)
            elif field_name == 'amount':
                # Нормализация суммы
                cleaned = self._normalize_amount(cleaned)
            elif field_name == 'name':
                # Нормализация имени
                cleaned = self._normalize_name(cleaned)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Ошибка при очистке поля {field_name}: {str(e)}")
            return value
    
    def _normalize_date(self, date_str: str) -> str:
        """Нормализация даты"""
        try:
            # Замена разделителей на точки
            normalized = re.sub(r'[/\-]', '.', date_str)
            
            # Проверка и исправление формата
            if re.match(r'\d{1,2}\.\d{1,2}\.\d{2,4}', normalized):
                return normalized
            
            return date_str
            
        except Exception as e:
            logger.error(f"Ошибка при нормализации даты: {str(e)}")
            return date_str
    
    def _normalize_amount(self, amount_str: str) -> str:
        """Нормализация суммы"""
        try:
            # Извлечение числа
            match = re.search(r'(\d+(?:[.,]\d+)?)', amount_str)
            if match:
                amount = match.group(1)
                # Замена запятой на точку
                amount = amount.replace(',', '.')
                return amount
            
            return amount_str
            
        except Exception as e:
            logger.error(f"Ошибка при нормализации суммы: {str(e)}")
            return amount_str
    
    def _normalize_name(self, name_str: str) -> str:
        """Нормализация имени"""
        try:
            # Удаление лишних пробелов и приведение к правильному регистру
            words = name_str.split()
            normalized_words = []
            
            for word in words:
                if word:
                    # Первая буква заглавная, остальные строчные
                    normalized_word = word[0].upper() + word[1:].lower()
                    normalized_words.append(normalized_word)
            
            return ' '.join(normalized_words)
            
        except Exception as e:
            logger.error(f"Ошибка при нормализации имени: {str(e)}")
            return name_str
    
    def _clean_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Очистка извлеченных данных
        
        Args:
            data: Словарь с извлеченными данными
            
        Returns:
            Очищенный словарь
        """
        try:
            cleaned_data = {}
            
            for key, value in data.items():
                if value is not None and str(value).strip():
                    cleaned_data[key] = value
            
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Ошибка при очистке данных: {str(e)}")
            return data
    
    def validate_json(self, data: Dict[str, Any]) -> bool:
        """
        Проверка валидности JSON
        
        Args:
            data: Данные для проверки
            
        Returns:
            True если JSON валиден, False иначе
        """
        try:
            # Попытка сериализации в JSON
            json.dumps(data, ensure_ascii=False)
            return True
            
        except (TypeError, ValueError) as e:
            logger.error(f"JSON не валиден: {str(e)}")
            return False
    
    def validate_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        Проверка соответствия данных схеме
        
        Args:
            data: Данные для проверки
            schema: JSON Schema
            
        Returns:
            True если данные соответствуют схеме, False иначе
        """
        try:
            if not schema:
                return True
            
            # Валидация с использованием jsonschema
            jsonschema.validate(data, schema)
            return True
            
        except jsonschema.ValidationError as e:
            logger.error(f"Данные не соответствуют схеме: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Ошибка при валидации схемы: {str(e)}")
            return False
    
    def calculate_field_accuracy(self, extracted_data: Dict[str, Any], 
                               ground_truth_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Расчет точности извлечения для каждого поля
        
        Args:
            extracted_data: Извлеченные данные
            ground_truth_data: Эталонные данные
            
        Returns:
            Словарь с точностью для каждого поля
        """
        try:
            field_accuracy = {}
            
            for field in ground_truth_data.keys():
                extracted_value = extracted_data.get(field, "")
                ground_truth_value = ground_truth_data.get(field, "")
                
                if ground_truth_value:
                    # Простое сравнение строк
                    accuracy = 1.0 if extracted_value == ground_truth_value else 0.0
                    field_accuracy[field] = accuracy
                else:
                    field_accuracy[field] = 0.0
            
            return field_accuracy
            
        except Exception as e:
            logger.error(f"Ошибка при расчете точности полей: {str(e)}")
            return {}
    
    def calculate_f1_score_per_field(self, extracted_data: Dict[str, Any], 
                                   ground_truth_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Расчет F1-score для каждого поля
        
        Args:
            extracted_data: Извлеченные данные
            ground_truth_data: Эталонные данные
            
        Returns:
            Словарь с F1-score для каждого поля
        """
        try:
            field_f1 = {}
            
            for field in ground_truth_data.keys():
                extracted_value = extracted_data.get(field, "")
                ground_truth_value = ground_truth_data.get(field, "")
                
                if ground_truth_value:
                    # Для простоты используем точное совпадение
                    # В реальном проекте можно использовать более сложные метрики
                    if extracted_value == ground_truth_value:
                        field_f1[field] = 1.0
                    else:
                        # Частичное совпадение
                        if extracted_value and ground_truth_value:
                            # Простая метрика на основе длины совпадающих символов
                            common_chars = set(extracted_value.lower()) & set(ground_truth_value.lower())
                            total_chars = set(extracted_value.lower()) | set(ground_truth_value.lower())
                            
                            if total_chars:
                                field_f1[field] = len(common_chars) / len(total_chars)
                            else:
                                field_f1[field] = 0.0
                        else:
                            field_f1[field] = 0.0
                else:
                    field_f1[field] = 0.0
            
            return field_f1
            
        except Exception as e:
            logger.error(f"Ошибка при расчете F1-score полей: {str(e)}")
            return {}
    
    def calculate_exact_match_percentage(self, results: List[Dict[str, Any]]) -> float:
        """
        Расчет процента документов, извлеченных полностью верно
        
        Args:
            results: Список результатов обработки документов
            
        Returns:
            Процент точных совпадений
        """
        try:
            if not results:
                return 0.0
            
            exact_matches = 0
            
            for result in results:
                extracted_data = result.get('extracted_data', {})
                ground_truth_data = result.get('ground_truth_data', {})
                
                # Проверка точного совпадения всех полей
                if extracted_data == ground_truth_data:
                    exact_matches += 1
            
            return (exact_matches / len(results)) * 100
            
        except Exception as e:
            logger.error(f"Ошибка при расчете процента точных совпадений: {str(e)}")
            return 0.0
    
    def add_custom_field_pattern(self, field_name: str, patterns: List[str]):
        """
        Добавление пользовательского паттерна для поля
        
        Args:
            field_name: Название поля
            patterns: Список регулярных выражений
        """
        try:
            self.field_patterns[field_name] = patterns
            logger.info(f"Добавлен паттерн для поля {field_name}")
            
        except Exception as e:
            logger.error(f"Ошибка при добавлении паттерна для поля {field_name}: {str(e)}")
    
    def get_available_fields(self) -> List[str]:
        """Получение списка доступных полей для извлечения"""
        return list(self.field_patterns.keys())
