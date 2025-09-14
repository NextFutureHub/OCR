#!/usr/bin/env python3
"""
Скрипт для запуска OCR Quality Assessment API сервера
"""

import uvicorn
import logging
import sys
import os
from config import Config

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ocr_api.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Основная функция запуска сервера"""
    try:
        logger.info(f"Запуск {Config.APP_NAME} v{Config.APP_VERSION}")
        logger.info(f"Сервер будет доступен по адресу: http://{Config.HOST}:{Config.PORT}")
        logger.info(f"Режим отладки: {Config.DEBUG}")
        logger.info(f"Языки OCR: {Config.OCR_LANGUAGES}")
        logger.info(f"GPU для OCR: {Config.OCR_GPU_ENABLED}")
        
        # Запуск сервера
        uvicorn.run(
            "main:app",
            host=Config.HOST,
            port=Config.PORT,
            reload=Config.DEBUG,
            workers=1,  # Используем только 1 воркер для Windows
            log_level=Config.LOG_LEVEL.lower(),
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания, остановка сервера...")
    except Exception as e:
        logger.error(f"Ошибка при запуске сервера: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
