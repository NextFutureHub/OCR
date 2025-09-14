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
