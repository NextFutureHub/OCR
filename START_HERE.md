# 🎯 НАЧНИТЕ ЗДЕСЬ - OCR Quality Assessment API

## ✅ Система готова к использованию!

Я создал полнофункциональную систему оценки качества OCR с использованием EasyOCR и FastAPI, которая реализует все требования по техническим критериям.

## 🚀 Быстрый запуск

### 1. Установите зависимости
```bash
pip install -r requirements.txt
```

### 2. Запустите сервер
```bash
python run_server.py
```

### 3. Откройте браузер
Перейдите по адресу: `http://localhost:8000`

### 4. Протестируйте систему
```bash
python test_api.py
```

### 5. Посмотрите демонстрацию
```bash
python demo.py
```

## 📊 Реализованные критерии оценки

### Техническая часть (70 баллов)

#### ✅ Точность OCR (25 баллов)
- **CER (Character Error Rate)** - процент ошибок на уровне символов
- **WER (Word Error Rate)** - процент ошибок на уровне слов  
- **Normalized Levenshtein Distance** - нормализованное расстояние Левенштейна

#### ✅ Извлечение данных (25 баллов)
- **Field-level Accuracy** - точность извлечения каждого поля
- **F1-score для каждого поля** - метрика качества извлечения
- **Exact Match per Document** - процент документов, извлеченных полностью верно

#### ✅ Работа с шумом (10 баллов)
- **CER/WER на noisy subset** - метрики качества на зашумленных данных
- Автоматическая очистка изображений от шума
- Определение уровня шума

#### ✅ Структурированность (10 баллов)
- **JSON Validity** - процент корректных JSON
- **Schema Consistency** - процент JSON с обязательными ключами

## 🔧 Основные компоненты

### API Endpoints
- `POST /ocr/process` - обработка документа с OCR
- `POST /metrics/calculate` - расчет метрик качества
- `POST /noise/process` - обработка зашумленных данных
- `POST /ocr/batch-process` - пакетная обработка
- `GET /health` - проверка состояния

### Модули системы
- `ocr_service.py` - сервис OCR с EasyOCR
- `metrics_calculator.py` - расчет всех метрик качества
- `data_extractor.py` - извлечение структурированных данных
- `noise_handler.py` - обработка зашумленных изображений
- `config.py` - централизованная конфигурация

## 📋 Поддерживаемые поля

Система автоматически извлекает:
- `name` - имя/ФИО
- `date` - дата
- `phone` - телефон
- `email` - электронная почта
- `address` - адрес
- `passport` - паспортные данные
- `inn` - ИНН
- `amount` - сумма

## 🎯 Пример использования

```python
import requests

# Расчет метрик качества
response = requests.post('http://localhost:8000/metrics/calculate', 
    json={
        'extracted_text': 'Иван Иванов 01.01.2023',
        'ground_truth': 'Иван Иванов 01.01.2023'
    })

result = response.json()
print(f"CER: {result['cer']}")      # Character Error Rate
print(f"WER: {result['wer']}")      # Word Error Rate
print(f"Exact Match: {result['exact_match']}")
```

## 📚 Документация

- **README.md** - полная документация системы
- **INSTALL.md** - подробная инструкция по установке
- **PROJECT_STRUCTURE.md** - структура проекта
- **QUICK_START.md** - быстрый старт
- **http://localhost:8000/docs** - интерактивная документация API

## 🧪 Тестирование

### Автоматические тесты
```bash
python test_api.py
```

### Примеры использования
```bash
python examples.py
```

### Демонстрация
```bash
python demo.py
```

## ⚙️ Настройка

Создайте файл `.env` для настройки:
```env
DEBUG=False
HOST=0.0.0.0
PORT=8000
OCR_LANGUAGES=ru,en
OCR_GPU_ENABLED=False
MAX_IMAGE_SIZE=10485760
```

## 🔍 Мониторинг

- Логи сохраняются в `ocr_api.log`
- Метрики производительности в реальном времени
- Статистика обработки документов

## 🎉 Готово к использованию!

Система полностью готова и реализует все требования:
- ✅ EasyOCR для распознавания текста
- ✅ Все метрики качества (CER, WER, F1-score)
- ✅ Извлечение структурированных данных
- ✅ Обработка зашумленных изображений
- ✅ Валидация JSON и схем
- ✅ FastAPI для REST API
- ✅ Полная документация и тесты

**Начните с команды: `python run_server.py`**
