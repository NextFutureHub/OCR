from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import json
import logging
import os

from ocr_service import OCRService
from metrics_calculator import MetricsCalculator
from data_extractor import DataExtractor
from noise_handler import NoiseHandler
from pdf_processor import PDFProcessor

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="OCR Quality Assessment API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация сервисов
ocr_service = OCRService()
metrics_calculator = MetricsCalculator()
data_extractor = DataExtractor()
noise_handler = NoiseHandler()
pdf_processor = PDFProcessor()

class OCRRequest(BaseModel):
    image_path: Optional[str] = None
    ground_truth: Optional[str] = None
    expected_fields: Optional[List[str]] = None
    schema: Optional[Dict[str, Any]] = None

class OCRResponse(BaseModel):
    extracted_text: str
    structured_data: Dict[str, Any]
    metrics: Dict[str, float]
    json_validity: bool
    schema_consistency: bool
    processing_time: float

@app.post("/ocr/process", response_model=OCRResponse)
async def process_document(
    file: UploadFile = File(...),
    ground_truth: Optional[str] = None,
    expected_fields: Optional[str] = None,
    schema: Optional[str] = None
):
    """
    Обработка документа с OCR и оценкой качества
    """
    try:
        import time
        start_time = time.time()
        
        # Валидация файла
        if not file.filename:
            raise HTTPException(status_code=400, detail="Файл не выбран")
        
        # Проверка типа файла
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.pdf'}
        file_extension = os.path.splitext(file.filename.lower())[1]
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Неподдерживаемый формат файла. Разрешены: {allowed_extensions}")
        
        # Чтение изображения
        image_data = await file.read()
        
        # Проверка размера файла
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="Пустой файл")
        
        if len(image_data) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="Файл слишком большой (максимум 10MB)")
        
        # Обработка параметров
        expected_fields_list = json.loads(expected_fields) if expected_fields else None
        schema_dict = json.loads(schema) if schema else None
        
        # Определяем тип файла и обрабатываем соответственно
        if file_extension == '.pdf':
            # Обработка PDF файла
            extracted_text = pdf_processor.extract_text_from_pdf(image_data)
            logger.info(f"Обработан PDF файл: {file.filename}")
        else:
            # Обработка изображения
            extracted_text = ocr_service.extract_text(image_data)
            logger.info(f"Обработано изображение: {file.filename}")
        
        # Извлечение структурированных данных
        structured_data = data_extractor.extract_fields(extracted_text, expected_fields_list)
        
        # Расчет метрик
        metrics = {}
        if ground_truth:
            metrics = metrics_calculator.calculate_all_metrics(extracted_text, ground_truth)
        
        # Проверка JSON валидности
        json_validity = data_extractor.validate_json(structured_data)
        
        # Проверка соответствия схеме
        schema_consistency = data_extractor.validate_schema(structured_data, schema_dict) if schema_dict else True
        
        processing_time = time.time() - start_time
        
        return OCRResponse(
            extracted_text=extracted_text,
            structured_data=structured_data,
            metrics=metrics,
            json_validity=json_validity,
            schema_consistency=schema_consistency,
            processing_time=processing_time
        )
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Ошибка при обработке документа: {str(e)}")
        logger.error(f"Детали ошибки: {error_details}")
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")

