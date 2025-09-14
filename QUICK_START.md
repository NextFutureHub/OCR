# Быстрый старт OCR Quality Assessment API

## 🚀 Запуск за 5 минут

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Запуск сервера
```bash
python run_server.py
```

### 3. Проверка работы
Откройте браузер: `http://localhost:8000`

### 4. Тестирование
```bash
python test_api.py
```

### 5. Демонстрация
```bash
python demo.py
```

## 📊 Основные метрики

Система автоматически рассчитывает:

- **CER (Character Error Rate)** - ошибки на уровне символов
- **WER (Word Error Rate)** - ошибки на уровне слов
- **Normalized Levenshtein Distance** - нормализованное расстояние
- **F1-score** - для каждого поля
- **Exact Match** - процент полностью верных документов

## 🔧 API Endpoints

| Endpoint | Описание |
|----------|----------|
| `POST /ocr/process` | Обработка документа |
| `POST /metrics/calculate` | Расчет метрик |
| `POST /noise/process` | Обработка шума |
| `GET /health` | Проверка состояния |

## 📝 Пример использования

```python
import requests

# Расчет метрик
response = requests.post('http://localhost:8000/metrics/calculate', 
    json={
        'extracted_text': 'Иван Иванов 01.01.2023',
        'ground_truth': 'Иван Иванов 01.01.2023'
    })

result = response.json()
print(f"CER: {result['cer']}")
print(f"WER: {result['wer']}")
```

## 🎯 Оценка качества

Система оценивает качество по критериям:

- **Точность OCR** (25 баллов)
- **Извлечение данных** (25 баллов)  
- **Работа с шумом** (10 баллов)
- **Структурированность** (10 баллов)

**Итого: 70 баллов**

## 📋 Поддерживаемые поля

- `name` - имя/ФИО
- `date` - дата
- `phone` - телефон
- `email` - электронная почта
- `address` - адрес
- `passport` - паспортные данные
- `inn` - ИНН
- `amount` - сумма

## 🔍 Документация

- **README.md** - полная документация
- **INSTALL.md** - инструкция по установке
- **PROJECT_STRUCTURE.md** - структура проекта
- **http://localhost:8000/docs** - интерактивная документация API

## ⚡ Быстрые команды

```bash
# Запуск сервера
python run_server.py

# Тестирование
python test_api.py

# Демонстрация
python demo.py

# Примеры
python examples.py
```

## 🛠️ Настройка

Создайте файл `.env`:
```env
DEBUG=False
HOST=0.0.0.0
PORT=8000
OCR_LANGUAGES=ru,en
OCR_GPU_ENABLED=False
```

## 📞 Поддержка

При проблемах:
1. Проверьте логи в `ocr_api.log`
2. Убедитесь, что порт 8000 свободен
3. Проверьте установку зависимостей

## 🎉 Готово!

Система готова к использованию для оценки качества OCR!
