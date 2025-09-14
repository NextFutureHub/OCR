import cv2
import numpy as np
from PIL import Image
import io
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class NoiseHandler:
    def __init__(self):
        """Инициализация обработчика шума"""
        pass
    
    def clean_image(self, image_data: bytes) -> bytes:
        """
        Очистка изображения от шума
        
        Args:
            image_data: Байты исходного изображения
            
        Returns:
            Байты очищенного изображения
        """
        try:
            # Конвертация байтов в изображение
            image = self._bytes_to_image(image_data)
            
            # Применение различных методов очистки
            cleaned_image = self._apply_noise_reduction(image)
            
            # Конвертация обратно в байты
            cleaned_bytes = self._image_to_bytes(cleaned_image)
            
            return cleaned_bytes
            
        except Exception as e:
            logger.error(f"Ошибка при очистке изображения: {str(e)}")
            return image_data
    
    def _bytes_to_image(self, image_data: bytes) -> np.ndarray:
        """Конвертация байтов в изображение OpenCV"""
        try:
            pil_image = Image.open(io.BytesIO(image_data))
            
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            image = np.array(pil_image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            return image
            
        except Exception as e:
            logger.error(f"Ошибка конвертации байтов в изображение: {str(e)}")
            raise
    
    def _image_to_bytes(self, image: np.ndarray) -> bytes:
        """Конвертация изображения OpenCV в байты"""
        try:
            # Конвертация в RGB
            if len(image.shape) == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
            
            # Конвертация в PIL Image
            pil_image = Image.fromarray(image_rgb)
            
            # Конвертация в байты
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            return img_byte_arr
            
        except Exception as e:
            logger.error(f"Ошибка конвертации изображения в байты: {str(e)}")
            raise
    
    def _apply_noise_reduction(self, image: np.ndarray) -> np.ndarray:
        """
        Применение методов снижения шума
        
        Args:
            image: Исходное изображение
            
        Returns:
            Очищенное изображение
        """
        try:
            # Конвертация в оттенки серого
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # 1. Удаление солевого и перцового шума
            denoised = self._remove_salt_pepper_noise(gray)
            
            # 2. Удаление гауссова шума
            denoised = self._remove_gaussian_noise(denoised)
            
            # 3. Улучшение контраста
            enhanced = self._enhance_contrast(denoised)
            
            # 4. Морфологические операции
            cleaned = self._apply_morphological_operations(enhanced)
            
            # 5. Бинаризация
            binary = self._adaptive_binarization(cleaned)
            
            return binary
            
        except Exception as e:
            logger.error(f"Ошибка при применении снижения шума: {str(e)}")
            return image
    
    def _remove_salt_pepper_noise(self, image: np.ndarray) -> np.ndarray:
        """Удаление солевого и перцового шума"""
        try:
            # Медианный фильтр эффективен против солевого и перцового шума
            denoised = cv2.medianBlur(image, 3)
            return denoised
            
        except Exception as e:
            logger.error(f"Ошибка при удалении солевого и перцового шума: {str(e)}")
            return image
    
    def _remove_gaussian_noise(self, image: np.ndarray) -> np.ndarray:
        """Удаление гауссова шума"""
        try:
            # Гауссов фильтр для удаления гауссова шума
            denoised = cv2.GaussianBlur(image, (3, 3), 0)
            return denoised
            
        except Exception as e:
            logger.error(f"Ошибка при удалении гауссова шума: {str(e)}")
            return image
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Улучшение контраста"""
        try:
            # CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(image)
            return enhanced
            
        except Exception as e:
            logger.error(f"Ошибка при улучшении контраста: {str(e)}")
            return image
    
    def _apply_morphological_operations(self, image: np.ndarray) -> np.ndarray:
        """Применение морфологических операций"""
        try:
            # Создание структурного элемента
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            
            # Закрытие (заполнение небольших отверстий)
            closed = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
            
            # Открытие (удаление небольших объектов)
            opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel)
            
            return opened
            
        except Exception as e:
            logger.error(f"Ошибка при применении морфологических операций: {str(e)}")
            return image
    
    def _adaptive_binarization(self, image: np.ndarray) -> np.ndarray:
        """Адаптивная бинаризация"""
        try:
            # Адаптивная бинаризация с гауссовым окном
            binary = cv2.adaptiveThreshold(
                image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            return binary
            
        except Exception as e:
            logger.error(f"Ошибка при адаптивной бинаризации: {str(e)}")
            return image
    
    def detect_noise_level(self, image_data: bytes) -> float:
        """
        Определение уровня шума в изображении
        
        Args:
            image_data: Байты изображения
            
        Returns:
            Уровень шума (0-1, где 1 - максимальный шум)
        """
        try:
            image = self._bytes_to_image(image_data)
            
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Расчет вариации (стандартного отклонения) как меры шума
            noise_level = np.std(gray) / 255.0
            
            return min(noise_level, 1.0)
            
        except Exception as e:
            logger.error(f"Ошибка при определении уровня шума: {str(e)}")
            return 0.0
    
    def apply_specific_noise_reduction(self, image_data: bytes, 
                                     noise_type: str = "auto") -> bytes:
        """
        Применение специфичного метода снижения шума
        
        Args:
            image_data: Байты изображения
            noise_type: Тип шума ("gaussian", "salt_pepper", "auto")
            
        Returns:
            Байты обработанного изображения
        """
        try:
            image = self._bytes_to_image(image_data)
            
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            if noise_type == "gaussian":
                denoised = self._remove_gaussian_noise(gray)
            elif noise_type == "salt_pepper":
                denoised = self._remove_salt_pepper_noise(gray)
            else:  # auto
                denoised = self._apply_noise_reduction(image)
            
            # Конвертация обратно в байты
            cleaned_bytes = self._image_to_bytes(denoised)
            
            return cleaned_bytes
            
        except Exception as e:
            logger.error(f"Ошибка при применении специфичного снижения шума: {str(e)}")
            return image_data
    
    def enhance_text_quality(self, image_data: bytes) -> bytes:
        """
        Улучшение качества текста в изображении
        
        Args:
            image_data: Байты изображения
            
        Returns:
            Байты улучшенного изображения
        """
        try:
            image = self._bytes_to_image(image_data)
            
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # 1. Улучшение резкости
            sharpened = self._sharpen_image(gray)
            
            # 2. Улучшение контраста
            enhanced = self._enhance_contrast(sharpened)
            
            # 3. Бинаризация
            binary = self._adaptive_binarization(enhanced)
            
            # 4. Удаление артефактов
            cleaned = self._remove_artifacts(binary)
            
            # Конвертация обратно в байты
            enhanced_bytes = self._image_to_bytes(cleaned)
            
            return enhanced_bytes
            
        except Exception as e:
            logger.error(f"Ошибка при улучшении качества текста: {str(e)}")
            return image_data
    
    def _sharpen_image(self, image: np.ndarray) -> np.ndarray:
        """Улучшение резкости изображения"""
        try:
            # Ядро для улучшения резкости
            kernel = np.array([[-1, -1, -1],
                              [-1,  9, -1],
                              [-1, -1, -1]])
            
            sharpened = cv2.filter2D(image, -1, kernel)
            
            # Нормализация значений
            sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
            
            return sharpened
            
        except Exception as e:
            logger.error(f"Ошибка при улучшении резкости: {str(e)}")
            return image
    
    def _remove_artifacts(self, image: np.ndarray) -> np.ndarray:
        """Удаление артефактов"""
        try:
            # Удаление небольших связанных компонентов
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(image, connectivity=8)
            
            # Фильтрация компонентов по размеру
            min_size = 10  # Минимальный размер компонента
            cleaned = np.zeros_like(image)
            
            for i in range(1, num_labels):  # Пропускаем фон (label 0)
                if stats[i, cv2.CC_STAT_AREA] >= min_size:
                    cleaned[labels == i] = 255
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Ошибка при удалении артефактов: {str(e)}")
            return image
    
    def get_noise_statistics(self, image_data: bytes) -> dict:
        """
        Получение статистики шума в изображении
        
        Args:
            image_data: Байты изображения
            
        Returns:
            Словарь со статистикой шума
        """
        try:
            image = self._bytes_to_image(image_data)
            
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Расчет различных метрик шума
            noise_level = np.std(gray) / 255.0
            mean_intensity = np.mean(gray) / 255.0
            contrast = np.std(gray) / np.mean(gray) if np.mean(gray) > 0 else 0
            
            return {
                'noise_level': noise_level,
                'mean_intensity': mean_intensity,
                'contrast': contrast,
                'image_size': gray.shape,
                'total_pixels': gray.size
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики шума: {str(e)}")
            return {}
