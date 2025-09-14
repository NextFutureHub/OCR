# OCR Quality Assessment API

Система оценки качества OCR с использованием EasyOCR и FastAPI.

## Возможности

### Техническая часть (70 баллов)

#### Точность OCR (25 баллов)
- **CER (Character Error Rate)** - процент ошибок на уровне символов
- **WER (Word Error Rate)** - процент ошибок на уровне слов  
- **Normalized Levenshtein Distance** - нормализованное расстояние Левенштейна

#### Извлечение данных (25 баллов)
- **Field-level Accuracy** - точность извлечения каждого поля
- **F1-score для каждого поля** - метрика качества извлечения
- **Exact Match per Document** - процент документов, извлеченных полностью верно

#### Работа с шумом (10 баллов)
- **CER/WER на noisy subset** - метрики качества на зашумленных данных
- Автоматическая очистка изображений от шума
- Определение уровня шума

#### Структурированность (10 баллов)
- **JSON Validity** - процент корректных JSON
- **Schema Consistency** - процент JSON с обязательными ключами

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите сервер:
```bash
python main.py
```

API будет доступен по адресу: `http://localhost:8000`

## Использование

### Основные endpoints

#### POST `/ocr/process`
Обработка документа с OCR и оценкой качества

**Параметры:**
- `file`: Изображение документа (multipart/form-data)
- `ground_truth`: Эталонный текст (опционально)
- `expected_fields`: Список ожидаемых полей (опционально)
- `schema`: JSON схема для валидации (опционально)

**Ответ:**
```json
{
  "extracted_text": "извлеченный текст",
  "structured_data": {
    "name": "Иван Иванов",
    "date": "01.01.2023",
    "phone": "+7(999)123-45-67"
  },
  "metrics": {
    "cer": 0.05,
    "wer": 0.12,
    "normalized_levenshtein": 0.08,
    "exact_match": 0.0,
    "char_precision": 0.95,
    "char_recall": 0.93,
    "char_f1": 0.94
  },
  "json_validity": true,
  "schema_consistency": true,
  "processing_time": 2.34
}
```

#### POST `/ocr/batch-process`
Пакетная обработка документов

#### POST `/metrics/calculate`
Расчет метрик качества OCR

#### POST `/noise/process`
Обработка зашумленного документа

#### GET `/health`
Проверка состояния сервиса

## Поддерживаемые поля

Система автоматически извлекает следующие поля:
- `name` - имя/ФИО
- `date` - дата
- `phone` - телефон
- `email` - электронная почта
- `address` - адрес
- `passport` - паспортные данные
- `inn` - ИНН
- `amount` - сумма

## Примеры использования

### Обработка документа
```python
import requests

# Загрузка изображения
with open('document.jpg', 'rb') as f:
    files = {'file': f}
    data = {
        'ground_truth': 'Иван Иванов 01.01.2023',
        'expected_fields': '["name", "date"]'
    }
    response = requests.post('http://localhost:8000/ocr/process', files=files, data=data)
    result = response.json()
    print(f"CER: {result['metrics']['cer']}")
    print(f"Извлеченные данные: {result['structured_data']}")
```

### Обработка зашумленного документа
```python
import requests

with open('noisy_document.jpg', 'rb') as f:
    files = {'file': f}
    data = {'ground_truth': 'эталонный текст'}
    response = requests.post('http://localhost:8000/noise/process', files=files, data=data)
    result = response.json()
    print(f"Текст после очистки: {result['extracted_text']}")
```

## Архитектура

- `main.py` - основной FastAPI сервер
- `ocr_service.py` - сервис OCR с EasyOCR
- `metrics_calculator.py` - расчет метрик качества
- `data_extractor.py` - извлечение структурированных данных
- `noise_handler.py` - обработка зашумленных изображений

## Метрики качества

### CER (Character Error Rate)
```
CER = (S + D + I) / N
```
где:
- S - количество замен
- D - количество удалений  
- I - количество вставок
- N - общее количество символов в эталонном тексте

### WER (Word Error Rate)
```
WER = (S + D + I) / N
```
где:
- S - количество замененных слов
- D - количество удаленных слов
- I - количество вставленных слов
- N - общее количество слов в эталонном тексте

### F1-score
```
F1 = 2 * (Precision * Recall) / (Precision + Recall)
```

## Лицензия

MIT License
