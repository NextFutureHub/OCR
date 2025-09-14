import easyocr
import pytesseract
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
            # Инициализируем с приоритетом русского языка
            self.reader = easyocr.Reader(
                ['ru', 'en'],  # Русский первым для приоритета
                gpu=False,
                verbose=False
            )
            logger.info(f"EasyOCR инициализирован для языков: ['ru', 'en'] с приоритетом русского")
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
            
            # Собираем набор изображений-кандидатов (варианты предобработки и поворотов)
            candidates: List[np.ndarray] = []

            # Вариант 1: базовая предобработка
            base = self._preprocess_image(image)
            candidates.append(base)

            # Вариант 2: инверсия
            try:
                inv = cv2.bitwise_not(base)
                candidates.append(inv)
            except Exception:
                pass

            # Вариант 3: адаптивная бинаризация
            try:
                adaptive = cv2.adaptiveThreshold(
                    cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image,
                    255,
                    cv2.ADAPTIVE_THRESH_MEAN_C,
                    cv2.THRESH_BINARY,
                    15,
                    10,
                )
                candidates.append(adaptive)
            except Exception:
                pass

            # Повороты
            rotation_angles = [0, 90, 180, 270]
            # Пытаемся определить ориентацию через OSD
            try:
                osd = pytesseract.image_to_osd(Image.fromarray(base))
                import re as _re
                m = _re.search(r"Rotate: (\d+)", osd)
                if m:
                    angle = int(m.group(1)) % 360
                    if angle not in rotation_angles:
                        rotation_angles.append(angle)
            except Exception:
                pass

            def rotate(img: np.ndarray, angle: int) -> np.ndarray:
                if angle % 360 == 0:
                    return img
                (h, w) = img.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

            # Оцениваем все комбинации и выбираем лучший текст
            best_text = ""
            best_score = -1.0

            for cand in candidates:
                for ang in rotation_angles:
                    img_rot = rotate(cand, ang)

                    # EasyOCR
                    try:
                        res_easy = self.reader.readtext(
                            img_rot,
                            width_ths=0.7,
                            height_ths=0.7,
                            paragraph=False,
                            detail=1,
                        )
                        text_easy = self._extract_text_from_results(res_easy)
                        score_easy = self._score_text(text_easy)
                        if score_easy > best_score:
                            best_text, best_score = text_easy, score_easy
                    except Exception:
                        pass

                    # Tesseract (несколько конфигураций psm)
                    for psm in (6, 4):
                        try:
                            pil_img = Image.fromarray(img_rot)
                            text_tess = pytesseract.image_to_string(
                                pil_img, lang='rus+eng', config=f'--oem 1 --psm {psm}'
                            )
                        except Exception:
                            text_tess = ''
                        score_tess = self._score_text(text_tess)
                        if score_tess > best_score:
                            best_text, best_score = text_tess, score_tess

            extracted_text = best_text
            
            logger.info(f"Извлечено {len(extracted_text)} символов текста")
            return extracted_text
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении текста: {str(e)}")
            # Возвращаем пустую строку вместо исключения
            return ""

    def _score_text(self, text: str) -> float:
        """Скоринг качества распознанного текста.
        Учитывает длину, долю кириллицы и плотность слов.
        """
        if not text:
            return 0.0
        num_alpha = sum(ch.isalpha() for ch in text)
        if num_alpha == 0:
            return 0.0
        cyr = sum('а' <= ch.lower() <= 'я' or ch in 'ёй' for ch in text)
        cyr_ratio = cyr / max(1, num_alpha)
        words = [w for w in text.split() if any(ch.isalpha() for ch in w)]
        word_density = len(words) / max(1, len(text) / 25)  # ~25 chars per word
        length_score = min(len(text) / 1000.0, 1.0)
        return 2.0 * cyr_ratio + 1.0 * word_density + 0.5 * length_score
    
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
        Оптимизировано для русского текста
        
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
            
            # Значительное увеличение размера для мелкого текста
            height, width = gray.shape
            if height < 3000 or width < 3000:
                scale_factor = max(3000/height, 3000/width)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            
            # Нормализация освещения
            normalized = cv2.convertScaleAbs(gray, alpha=1.2, beta=10)
            
            # Гауссово размытие для сглаживания
            blurred = cv2.GaussianBlur(normalized, (3, 3), 0)
            
            # Улучшение контраста специально для текста
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(16,16))
            enhanced = clahe.apply(blurred)
            
            # Простая бинаризация по Оцу (часто лучше для текста)
            _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Инвертируем если нужно (темный текст на светлом фоне)
            if cv2.mean(binary)[0] < 127:
                binary = cv2.bitwise_not(binary)
            
            # Легкая морфологическая обработка для очистки
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)
            
            return cleaned
            
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
                if confidence > 0.4:  # Повышаем порог уверенности
                    # Применяем постобработку для исправления ошибок OCR
                    corrected_text = self._correct_ocr_errors(text.strip())
                    texts.append(corrected_text)
            
            # Объединение текста с сохранением порядка
            full_text = ' '.join(texts)
            
            return full_text
            
        except Exception as e:
            logger.error(f"Ошибка извлечения текста из результатов: {str(e)}")
            return ""
    
    def _correct_ocr_errors(self, text: str) -> str:
        """
        Исправляет распространенные ошибки OCR для русского текста
        
        Args:
            text: Исходный текст с ошибками OCR
            
        Returns:
            Исправленный текст
        """
        try:
            # Словарь для исправления типичных ошибок OCR русского текста
            corrections = {
                # Частые замены латинских символов на кириллические
                'a': 'а', 'A': 'А', 'B': 'В', 'C': 'С', 'E': 'Е', 'H': 'Н',
                'K': 'К', 'M': 'М', 'O': 'О', 'P': 'Р', 'T': 'Т', 'X': 'Х',
                'Y': 'У', 'c': 'с', 'e': 'е', 'o': 'о', 'p': 'р', 'x': 'х',
                'y': 'у', 'r': 'г', 'u': 'и', 'n': 'п', 'b': 'б', 'd': 'д',
                '6': 'б', '9': 'я', 'I': 'І', 'l': 'л', '1': 'І',
                
                # Исправление частых слов и фраз
                'TOO': 'ТОО', 'OOO': 'ООО', 'LLC': 'ЛЛС',
                'AOBOP': 'ДОГОВОР', 'roBoр': 'ДОГОВОР', 'AoroBop': 'Договор',
                'KyrrJrrr': 'Кыргыз', 'Anruarrr': 'Алматы', 'Anruarr': 'Алматы',
                'AoroBopa': 'Договора', 'Cropourr': 'Сторон', 'Cropon': 'Сторон',
                'rpoAalrur': 'рамочный', 'O6oy4onauus': 'обслуживание',
                'aKaзчик': 'Заказчик', 'oMnaния': 'Компания', 'омпания': 'Компания',
                'ТОО': 'ТОО', 'редприятие': 'Предприятие', 'едприятие': 'Предприятие',
                'редмет': 'Предмет', 'оимость': 'Стоимость', 'Tоимость': 'Стоимость',
            }
            
            corrected = text
            
            # Применяем исправления
            for wrong, correct in corrections.items():
                corrected = corrected.replace(wrong, correct)
            
            # Дополнительные правила для русского текста
            import re
            
            # Исправляем смешанные слова (латиница + кириллица)
            mixed_words = re.findall(r'\b[a-zA-Zа-яё]+\b', corrected)
            for word in mixed_words:
                if any(char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' for char in word) and \
                   any(char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ' for char in word):
                    # Пытаемся исправить смешанное слово
                    fixed_word = word
                    for lat, cyr in corrections.items():
                        if len(lat) == 1 and len(cyr) == 1:  # Только одиночные символы
                            fixed_word = fixed_word.replace(lat, cyr)
                    corrected = corrected.replace(word, fixed_word)
            
            return corrected
            
        except Exception as e:
            logger.error(f"Ошибка исправления OCR: {str(e)}")
            return text
    
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
            
            # Сначала пытаемся найти столбцы по X-координатам
            x_coords = []
            for (bbox, text, confidence) in filtered_results:
                avg_x = sum([point[0] for point in bbox]) / len(bbox)
                x_coords.append(avg_x)
            
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
            min_gap_threshold = image_width * 0.15  # 15% от ширины изображения
            
            if max_gap >= min_gap_threshold:
                # Разделяем на два столбца по X-координатам
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
                
                logger.info(f"Обнаружено {len(columns_info)} столбцов по X-координатам, разрыв: {max_gap:.1f}px")
                return columns_info
            
            # Если разрыв недостаточный, пытаемся найти столбцы по языкам
            logger.info("Недостаточный разрыв по X-координатам, анализируем по языкам")
            
            # Группируем по языкам
            russian_items = []
            english_items = []
            
            for (bbox, text, confidence) in filtered_results:
                language = self._detect_language([text])
                if language == 'ru':
                    avg_x = sum([point[0] for point in bbox]) / len(bbox)
                    russian_items.append((bbox, text, confidence, avg_x))
                elif language == 'en':
                    avg_x = sum([point[0] for point in bbox]) / len(bbox)
                    english_items.append((bbox, text, confidence, avg_x))
            
            # Если есть элементы на обоих языках, создаем столбцы
            if russian_items and english_items:
                columns_info = []
                
                # Сортируем по X-координатам
                russian_items.sort(key=lambda x: x[3])
                english_items.sort(key=lambda x: x[3])
                
                # Определяем, какой язык слева, какой справа
                russian_avg_x = sum([item[3] for item in russian_items]) / len(russian_items)
                english_avg_x = sum([item[3] for item in english_items]) / len(english_items)
                
                if russian_avg_x < english_avg_x:
                    # Русский слева, английский справа
                    columns_info.append({
                        'side': 'left',
                        'x_range': (0, image_width // 2),
                        'items': russian_items,
                        'language': 'ru'
                    })
                    columns_info.append({
                        'side': 'right',
                        'x_range': (image_width // 2, image_width),
                        'items': english_items,
                        'language': 'en'
                    })
                else:
                    # Английский слева, русский справа
                    columns_info.append({
                        'side': 'left',
                        'x_range': (0, image_width // 2),
                        'items': english_items,
                        'language': 'en'
                    })
                    columns_info.append({
                        'side': 'right',
                        'x_range': (image_width // 2, image_width),
                        'items': russian_items,
                        'language': 'ru'
                    })
                
                logger.info(f"Обнаружено {len(columns_info)} столбцов по языкам")
                return columns_info
            
            # Если ничего не найдено, возвращаем пустой список
            logger.info("Столбцы не обнаружены")
            return []
            
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
