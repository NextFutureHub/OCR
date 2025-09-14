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
