import re
import Levenshtein
from typing import List, Dict, Any, Tuple
from sklearn.metrics import precision_score, recall_score, f1_score
import logging

logger = logging.getLogger(__name__)

class MetricsCalculator:
    def __init__(self):
        """Инициализация калькулятора метрик"""
        pass
    
    def calculate_all_metrics(self, extracted_text: str, ground_truth: str) -> Dict[str, float]:
        """
        Расчет всех основных метрик качества OCR
        
        Args:
            extracted_text: Извлеченный текст
            ground_truth: Эталонный текст
            
        Returns:
            Словарь с метриками
        """
        try:
            metrics = {}
            
            # CER (Character Error Rate)
            metrics['cer'] = self.calculate_cer(extracted_text, ground_truth)
            
            # WER (Word Error Rate)
            metrics['wer'] = self.calculate_wer(extracted_text, ground_truth)
            
            # Normalized Levenshtein Distance
            metrics['normalized_levenshtein'] = self.calculate_normalized_levenshtein(
                extracted_text, ground_truth
            )
            
            # Exact Match
            metrics['exact_match'] = 1.0 if extracted_text.strip() == ground_truth.strip() else 0.0
            
            # Character-level precision, recall, F1
            char_metrics = self.calculate_character_metrics(extracted_text, ground_truth)
            metrics.update(char_metrics)
            
            # Word-level precision, recall, F1
            word_metrics = self.calculate_word_metrics(extracted_text, ground_truth)
            metrics.update(word_metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Ошибка при расчете метрик: {str(e)}")
            return {}
    
    def calculate_cer(self, extracted_text: str, ground_truth: str) -> float:
        """
        Расчет Character Error Rate (CER)
        
        Args:
            extracted_text: Извлеченный текст
            ground_truth: Эталонный текст
            
        Returns:
            CER в диапазоне [0, 1]
        """
        try:
            if not ground_truth:
                return 1.0 if extracted_text else 0.0
            
            # Нормализация текста
            extracted_normalized = self._normalize_text(extracted_text)
            ground_truth_normalized = self._normalize_text(ground_truth)
            
            # Расчет расстояния Левенштейна
            distance = Levenshtein.distance(extracted_normalized, ground_truth_normalized)
            
            # CER = расстояние / длина эталонного текста
            cer = distance / len(ground_truth_normalized) if ground_truth_normalized else 0.0
            
            return min(cer, 1.0)  # Ограничиваем максимальным значением 1.0
            
        except Exception as e:
            logger.error(f"Ошибка при расчете CER: {str(e)}")
            return 1.0
    
    def calculate_wer(self, extracted_text: str, ground_truth: str) -> float:
        """
        Расчет Word Error Rate (WER)
        
        Args:
            extracted_text: Извлеченный текст
            ground_truth: Эталонный текст
            
        Returns:
            WER в диапазоне [0, 1]
        """
        try:
            if not ground_truth:
                return 1.0 if extracted_text else 0.0
            
            # Разбиение на слова
            extracted_words = self._split_into_words(extracted_text)
            ground_truth_words = self._split_into_words(ground_truth)
            
            if not ground_truth_words:
                return 1.0 if extracted_words else 0.0
            
            # Расчет расстояния Левенштейна на уровне слов
            distance = Levenshtein.distance(extracted_words, ground_truth_words)
            
            # WER = расстояние / количество слов в эталонном тексте
            wer = distance / len(ground_truth_words)
            
            return min(wer, 1.0)  # Ограничиваем максимальным значением 1.0
            
        except Exception as e:
            logger.error(f"Ошибка при расчете WER: {str(e)}")
            return 1.0
    
    def calculate_normalized_levenshtein(self, extracted_text: str, ground_truth: str) -> float:
        """
        Расчет нормализованного расстояния Левенштейна
        
        Args:
            extracted_text: Извлеченный текст
            ground_truth: Эталонный текст
            
        Returns:
            Нормализованное расстояние в диапазоне [0, 1]
        """
        try:
            if not ground_truth and not extracted_text:
                return 0.0
            
            # Нормализация текста
            extracted_normalized = self._normalize_text(extracted_text)
            ground_truth_normalized = self._normalize_text(ground_truth)
            
            # Расчет расстояния Левенштейна
            distance = Levenshtein.distance(extracted_normalized, ground_truth_normalized)
            
            # Нормализация по максимальной длине
            max_length = max(len(extracted_normalized), len(ground_truth_normalized))
            
            if max_length == 0:
                return 0.0
            
            normalized_distance = distance / max_length
            return min(normalized_distance, 1.0)
            
        except Exception as e:
            logger.error(f"Ошибка при расчете нормализованного расстояния Левенштейна: {str(e)}")
            return 1.0
    
    def calculate_character_metrics(self, extracted_text: str, ground_truth: str) -> Dict[str, float]:
        """
        Расчет метрик на уровне символов (precision, recall, F1)
        
        Args:
            extracted_text: Извлеченный текст
            ground_truth: Эталонный текст
            
        Returns:
            Словарь с метриками
        """
        try:
            extracted_normalized = self._normalize_text(extracted_text)
            ground_truth_normalized = self._normalize_text(ground_truth)
            
            # Создание множеств символов
            extracted_chars = set(extracted_normalized)
            ground_truth_chars = set(ground_truth_normalized)
            
            # Расчет пересечения
            intersection = extracted_chars.intersection(ground_truth_chars)
            
            # Precision: сколько извлеченных символов правильные
            precision = len(intersection) / len(extracted_chars) if extracted_chars else 0.0
            
            # Recall: сколько правильных символов извлечено
            recall = len(intersection) / len(ground_truth_chars) if ground_truth_chars else 0.0
            
            # F1-score
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            return {
                'char_precision': precision,
                'char_recall': recall,
                'char_f1': f1
            }
            
        except Exception as e:
            logger.error(f"Ошибка при расчете метрик символов: {str(e)}")
            return {'char_precision': 0.0, 'char_recall': 0.0, 'char_f1': 0.0}
    
    def calculate_word_metrics(self, extracted_text: str, ground_truth: str) -> Dict[str, float]:
        """
        Расчет метрик на уровне слов (precision, recall, F1)
        
        Args:
            extracted_text: Извлеченный текст
            ground_truth: Эталонный текст
            
        Returns:
            Словарь с метриками
        """
        try:
            extracted_words = set(self._split_into_words(extracted_text))
            ground_truth_words = set(self._split_into_words(ground_truth))
            
            # Расчет пересечения
            intersection = extracted_words.intersection(ground_truth_words)
            
            # Precision: сколько извлеченных слов правильные
            precision = len(intersection) / len(extracted_words) if extracted_words else 0.0
            
            # Recall: сколько правильных слов извлечено
            recall = len(intersection) / len(ground_truth_words) if ground_truth_words else 0.0
            
            # F1-score
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            return {
                'word_precision': precision,
                'word_recall': recall,
                'word_f1': f1
            }
            
        except Exception as e:
            logger.error(f"Ошибка при расчете метрик слов: {str(e)}")
            return {'word_precision': 0.0, 'word_recall': 0.0, 'word_f1': 0.0}
    
    def calculate_field_metrics(self, extracted_text: str, ground_truth: str, field_name: str) -> Dict[str, float]:
        """
        Расчет метрик для конкретного поля
        
        Args:
            extracted_text: Извлеченный текст
            ground_truth: Эталонный текст
            field_name: Название поля
            
        Returns:
            Словарь с метриками поля
        """
        try:
            # Здесь можно добавить логику извлечения конкретного поля
            # Пока возвращаем общие метрики
            return self.calculate_all_metrics(extracted_text, ground_truth)
            
        except Exception as e:
            logger.error(f"Ошибка при расчете метрик поля {field_name}: {str(e)}")
            return {}
    
    def calculate_noise_metrics(self, extracted_text: str, ground_truth: str) -> Dict[str, float]:
        """
        Расчет метрик для зашумленных документов
        
        Args:
            extracted_text: Извлеченный текст
            ground_truth: Эталонный текст
            
        Returns:
            Словарь с метриками для зашумленных данных
        """
        try:
            # Базовые метрики
            metrics = self.calculate_all_metrics(extracted_text, ground_truth)
            
            # Дополнительные метрики для зашумленных данных
            metrics['noise_cer'] = metrics.get('cer', 1.0)
            metrics['noise_wer'] = metrics.get('wer', 1.0)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Ошибка при расчете метрик для зашумленных данных: {str(e)}")
            return {}
    
    def _normalize_text(self, text: str) -> str:
        """
        Нормализация текста для сравнения
        
        Args:
            text: Исходный текст
            
        Returns:
            Нормализованный текст
        """
        if not text:
            return ""
        
        # Приведение к нижнему регистру
        normalized = text.lower()
        
        # Удаление лишних пробелов
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Удаление знаков препинания (опционально)
        # normalized = re.sub(r'[^\w\s]', '', normalized)
        
        return normalized.strip()
    
    def _split_into_words(self, text: str) -> List[str]:
        """
        Разбиение текста на слова
        
        Args:
            text: Исходный текст
            
        Returns:
            Список слов
        """
        if not text:
            return []
        
        # Нормализация и разбиение на слова
        normalized = self._normalize_text(text)
        words = normalized.split()
        
        return words
    
    def calculate_document_level_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Расчет метрик на уровне документа
        
        Args:
            results: Список результатов обработки документов
            
        Returns:
            Словарь с агрегированными метриками
        """
        try:
            if not results:
                return {}
            
            # Агрегация метрик
            total_cer = sum(r.get('cer', 0) for r in results)
            total_wer = sum(r.get('wer', 0) for r in results)
            exact_matches = sum(1 for r in results if r.get('exact_match', 0) == 1.0)
            
            return {
                'average_cer': total_cer / len(results),
                'average_wer': total_wer / len(results),
                'exact_match_percentage': (exact_matches / len(results)) * 100
            }
            
        except Exception as e:
            logger.error(f"Ошибка при расчете метрик на уровне документа: {str(e)}")
            return {}
