import os
from typing import List, Dict, Any

class Config:
    """Конфигурация приложения"""
    
    # Основные настройки
    APP_NAME = "OCR Quality Assessment API"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Настройки сервера
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # Настройки OCR
    OCR_LANGUAGES = ["ru", "en"]
    OCR_GPU_ENABLED = os.getenv("OCR_GPU_ENABLED", "False").lower() == "true"
    OCR_MIN_CONFIDENCE = float(os.getenv("OCR_MIN_CONFIDENCE", "0.5"))
    
    # Настройки обработки изображений
    MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", 10 * 1024 * 1024))  # 10MB
    SUPPORTED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "bmp", "tiff"]
    
    # Настройки метрик
    METRICS_PRECISION = int(os.getenv("METRICS_PRECISION", 4))
    
    # Настройки извлечения данных
    DEFAULT_FIELDS = [
        "name", "date", "phone", "email", 
        "address", "passport", "inn", "amount"
    ]
    
    # Настройки обработки шума
    NOISE_REDUCTION_ENABLED = True
    NOISE_DETECTION_THRESHOLD = float(os.getenv("NOISE_DETECTION_THRESHOLD", "0.1"))
    
    # Настройки логирования
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Настройки CORS
    CORS_ORIGINS = ["*"]
    CORS_METHODS = ["*"]
    CORS_HEADERS = ["*"]
    
    # Настройки валидации
    JSON_VALIDATION_ENABLED = True
    SCHEMA_VALIDATION_ENABLED = True
    
    # Настройки производительности
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", 4))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 300))  # 5 минут
    
    # Настройки кэширования
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "False").lower() == "true"
    CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))  # 1 час
    
    @classmethod
    def get_ocr_config(cls) -> Dict[str, Any]:
        """Получение конфигурации OCR"""
        return {
            "languages": cls.OCR_LANGUAGES,
            "gpu": cls.OCR_GPU_ENABLED,
            "min_confidence": cls.OCR_MIN_CONFIDENCE
        }
    
    @classmethod
    def get_processing_config(cls) -> Dict[str, Any]:
        """Получение конфигурации обработки"""
        return {
            "max_image_size": cls.MAX_IMAGE_SIZE,
            "supported_formats": cls.SUPPORTED_IMAGE_FORMATS,
            "noise_reduction": cls.NOISE_REDUCTION_ENABLED,
            "noise_threshold": cls.NOISE_DETECTION_THRESHOLD
        }
    
    @classmethod
    def get_validation_config(cls) -> Dict[str, Any]:
        """Получение конфигурации валидации"""
        return {
            "json_validation": cls.JSON_VALIDATION_ENABLED,
            "schema_validation": cls.SCHEMA_VALIDATION_ENABLED,
            "default_fields": cls.DEFAULT_FIELDS
        }
    
    @classmethod
    def get_server_config(cls) -> Dict[str, Any]:
        """Получение конфигурации сервера"""
        return {
            "host": cls.HOST,
            "port": cls.PORT,
            "debug": cls.DEBUG,
            "max_workers": cls.MAX_WORKERS,
            "request_timeout": cls.REQUEST_TIMEOUT
        }

# Схемы для валидации
DEFAULT_SCHEMAS = {
    "person_document": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "date": {"type": "string", "pattern": r"^\d{1,2}[./]\d{1,2}[./]\d{2,4}$"},
            "phone": {"type": "string", "pattern": r"^[+]?[0-9\s\-\(\)]+$"},
            "email": {"type": "string", "format": "email"}
        },
        "required": ["name"]
    },
    
    "financial_document": {
        "type": "object",
        "properties": {
            "amount": {"type": "string", "pattern": r"^\d+(?:[.,]\d+)?$"},
            "date": {"type": "string", "pattern": r"^\d{1,2}[./]\d{1,2}[./]\d{2,4}$"},
            "inn": {"type": "string", "pattern": r"^\d{10,12}$"}
        },
        "required": ["amount", "date"]
    },
    
    "identity_document": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "passport": {"type": "string", "pattern": r"^\d{4}\s*\d{6}$"},
            "date": {"type": "string", "pattern": r"^\d{1,2}[./]\d{1,2}[./]\d{2,4}$"}
        },
        "required": ["name", "passport"]
    }
}

# Паттерны для извлечения полей
FIELD_PATTERNS = {
    "name": [
        r"(?:имя|name|фио|ф\.и\.о\.?)\s*:?\s*([а-яё\s]+)",
        r"([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)"
    ],
    "date": [
        r"(?:дата|date)\s*:?\s*(\d{1,2}[./]\d{1,2}[./]\d{2,4})",
        r"(\d{1,2}[./]\d{1,2}[./]\d{2,4})"
    ],
    "phone": [
        r"(?:телефон|phone|тел\.?)\s*:?\s*([+]?[0-9\s\-\(\)]+)",
        r"([+]?[0-9\s\-\(\)]{10,})"
    ],
    "email": [
        r"(?:email|почта|e-mail)\s*:?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
        r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
    ],
    "address": [
        r"(?:адрес|address|адр\.?)\s*:?\s*([а-яё\s\d,.-]+)",
        r"(г\.\s*[а-яё\s]+,\s*[а-яё\s\d,.-]+)"
    ],
    "passport": [
        r"(?:паспорт|passport|пасп\.?)\s*:?\s*(\d{4}\s*\d{6})",
        r"(\d{4}\s*\d{6})"
    ],
    "inn": [
        r"(?:инн|inn)\s*:?\s*(\d{10,12})",
        r"(\d{10,12})"
    ],
    "amount": [
        r"(?:сумма|amount|сумм\.?)\s*:?\s*(\d+(?:[.,]\d+)?)",
        r"(\d+(?:[.,]\d+)?\s*(?:руб|р\.?|₽))"
    ]
}

# Настройки обработки шума
NOISE_PROCESSING_CONFIG = {
    "gaussian_blur": {"kernel_size": (3, 3), "sigma": 0},
    "median_blur": {"kernel_size": 3},
    "morphology": {"kernel_size": (2, 2)},
    "adaptive_threshold": {"max_value": 255, "block_size": 11, "c": 2},
    "clahe": {"clip_limit": 2.0, "tile_grid_size": (8, 8)}
}

# Настройки метрик
METRICS_CONFIG = {
    "cer_weight": 0.4,
    "wer_weight": 0.3,
    "levenshtein_weight": 0.3,
    "precision_digits": 4,
    "exact_match_bonus": 0.1
}
