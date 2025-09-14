import io
import logging
from typing import List, Optional
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
                return {
                    'full_text': direct_text,
                    'pages': [{
                        'page_number': 1,
                        'text': direct_text,
                        'columns': [],
                        'columns_count': 0,
                        'has_multiple_columns': False
                    }],
                    'total_pages': 1,
                    'has_multiple_columns': False,
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
