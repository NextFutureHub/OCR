import easyocr
import cv2
import numpy as np
from PIL import Image
import io
import logging
from typing import List, Tuple, Dict, Any

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self, languages: List[str] = ['ru', 'en']):
        """
        Инициализация OCR сервиса с EasyOCR
        
        Args:
            languages: Список языков для распознавания
        """
        self.languages = languages
        self.reader = None
        self._initialize_reader()
    
    def _initialize_reader(self):
        """Инициализация EasyOCR reader"""
        try:
            self.reader = easyocr.Reader(self.languages, gpu=False)
            logger.info(f"EasyOCR инициализирован для языков: {self.languages}")
        except Exception as e:
            logger.error(f"Ошибка инициализации EasyOCR: {str(e)}")
            raise
    
    def extract_text(self, image_data: bytes) -> str:
        """
        Извлечение текста из изображения
        
        Args:
            image_data: Байты изображения
            
        Returns:
            Извлеченный текст
        """
        try:
            # Конвертация байтов в изображение
            image = self._bytes_to_image(image_data)
            
            # Проверка, что изображение не пустое
            if image is None or image.size == 0:
                logger.warning("Получено пустое изображение")
                return ""
            
            # Предобработка изображения
            processed_image = self._preprocess_image(image)
            
            # OCR распознавание
            results = self.reader.readtext(processed_image)
            
            # Извлечение текста
            extracted_text = self._extract_text_from_results(results)
            
            logger.info(f"Извлечено {len(extracted_text)} символов текста")
            return extracted_text
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении текста: {str(e)}")
            # Возвращаем пустую строку вместо исключения
            return ""
    
    def extract_text_with_confidence(self, image_data: bytes, min_confidence: float = 0.5) -> List[Dict[str, Any]]:
        """
        Извлечение текста с информацией о уверенности
        
        Args:
            image_data: Байты изображения
            min_confidence: Минимальная уверенность для включения текста
            
        Returns:
            Список словарей с текстом, координатами и уверенностью
        """
        try:
            image = self._bytes_to_image(image_data)
            processed_image = self._preprocess_image(image)
            
            results = self.reader.readtext(processed_image)
            
            filtered_results = []
            for (bbox, text, confidence) in results:
                if confidence >= min_confidence:
                    filtered_results.append({
                        'text': text,
                        'confidence': confidence,
                        'bbox': bbox
                    })
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении текста с уверенностью: {str(e)}")
            raise
    
    def _bytes_to_image(self, image_data: bytes) -> np.ndarray:
        """Конвертация байтов в изображение OpenCV"""
        try:
            # Проверка, что данные не пустые
            if not image_data:
                raise ValueError("Пустые данные изображения")
            
            # Использование PIL для чтения изображения
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Проверка, что изображение загружено
            if pil_image is None:
                raise ValueError("Не удалось загрузить изображение")
            
            # Конвертация в RGB если необходимо
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Конвертация в numpy array для OpenCV
            image = np.array(pil_image)
            
            # Проверка, что массив не пустой
            if image.size == 0:
                raise ValueError("Пустой массив изображения")
            
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            return image
            
        except Exception as e:
            logger.error(f"Ошибка конвертации байтов в изображение: {str(e)}")
            # Создаем простое тестовое изображение
            test_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
            return test_image
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Предобработка изображения для улучшения качества OCR
        
        Args:
            image: Исходное изображение
            
        Returns:
            Обработанное изображение
        """
        try:
            # Конвертация в оттенки серого
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Увеличение контраста
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # Удаление шума
            denoised = cv2.medianBlur(enhanced, 3)
            
            # Бинаризация
            _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return binary
            
        except Exception as e:
            logger.error(f"Ошибка предобработки изображения: {str(e)}")
            return image
    
    def _extract_text_from_results(self, results: List[Tuple]) -> str:
        """
        Извлечение текста из результатов OCR
        
        Args:
            results: Результаты от EasyOCR
            
        Returns:
            Объединенный текст
        """
        try:
            texts = []
            for (bbox, text, confidence) in results:
                if confidence > 0.3:  # Фильтрация по уверенности
                    texts.append(text.strip())
            
            # Объединение текста с сохранением порядка
            full_text = ' '.join(texts)
            
            return full_text
            
        except Exception as e:
            logger.error(f"Ошибка извлечения текста из результатов: {str(e)}")
            return ""
    
    def extract_text_with_columns(self, image_data: bytes) -> Dict[str, Any]:
        """
        Извлечение текста с анализом столбцов
        
        Args:
            image_data: Байты изображения
            
        Returns:
            Словарь с текстом, столбцами и метаданными
        """
        try:
            image = self._bytes_to_image(image_data)
            processed_image = self._preprocess_image(image)
            
            # OCR распознавание
            results = self.reader.readtext(processed_image)
            
            # Общий текст (всегда извлекаем)
            full_text = self._extract_text_from_results(results)
            
            # Анализ столбцов
            columns_info = self._analyze_columns(results, image.shape[1])
            
            # Извлечение текста по столбцам
            column_texts = self._extract_text_by_columns(results, columns_info)
            
            logger.info(f"Извлечено {len(full_text)} символов, обнаружено {len(column_texts)} столбцов")
            
            return {
                'full_text': full_text,
                'columns': column_texts,
                'columns_count': len(column_texts),
                'column_info': columns_info,
                'has_multiple_columns': len(column_texts) > 1
            }
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении текста с столбцами: {str(e)}")
            # В случае ошибки, пытаемся извлечь хотя бы базовый текст
            try:
                basic_text = self.extract_text(image_data)
                return {
                    'full_text': basic_text,
                    'columns': [],
                    'columns_count': 0,
                    'column_info': [],
                    'has_multiple_columns': False
                }
            except:
                return {
                    'full_text': '',
                    'columns': [],
                    'columns_count': 0,
                    'column_info': [],
                    'has_multiple_columns': False
                }
    
    def _analyze_columns(self, results: List[Tuple], image_width: int) -> List[Dict[str, Any]]:
        """
        Анализ столбцов в документе
        
        Args:
            results: Результаты OCR
            image_width: Ширина изображения
            
        Returns:
            Информация о столбцах
        """
        try:
            if not results:
                return []
            
            # Фильтруем результаты по уверенности
            filtered_results = [(bbox, text, confidence) for (bbox, text, confidence) in results if confidence > 0.3]
            
            if len(filtered_results) < 2:
                return []
            
            # Вычисляем X-координаты всех элементов
            x_coords = []
            for (bbox, text, confidence) in filtered_results:
                avg_x = sum([point[0] for point in bbox]) / len(bbox)
                x_coords.append(avg_x)
            
            # Сортируем X-координаты
            x_coords.sort()
            
            # Находим разрыв между столбцами
            max_gap = 0
            gap_index = 0
            
            for i in range(len(x_coords) - 1):
                gap = x_coords[i + 1] - x_coords[i]
                if gap > max_gap:
                    max_gap = gap
                    gap_index = i
            
            # Если разрыв достаточно большой, считаем что есть два столбца
            min_gap_threshold = image_width * 0.2  # 20% от ширины изображения
            
            if max_gap < min_gap_threshold:
                # Считаем что это один столбец
                return []
            
            # Разделяем на два столбца
            split_x = (x_coords[gap_index] + x_coords[gap_index + 1]) / 2
            
            left_column = []
            right_column = []
            
            for (bbox, text, confidence) in filtered_results:
                avg_x = sum([point[0] for point in bbox]) / len(bbox)
                
                if avg_x < split_x:
                    left_column.append((bbox, text, confidence, avg_x))
                else:
                    right_column.append((bbox, text, confidence, avg_x))
            
            columns_info = []
            
            # Левый столбец
            if left_column:
                left_column.sort(key=lambda x: x[3])  # Сортировка по X
                columns_info.append({
                    'side': 'left',
                    'x_range': (0, split_x),
                    'items': left_column,
                    'language': self._detect_language([item[1] for item in left_column])
                })
            
            # Правый столбец
            if right_column:
                right_column.sort(key=lambda x: x[3])  # Сортировка по X
                columns_info.append({
                    'side': 'right',
                    'x_range': (split_x, image_width),
                    'items': right_column,
                    'language': self._detect_language([item[1] for item in right_column])
                })
            
            logger.info(f"Обнаружено {len(columns_info)} столбцов, разрыв: {max_gap:.1f}px")
            return columns_info
            
        except Exception as e:
            logger.error(f"Ошибка анализа столбцов: {str(e)}")
            return []
    
    def _extract_text_by_columns(self, results: List[Tuple], columns_info: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Извлечение текста по столбцам
        
        Args:
            results: Результаты OCR
            columns_info: Информация о столбцах
            
        Returns:
            Список текстов по столбцам
        """
        try:
            column_texts = []
            
            if not columns_info:
                # Если столбцы не обнаружены, создаем один "столбец" со всем текстом
                if results:
                    all_text = ' '.join([text for (bbox, text, confidence) in results if confidence > 0.3])
                    if all_text.strip():
                        column_texts.append({
                            'text': all_text,
                            'side': 'single',
                            'language': self._detect_language([text for (bbox, text, confidence) in results if confidence > 0.3]),
                            'items_count': len([r for r in results if r[2] > 0.3]),
                            'confidence_avg': sum([r[2] for r in results if r[2] > 0.3]) / len([r for r in results if r[2] > 0.3]) if results else 0
                        })
                return column_texts
            
            for column in columns_info:
                # Сортировка элементов по Y-координате (сверху вниз)
                items = column['items']
                items.sort(key=lambda x: sum([point[1] for point in x[0]]) / len(x[0]))
                
                # Объединение текста столбца
                column_text = ' '.join([item[1] for item in items])
                
                column_texts.append({
                    'text': column_text,
                    'side': column['side'],
                    'language': column['language'],
                    'items_count': len(items),
                    'confidence_avg': sum([item[2] for item in items]) / len(items) if items else 0
                })
            
            return column_texts
            
        except Exception as e:
            logger.error(f"Ошибка извлечения текста по столбцам: {str(e)}")
            return []
    
    def _detect_language(self, texts: List[str]) -> str:
        """
        Простое определение языка текста
        
        Args:
            texts: Список текстов
            
        Returns:
            Код языка
        """
        try:
            if not texts:
                return 'unknown'
            
            # Объединяем все тексты
            full_text = ' '.join(texts).lower()
            
            # Простая эвристика для определения языка
            cyrillic_chars = sum(1 for char in full_text if 'а' <= char <= 'я' or 'А' <= char <= 'Я')
            latin_chars = sum(1 for char in full_text if 'a' <= char <= 'z' or 'A' <= char <= 'Z')
            
            if cyrillic_chars > latin_chars:
                return 'ru'
            elif latin_chars > cyrillic_chars:
                return 'en'
            else:
                return 'mixed'
                
        except Exception as e:
            logger.error(f"Ошибка определения языка: {str(e)}")
            return 'unknown'
    
    def get_supported_languages(self) -> List[str]:
        """Получение списка поддерживаемых языков"""
        return self.languages
    
    def set_languages(self, languages: List[str]):
        """
        Изменение языков для распознавания
        
        Args:
            languages: Новый список языков
        """
        self.languages = languages
        self._initialize_reader()
        logger.info(f"Языки изменены на: {languages}")