@app.post("/ocr/batch-process")
async def batch_process_documents(files: List[UploadFile] = File(...)):
    """
    Пакетная обработка документов
    """
    results = []
    
    for file in files:
        try:
            result = await process_document(file)
            results.append({
                "filename": file.filename,
                "result": result.dict()
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {"results": results}

@app.post("/metrics/calculate")
async def calculate_metrics(
    extracted_text: str,
    ground_truth: str,
    expected_fields: Optional[List[str]] = None
):
    """
    Расчет метрик качества OCR
    """
    try:
        metrics = metrics_calculator.calculate_all_metrics(extracted_text, ground_truth)
        
        if expected_fields:
            field_metrics = {}
            for field in expected_fields:
                field_metrics[field] = metrics_calculator.calculate_field_metrics(
                    extracted_text, ground_truth, field
                )
            metrics["field_metrics"] = field_metrics
        
        return metrics
        
    except Exception as e:
        logger.error(f"Ошибка при расчете метрик: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/noise/process")
async def process_noisy_document(
    file: UploadFile = File(...),
    ground_truth: Optional[str] = None
):
    """
    Обработка зашумленного документа
    """
    try:
        image_data = await file.read()
        
        # Предобработка для удаления шума
        cleaned_image = noise_handler.clean_image(image_data)
        
        # OCR обработка
        extracted_text = ocr_service.extract_text(cleaned_image)
        
        # Расчет метрик для зашумленного документа
        metrics = {}
        if ground_truth:
            metrics = metrics_calculator.calculate_noise_metrics(extracted_text, ground_truth)
        
        return {
            "extracted_text": extracted_text,
            "metrics": metrics,
            "noise_removed": True
        }
        
    except Exception as e:
        logger.error(f"Ошибка при обработке зашумленного документа: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pdf/process")
async def process_pdf_document(
    file: UploadFile = File(...),
    ground_truth: Optional[str] = None,
    expected_fields: Optional[str] = None,
    schema: Optional[str] = None
):
    """
    Обработка PDF документа
    """
    try:
        import time
        start_time = time.time()
        
        # Валидация файла
        if not file.filename:
            raise HTTPException(status_code=400, detail="Файл не выбран")
        
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Файл должен быть PDF")
        
        # Чтение PDF
        pdf_data = await file.read()
        
        if len(pdf_data) == 0:
            raise HTTPException(status_code=400, detail="Пустой файл")
        
        if len(pdf_data) > 50 * 1024 * 1024:  # 50MB для PDF
            raise HTTPException(status_code=400, detail="PDF файл слишком большой (максимум 50MB)")
        
        # Обработка параметров
        expected_fields_list = json.loads(expected_fields) if expected_fields else None
        schema_dict = json.loads(schema) if schema else None
        
        # Извлечение текста из PDF
        extracted_text = pdf_processor.extract_text_from_pdf(pdf_data)
        
        # Получение информации о PDF
        pdf_info = pdf_processor.get_pdf_info(pdf_data)
        
        # Извлечение структурированных данных
        structured_data = data_extractor.extract_fields(extracted_text, expected_fields_list)
        
        # Расчет метрик
        metrics = {}
        if ground_truth:
            metrics = metrics_calculator.calculate_all_metrics(extracted_text, ground_truth)
        
        # Проверка JSON валидности
        json_validity = data_extractor.validate_json(structured_data)
        
        # Проверка соответствия схеме
        schema_consistency = data_extractor.validate_schema(structured_data, schema_dict) if schema_dict else True
        
        processing_time = time.time() - start_time
        
        return {
            "extracted_text": extracted_text,
            "structured_data": structured_data,
            "metrics": metrics,
            "json_validity": json_validity,
            "schema_consistency": schema_consistency,
            "processing_time": processing_time,
            "pdf_info": pdf_info,
            "file_type": "PDF"
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Ошибка при обработке PDF: {str(e)}")
        logger.error(f"Детали ошибки: {error_details}")
        raise HTTPException(status_code=500, detail=f"Ошибка обработки PDF: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Проверка состояния сервиса
    """
    return {"status": "healthy", "service": "OCR Quality Assessment API"}

@app.post("/test/ocr")
async def test_ocr():
    """
    Тестовый endpoint для проверки OCR без файла
    """
    try:
        # Создаем тестовое изображение с текстом
        import numpy as np
        import cv2
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Создаем простое изображение с текстом
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Пытаемся использовать системный шрифт
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        draw.text((10, 30), "Тестовый текст для OCR", fill='black', font=font)
        
        # Конвертируем в байты
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Обрабатываем через OCR
        extracted_text = ocr_service.extract_text(img_byte_arr)
        
        return {
            "status": "success",
            "extracted_text": extracted_text,
            "message": "OCR тест выполнен успешно"
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Ошибка в тестовом OCR: {str(e)}")
        logger.error(f"Детали ошибки: {error_details}")
        return {
            "status": "error",
            "error": str(e),
            "details": error_details
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
