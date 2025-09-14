import io
import logging
from typing import List, Optional, Dict, Any
from PIL import Image
import PyPDF2
from pdf2image import convert_from_bytes
import numpy as np
import cv2

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        """Инициализация процессора PDF"""
        pass
    
    def extract_text_from_pdf(self, pdf_data: bytes) -> str:
        """
        Извлечение текста из PDF файла
        
        Args:
            pdf_data: Байты PDF файла
            
        Returns:
            Извлеченный текст
        """
        try:
            # Сначала пытаемся извлечь текст напрямую из PDF
            text = self._extract_text_direct(pdf_data)
            
            if text and len(text.strip()) > 10:  # Если текста достаточно
                logger.info(f"Извлечено {len(text)} символов текста из PDF")
                return text
            else:
                # Если текста мало, конвертируем в изображения и используем OCR
                logger.info("Мало текста в PDF, конвертируем в изображения для OCR")
                return self._extract_text_via_ocr(pdf_data)
                
        except Exception as e:
            logger.error(f"Ошибка при извлечении текста из PDF: {str(e)}")
            return ""
    
    def extract_text_with_pages_and_columns(self, pdf_data: bytes) -> dict:
        """
        Извлечение текста из PDF с анализом страниц и столбцов
        
        Args:
            pdf_data: Байты PDF файла
            
        Returns:
            Словарь с текстом, страницами и столбцами
        """
        try:
            # Получаем информацию о PDF
            pdf_info = self.get_pdf_info(pdf_data)
            
            # Сначала пытаемся извлечь текст напрямую из PDF
            direct_text = self._extract_text_direct(pdf_data)
            
            if direct_text and len(direct_text.strip()) > 10:
                logger.info(f"Извлечен текст напрямую из PDF: {len(direct_text)} символов")
                
                # Анализируем столбцы в тексте
                columns_analysis = self._analyze_text_columns(direct_text)
                
                return {
                    'full_text': direct_text,
                    'pages': [{
                        'page_number': 1,
                        'text': direct_text,
                        'columns': columns_analysis['columns'],
                        'columns_count': columns_analysis['columns_count'],
                        'has_multiple_columns': columns_analysis['has_multiple_columns']
                    }],
                    'total_pages': 1,
                    'has_multiple_columns': columns_analysis['has_multiple_columns'],
                    'pdf_info': pdf_info
                }
            
            # Если прямого извлечения недостаточно, пытаемся конвертировать в изображения
            logger.info("Прямое извлечение текста недостаточно, конвертируем в изображения")
            images = self.convert_pdf_to_images(pdf_data)
            
            if not images:
                logger.warning("Не удалось конвертировать PDF в изображения, используем прямое извлечение")
                return {
                    'full_text': direct_text or '',
                    'pages': [{
                        'page_number': 1,
                        'text': direct_text or '',
                        'columns': [],
                        'columns_count': 0,
                        'has_multiple_columns': False
                    }],
                    'total_pages': 1,
                    'has_multiple_columns': False,
                    'pdf_info': pdf_info
                }
            
            # Импортируем OCR сервис
            from ocr_service import OCRService
            ocr_service = OCRService()
            
            pages_data = []
            all_text = ""
            has_multiple_columns = False
            
            for i, image in enumerate(images):
                logger.info(f"Обработка страницы {i+1} из {len(images)}")
                
                # Конвертируем numpy array в байты
                img_byte_arr = io.BytesIO()
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                pil_image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # Обрабатываем через OCR с анализом столбцов
                page_result = ocr_service.extract_text_with_columns(img_byte_arr)
                
                page_data = {
                    'page_number': i + 1,
                    'text': page_result['full_text'],
                    'columns': page_result['columns'],
                    'columns_count': page_result['columns_count'],
                    'has_multiple_columns': page_result['has_multiple_columns']
                }
                
                pages_data.append(page_data)
                all_text += page_result['full_text'] + "\n"
                
                if page_result['has_multiple_columns']:
                    has_multiple_columns = True
            
            return {
                'full_text': all_text.strip(),
                'pages': pages_data,
                'total_pages': len(pages_data),
                'has_multiple_columns': has_multiple_columns,
                'pdf_info': pdf_info
            }
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении текста с анализом страниц и столбцов: {str(e)}")
            # В случае ошибки, пытаемся хотя бы извлечь текст напрямую
            try:
                direct_text = self._extract_text_direct(pdf_data)
                return {
                    'full_text': direct_text or '',
                    'pages': [{
                        'page_number': 1,
                        'text': direct_text or '',
                        'columns': [],
                        'columns_count': 0,
                        'has_multiple_columns': False
                    }],
                    'total_pages': 1,
                    'has_multiple_columns': False,
                    'pdf_info': {'pages': 1}
                }
            except:
                return {
                    'full_text': '',
                    'pages': [],
                    'total_pages': 0,
                    'has_multiple_columns': False
                }
    
    def _extract_text_direct(self, pdf_data: bytes) -> str:
        """Прямое извлечение текста из PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_data))
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Ошибка при прямом извлечении текста: {str(e)}")
            return ""
    
    def _extract_text_via_ocr(self, pdf_data: bytes) -> str:
        """Извлечение текста через OCR после конвертации в изображения"""
        try:
            # Конвертируем PDF в изображения
            images = convert_from_bytes(pdf_data, dpi=300)
            
            if not images:
                logger.warning("Не удалось конвертировать PDF в изображения")
                return ""
            
            # Импортируем OCR сервис
            from ocr_service import OCRService
            ocr_service = OCRService()
            
            all_text = ""
            
            for i, image in enumerate(images):
                logger.info(f"Обработка страницы {i+1} из {len(images)}")
                
                # Конвертируем PIL изображение в байты
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # Обрабатываем через OCR
                page_text = ocr_service.extract_text(img_byte_arr)
                
                if page_text:
                    all_text += page_text + "\n"
            
            return all_text.strip()
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении текста через OCR: {str(e)}")
            return ""
    
    def get_pdf_info(self, pdf_data: bytes) -> dict:
        """
        Получение информации о PDF файле
        
        Args:
            pdf_data: Байты PDF файла
            
        Returns:
            Словарь с информацией о PDF
        """
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_data))
            
            info = {
                "pages": len(pdf_reader.pages),
                "title": "",
                "author": "",
                "subject": "",
                "creator": "",
                "producer": ""
            }
            
            # Получаем метаданные
            if pdf_reader.metadata:
                metadata = pdf_reader.metadata
                info["title"] = metadata.get("/Title", "")
                info["author"] = metadata.get("/Author", "")
                info["subject"] = metadata.get("/Subject", "")
                info["creator"] = metadata.get("/Creator", "")
                info["producer"] = metadata.get("/Producer", "")
            
            return info
            
        except Exception as e:
            logger.error(f"Ошибка при получении информации о PDF: {str(e)}")
            return {"pages": 0}
    
    def convert_pdf_to_images(self, pdf_data: bytes, dpi: int = 300) -> List[np.ndarray]:
        """
        Конвертация PDF в изображения
        
        Args:
            pdf_data: Байты PDF файла
            dpi: Разрешение изображений
            
        Returns:
            Список изображений в формате numpy array
        """
        try:
            # Конвертируем PDF в PIL изображения
            pil_images = convert_from_bytes(pdf_data, dpi=dpi)
            
            # Конвертируем в numpy arrays
            images = []
            for pil_image in pil_images:
                # Конвертируем PIL в numpy array
                img_array = np.array(pil_image)
                
                # Конвертируем RGB в BGR для OpenCV
                if len(img_array.shape) == 3:
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                images.append(img_array)
            
            return images
            
        except Exception as e:
            logger.error(f"Ошибка при конвертации PDF в изображения: {str(e)}")
            return []
    
    def _analyze_text_columns(self, text: str) -> dict:
        """
        Анализ столбцов в тексте на основе языковых паттернов
        
        Args:
            text: Текст для анализа
            
        Returns:
            Словарь с информацией о столбцов
        """
        try:
            # Подсчитываем общее количество кириллических и латинских символов
            cyrillic_chars = sum(1 for char in text if 'а' <= char.lower() <= 'я' or char in 'ёйцукенгшщзхъфывапролджэячсмитьбю')
            latin_chars = sum(1 for char in text if 'a' <= char.lower() <= 'z')
            
            logger.info(f"Анализ текста: кириллических символов {cyrillic_chars}, латинских символов {latin_chars}, общая длина {len(text)}")
            
            # ОЧЕНЬ СТРОГИЙ ПОДХОД: НЕ создаем столбцы, если нет АБСОЛЮТНО четких признаков
            
            # Проверяем только ЯВНЫЕ случаи двуязычных документов
            if self._is_clear_side_by_side_document(text):
                logger.info("Обнаружен документ с четкими параллельными столбцами")
                return self._create_side_by_side_columns(text)
            
            # Во всех остальных случаях - НЕ создаем столбцы
            logger.info("Документ не является двустолбцовым, оставляем как единый текст")
            return {
                'columns': [],
                'columns_count': 0,
                'has_multiple_columns': False
            }
            
        except Exception as e:
            logger.error(f"Ошибка анализа столбцов в тексте: {str(e)}")
            return {
                'columns': [],
                'columns_count': 0,
                'has_multiple_columns': False
            }
    
    def _is_clear_side_by_side_document(self, text: str) -> bool:
        """
        Проверяет, является ли документ четким двустолбцовым документом
        
        Args:
            text: Текст для анализа
            
        Returns:
            True только если документ ТОЧНО имеет два столбца
        """
        try:
            lines = text.split('\n')
            if len(lines) < 10:  # Слишком мало строк
                return False
            
            # Ищем строки с явными переводами (одинаковые номера, даты и т.д.)
            translation_pairs = 0
            
            for i in range(len(lines) - 1):
                line1 = lines[i].strip()
                line2 = lines[i + 1].strip()
                
                if not line1 or not line2:
                    continue
                
                # Проверяем на парные строки с номерами/датами
                if self._are_translation_pair(line1, line2):
                    translation_pairs += 1
            
            # Если найдено достаточно парных переводов - это двустолбцовый документ
            return translation_pairs >= 5  # ОЧЕНЬ строгий критерий
            
        except Exception as e:
            logger.error(f"Ошибка проверки двустолбцового документа: {str(e)}")
            return False
    
    def _are_translation_pair(self, line1: str, line2: str) -> bool:
        """
        Проверяет, являются ли две строки переводом друг друга
        
        Args:
            line1: Первая строка
            line2: Вторая строка
            
        Returns:
            True если строки являются переводом
        """
        try:
            # Проверяем на схожие числа
            import re
            numbers1 = re.findall(r'\d+', line1)
            numbers2 = re.findall(r'\d+', line2)
            
            if numbers1 and numbers2 and numbers1 == numbers2:
                return True
            
            # Проверяем на схожую структуру (пункты, подпункты)
            if (line1.startswith(('1.', '2.', '3.', '4.', '5.')) and 
                line2.startswith(('1.', '2.', '3.', '4.', '5.'))):
                return True
            
            # Проверяем на ключевые слова переводов
            keywords_pairs = [
                ('ДОГОВОР', 'AGREEMENT'),
                ('ИСПОЛНИТЕЛЬ', 'CONTRACTOR'),
                ('ЗАКАЗЧИК', 'CUSTOMER'),
                ('СТОРОНА', 'PARTY'),
                ('УСЛОВИЯ', 'TERMS'),
                ('УСЛУГИ', 'SERVICES')
            ]
            
            for ru_word, en_word in keywords_pairs:
                if ru_word in line1.upper() and en_word in line2.upper():
                    return True
                if en_word in line1.upper() and ru_word in line2.upper():
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка проверки парных строк: {str(e)}")
            return False
    
    def _create_side_by_side_columns(self, text: str) -> dict:
        """
        Создает столбцы для документа с параллельными переводами
        
        Args:
            text: Текст для анализа
            
        Returns:
            Словарь с информацией о столбцах
        """
        try:
            lines = text.split('\n')
            russian_lines = []
            english_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Анализируем язык строки
                cyrillic_count = sum(1 for char in line if 'а' <= char.lower() <= 'я' or char in 'ёйцукенгшщзхъфывапролджэячсмитьбю')
                latin_count = sum(1 for char in line if 'a' <= char.lower() <= 'z')
                
                # Если больше кириллицы - русская строка
                if cyrillic_count > latin_count and cyrillic_count > 0:
                    russian_lines.append(line)
                # Если больше латиницы - английская строка
                elif latin_count > cyrillic_count and latin_count > 0:
                    english_lines.append(line)
            
            if russian_lines and english_lines:
                columns = []
                
                # Русский столбец
                russian_text = '\n'.join(russian_lines)
                columns.append({
                    'text': russian_text,
                    'side': 'left',
                    'language': 'ru',
                    'items_count': len(russian_lines),
                    'confidence_avg': 0.95
                })
                
                # Английский столбец
                english_text = '\n'.join(english_lines)
                columns.append({
                    'text': english_text,
                    'side': 'right',
                    'language': 'en',
                    'items_count': len(english_lines),
                    'confidence_avg': 0.95
                })
                
                logger.info(f"Создано 2 столбца для параллельного документа: русский ({len(russian_text)} символов), английский ({len(english_text)} символов)")
                return {
                    'columns': columns,
                    'columns_count': len(columns),
                    'has_multiple_columns': len(columns) > 1
                }
            
            return {
                'columns': [],
                'columns_count': 0,
                'has_multiple_columns': False
            }
            
        except Exception as e:
            logger.error(f"Ошибка создания параллельных столбцов: {str(e)}")
            return {
                'columns': [],
                'columns_count': 0,
                'has_multiple_columns': False
            }
    
    def _has_clear_bilingual_structure(self, text: str) -> bool:
        """
        Проверяет наличие четкой двуязычной структуры
        
        Args:
            text: Текст для анализа
            
        Returns:
            True если обнаружена четкая двуязычная структура
        """
        try:
            lines = text.split('\n')
            if len(lines) < 6:  # Нужно минимум 6 строк
                return False
            
            # Ищем строки, которые явно являются переводами друг друга
            bilingual_pairs = 0
            
            for i in range(len(lines) - 1):
                line1 = lines[i].strip()
                line2 = lines[i + 1].strip()
                
                if not line1 or not line2:
                    continue
                
                # Анализируем соседние строки
                line1_cyrillic = sum(1 for char in line1 if 'а' <= char.lower() <= 'я' or char in 'ёйцукенгшщзхъфывапролджэячсмитьбю')
                line1_latin = sum(1 for char in line1 if 'a' <= char.lower() <= 'z')
                
                line2_cyrillic = sum(1 for char in line2 if 'а' <= char.lower() <= 'я' or char in 'ёйцукенгшщзхъфывапролджэячсмитьбю')
                line2_latin = sum(1 for char in line2 if 'a' <= char.lower() <= 'z')
                
                # Если одна строка на русском, а следующая на английском
                if (line1_cyrillic > line1_latin and line1_cyrillic > 0 and
                    line2_latin > line2_cyrillic and line2_latin > 0):
                    bilingual_pairs += 1
                elif (line1_latin > line1_cyrillic and line1_latin > 0 and
                      line2_cyrillic > line2_latin and line2_cyrillic > 0):
                    bilingual_pairs += 1
            
            # Если найдено достаточно двуязычных пар, считаем структуру четкой
            return bilingual_pairs >= 3
            
        except Exception as e:
            logger.error(f"Ошибка проверки двуязычной структуры: {str(e)}")
            return False
    
    def _create_bilingual_columns(self, text: str) -> dict:
        """
        Создает столбцы для четкой двуязычной структуры
        
        Args:
            text: Текст для анализа
            
        Returns:
            Словарь с информацией о столбцах
        """
        try:
            lines = text.split('\n')
            russian_lines = []
            english_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Анализируем строку
                line_cyrillic = sum(1 for char in line if 'а' <= char.lower() <= 'я' or char in 'ёйцукенгшщзхъфывапролджэячсмитьбю')
                line_latin = sum(1 for char in line if 'a' <= char.lower() <= 'z')
                
                if line_cyrillic > line_latin and line_cyrillic > 0:
                    russian_lines.append(line)
                elif line_latin > line_cyrillic and line_latin > 0:
                    english_lines.append(line)
            
            if russian_lines and english_lines:
                columns = []
                
                # Русский столбец
                russian_text = '\n'.join(russian_lines)
                columns.append({
                    'text': russian_text,
                    'side': 'left',
                    'language': 'ru',
                    'items_count': len(russian_lines),
                    'confidence_avg': 0.9
                })
                
                # Английский столбец
                english_text = '\n'.join(english_lines)
                columns.append({
                    'text': english_text,
                    'side': 'right',
                    'language': 'en',
                    'items_count': len(english_lines),
                    'confidence_avg': 0.9
                })
                
                logger.info(f"Создано 2 столбца для двуязычной структуры: русский ({len(russian_text)} символов), английский ({len(english_text)} символов)")
                return {
                    'columns': columns,
                    'columns_count': len(columns),
                    'has_multiple_columns': len(columns) > 1
                }
            
            return {
                'columns': [],
                'columns_count': 0,
                'has_multiple_columns': False
            }
            
        except Exception as e:
            logger.error(f"Ошибка создания двуязычных столбцов: {str(e)}")
            return {
                'columns': [],
                'columns_count': 0,
                'has_multiple_columns': False
            }
    
    def _detect_column_patterns(self, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Обнаружение паттернов столбцов в тексте
        
        Args:
            lines: Список строк текста
            
        Returns:
            Список обнаруженных паттернов столбцов
        """
        try:
            patterns = []
            
            # Ищем строки с повторяющимися паттернами (номера, даты, заголовки)
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                # Проверяем на наличие номеров страниц
                if (line.startswith(('стр.', 'page', 'Стр.', 'Page', 'Page ')) or 
                    line.endswith(('стр.', 'page', 'Стр.', 'Page')) or
                    'Page ' in line and 'of ' in line):
                    
                    patterns.append({
                        'line_number': i,
                        'content': line,
                        'type': 'page_number'
                    })
                
                # Проверяем на заголовки разделов (содержат цифры и точки)
                elif (line.count('.') >= 2 and 
                      any(char.isdigit() for char in line) and 
                      len(line) < 100 and
                      not line.endswith('.')):
                    
                    patterns.append({
                        'line_number': i,
                        'content': line,
                        'type': 'section_header'
                    })
            
            # Если найдено несколько паттернов, возможно есть столбцы
            if len(patterns) >= 3:  # Увеличиваем порог для более точного определения
                return patterns
            
            return []
            
        except Exception as e:
            logger.error(f"Ошибка обнаружения паттернов столбцов: {str(e)}")
            return []
    
    def _create_columns_from_patterns(self, text: str, patterns: List[Dict[str, Any]]) -> dict:
        """
        Создание столбцов на основе обнаруженных паттернов
        
        Args:
            text: Исходный текст
            patterns: Обнаруженные паттерны
            
        Returns:
            Словарь с информацией о столбцах
        """
        try:
            lines = text.split('\n')
            
            if len(patterns) < 2:
                return {
                    'columns': [],
                    'columns_count': 0,
                    'has_multiple_columns': False
                }
            
            # Анализируем распределение паттернов по тексту
            pattern_positions = [p['line_number'] for p in patterns]
            
            # Ищем естественную точку разделения
            # Если паттерны равномерно распределены, используем середину
            if len(pattern_positions) >= 4:
                # Берем среднюю позицию между первым и последним паттерном
                first_pos = pattern_positions[0]
                last_pos = pattern_positions[-1]
                mid_point = (first_pos + last_pos) // 2
            else:
                # Для меньшего количества паттернов используем середину текста
                mid_point = len(lines) // 2
            
            # Разделяем текст
            left_lines = lines[:mid_point]
            right_lines = lines[mid_point:]
            
            left_text = '\n'.join(left_lines).strip()
            right_text = '\n'.join(right_lines).strip()
            
            if not left_text or not right_text:
                return {
                    'columns': [],
                    'columns_count': 0,
                    'has_multiple_columns': False
                }
            
            # Проверяем, что столбцы не слишком отличаются по размеру
            ratio = min(len(left_text), len(right_text)) / max(len(left_text), len(right_text))
            if ratio < 0.3:  # Если размеры отличаются более чем в 3 раза, не создаем столбцы
                logger.info(f"Столбцы слишком отличаются по размеру (ratio: {ratio:.2f}), не создаем")
                return {
                    'columns': [],
                    'columns_count': 0,
                    'has_multiple_columns': False
                }
            
            # Анализируем языки в каждом столбце
            left_cyrillic = sum(1 for char in left_text if 'а' <= char.lower() <= 'я' or char in 'ёйцукенгшщзхъфывапролджэячсмитьбю')
            left_latin = sum(1 for char in left_text if 'a' <= char.lower() <= 'z')
            left_lang = 'ru' if left_cyrillic > left_latin else 'en'
            
            right_cyrillic = sum(1 for char in right_text if 'а' <= char.lower() <= 'я' or char in 'ёйцукенгшщзхъфывапролджэячсмитьбю')
            right_latin = sum(1 for char in right_text if 'a' <= char.lower() <= 'z')
            right_lang = 'ru' if right_cyrillic > right_latin else 'en'
            
            columns = []
            
            # Левый столбец
            columns.append({
                'text': left_text,
                'side': 'left',
                'language': left_lang,
                'items_count': len(left_lines),
                'confidence_avg': 0.8
            })
            
            # Правый столбец
            columns.append({
                'text': right_text,
                'side': 'right',
                'language': right_lang,
                'items_count': len(right_lines),
                'confidence_avg': 0.8
            })
            
            logger.info(f"Создано 2 столбца на основе паттернов: левый ({len(left_text)} символов, {left_lang}), правый ({len(right_text)} символов, {right_lang})")
            return {
                'columns': columns,
                'columns_count': len(columns),
                'has_multiple_columns': len(columns) > 1
            }
            
        except Exception as e:
            logger.error(f"Ошибка создания столбцов из паттернов: {str(e)}")
            return {
                'columns': [],
                'columns_count': 0,
                'has_multiple_columns': False
            }
    
    def _detect_language_split(self, text: str) -> dict:
        """
        Обнаружение разделения текста по языкам
        
        Args:
            text: Исходный текст
            
        Returns:
            Словарь с информацией о столбцах или None
        """
        try:
            # Разбиваем текст на строки для анализа структуры
            lines = text.split('\n')
            if len(lines) < 4:  # Нужно минимум 4 строки для анализа
                return None
            
            # Анализируем каждую строку
            line_analysis = []
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                # Анализируем строку
                line_cyrillic = sum(1 for char in line if 'а' <= char.lower() <= 'я' or char in 'ёйцукенгшщзхъфывапролджэячсмитьбю')
                line_latin = sum(1 for char in line if 'a' <= char.lower() <= 'z')
                
                if line_cyrillic > line_latin and line_cyrillic > 0:
                    line_analysis.append({'line': line, 'language': 'ru', 'index': i})
                elif line_latin > line_cyrillic and line_latin > 0:
                    line_analysis.append({'line': line, 'language': 'en', 'index': i})
                else:
                    line_analysis.append({'line': line, 'language': 'mixed', 'index': i})
            
            # Группируем строки по языкам
            russian_lines = [item['line'] for item in line_analysis if item['language'] == 'ru']
            english_lines = [item['line'] for item in line_analysis if item['language'] == 'en']
            
            logger.info(f"Анализ: русских строк {len(russian_lines)}, английских строк {len(english_lines)}")
            
            # Проверяем, есть ли достаточно строк на обоих языках
            if len(russian_lines) >= 2 and len(english_lines) >= 2:
                # Анализируем чередование языков в исходном порядке
                language_sequence = [item['language'] for item in line_analysis]
                logger.info(f"Последовательность языков: {language_sequence}")
                
                # Ищем паттерн чередования языков
                alternating_pattern = self._detect_alternating_pattern(language_sequence)
                logger.info(f"Чередующийся паттерн: {alternating_pattern}")
                
                if alternating_pattern:
                    # Разделяем строки на два столбца на основе чередования
                    left_lines = []
                    right_lines = []
                    
                    for i, item in enumerate(line_analysis):
                        if i % 2 == 0:  # Четные позиции - левый столбец
                            left_lines.append(item['line'])
                        else:  # Нечетные позиции - правый столбец
                            right_lines.append(item['line'])
                    
                    if left_lines and right_lines:
                        left_text = '\n'.join(left_lines)
                        right_text = '\n'.join(right_lines)
                        
                        # Проверяем, что столбцы не слишком отличаются по размеру
                        ratio = min(len(left_text), len(right_text)) / max(len(left_text), len(right_text))
                        logger.info(f"Соотношение размеров столбцов: {ratio:.2f}")
                        
                        if ratio > 0.2:  # Размеры не отличаются более чем в 5 раз
                            columns = []
                            
                            # Определяем язык каждого столбца
                            left_cyrillic = sum(1 for char in left_text if 'а' <= char.lower() <= 'я' or char in 'ёйцукенгшщзхъфывапролджэячсмитьбю')
                            left_latin = sum(1 for char in left_text if 'a' <= char.lower() <= 'z')
                            left_lang = 'ru' if left_cyrillic > left_latin else 'en'
                            
                            right_cyrillic = sum(1 for char in right_text if 'а' <= char.lower() <= 'я' or char in 'ёйцукенгшщзхъфывапролджэячсмитьбю')
                            right_latin = sum(1 for char in right_text if 'a' <= char.lower() <= 'z')
                            right_lang = 'ru' if right_cyrillic > right_latin else 'en'
                            
                            # Левый столбец
                            columns.append({
                                'text': left_text,
                                'side': 'left',
                                'language': left_lang,
                                'items_count': len(left_lines),
                                'confidence_avg': 0.8
                            })
                            
                            # Правый столбец
                            columns.append({
                                'text': right_text,
                                'side': 'right',
                                'language': right_lang,
                                'items_count': len(right_lines),
                                'confidence_avg': 0.8
                            })
                            
                            logger.info(f"Создано 2 столбца по чередованию языков: левый ({len(left_text)} символов, {left_lang}), правый ({len(right_text)} символов, {right_lang})")
                            return {
                                'columns': columns,
                                'columns_count': len(columns),
                                'has_multiple_columns': len(columns) > 1
                            }
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка обнаружения разделения по языкам: {str(e)}")
            return None
    
    def _detect_alternating_pattern(self, sequence: List[str]) -> bool:
        """
        Обнаружение паттерна чередования языков
        
        Args:
            sequence: Последовательность языков
            
        Returns:
            True если обнаружен паттерн чередования
        """
        try:
            if len(sequence) < 4:
                return False
            
            # Ищем паттерны ru-en-ru-en или en-ru-en-ru
            ru_en_pattern = True
            en_ru_pattern = True
            
            for i in range(len(sequence)):
                if sequence[i] == 'mixed':
                    continue
                    
                if i % 2 == 0:
                    if sequence[i] != 'ru':
                        ru_en_pattern = False
                    if sequence[i] != 'en':
                        en_ru_pattern = False
                else:
                    if sequence[i] != 'en':
                        ru_en_pattern = False
                    if sequence[i] != 'ru':
                        en_ru_pattern = False
            
            return ru_en_pattern or en_ru_pattern
            
        except Exception as e:
            logger.error(f"Ошибка обнаружения паттерна чередования: {str(e)}")
            return False
    
    def _detect_structure_split(self, text: str) -> dict:
        """
        Обнаружение столбцов на основе анализа структуры текста
        
        Args:
            text: Исходный текст
            
        Returns:
            Словарь с информацией о столбцах или None
        """
        try:
            # Разбиваем текст на строки
            lines = text.split('\n')
            if len(lines) < 6:  # Нужно минимум 6 строк для анализа структуры
                return None
            
            # Анализируем длину строк и их содержимое
            line_lengths = [len(line.strip()) for line in lines if line.strip()]
            avg_line_length = sum(line_lengths) / len(line_lengths) if line_lengths else 0
            
            # Ищем строки, которые могут быть разделителями столбцов
            # (короткие строки, содержащие номера, даты, или специальные символы)
            potential_dividers = []
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                # Проверяем на короткие строки с номерами или датами
                if (len(line) < 50 and 
                    (any(char.isdigit() for char in line) or 
                     line.startswith(('№', 'No', 'стр.', 'page', 'Стр.', 'Page')))):
                    potential_dividers.append(i)
            
            # Если найдено несколько потенциальных разделителей, анализируем структуру
            if len(potential_dividers) >= 2:
                # Разделяем текст на части между разделителями
                parts = []
                start = 0
                
                for divider in potential_dividers:
                    if divider > start:
                        part_text = '\n'.join(lines[start:divider]).strip()
                        if part_text:
                            parts.append(part_text)
                    start = divider + 1
                
                # Добавляем последнюю часть
                if start < len(lines):
                    part_text = '\n'.join(lines[start:]).strip()
                    if part_text:
                        parts.append(part_text)
                
                # Если получилось 2 части примерно одинакового размера, создаем столбцы
                if len(parts) == 2:
                    part1_len = len(parts[0])
                    part2_len = len(parts[1])
                    
                    # Проверяем, что части не слишком отличаются по размеру
                    if part1_len > 50 and part2_len > 50:
                        ratio = min(part1_len, part2_len) / max(part1_len, part2_len)
                        if ratio > 0.3:  # Размеры не отличаются более чем в 3 раза
                            columns = []
                            
                            # Левый столбец
                            columns.append({
                                'text': parts[0],
                                'side': 'left',
                                'language': 'ru',
                                'items_count': len(parts[0].split('\n')),
                                'confidence_avg': 0.7
                            })
                            
                            # Правый столбец
                            columns.append({
                                'text': parts[1],
                                'side': 'right',
                                'language': 'ru',
                                'items_count': len(parts[1].split('\n')),
                                'confidence_avg': 0.7
                            })
                            
                            logger.info(f"Создано 2 столбца по структуре: левый ({part1_len} символов), правый ({part2_len} символов)")
                            return {
                                'columns': columns,
                                'columns_count': len(columns),
                                'has_multiple_columns': len(columns) > 1
                            }
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка обнаружения разделения по структуре: {str(e)}")
            return None
    
    def is_pdf_file(self, file_data: bytes, filename: str = "") -> bool:
        """
        Проверка, является ли файл PDF
        
        Args:
            file_data: Байты файла
            filename: Имя файла (опционально)
            
        Returns:
            True если файл является PDF
        """
        try:
            # Проверка по расширению файла
            if filename.lower().endswith('.pdf'):
                return True
            
            # Проверка по магическим байтам
            if file_data.startswith(b'%PDF'):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка при проверке PDF файла: {str(e)}")
            return False
