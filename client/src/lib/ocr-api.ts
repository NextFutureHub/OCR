/**
 * OCR API интеграция для работы с бэкенд сервисом
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

export interface ColumnData {
  text: string;
  side: 'left' | 'right';
  language: string;
  items_count: number;
  confidence_avg: number;
}

export interface PageData {
  page_number: number;
  text: string;
  columns: ColumnData[];
  columns_count: number;
  has_multiple_columns: boolean;
}

export interface OCRResponse {
  extracted_text: string;
  structured_data: Record<string, any>;
  metrics: Record<string, number>;
  json_validity: boolean;
  schema_consistency: boolean;
  processing_time: number;
  // Новые поля для столбцов и страниц
  pages?: PageData[];
  total_pages?: number;
  has_multiple_columns?: boolean;
  columns?: ColumnData[];
  columns_count?: number;
}

export interface OCRMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  character_error_rate: number;
  word_error_rate: number;
  field_metrics?: Record<string, any>;
}

export interface OCRRequest {
  file: File;
  ground_truth?: string;
  expected_fields?: string[];
  schema?: Record<string, any>;
}

/**
 * Отправка файла на OCR обработку
 */
export async function processDocumentOCR(request: OCRRequest): Promise<OCRResponse> {
  const formData = new FormData();
  formData.append('file', request.file);
  
  if (request.ground_truth) {
    formData.append('ground_truth', request.ground_truth);
  }
  
  if (request.expected_fields) {
    formData.append('expected_fields', JSON.stringify(request.expected_fields));
  }
  
  if (request.schema) {
    formData.append('schema', JSON.stringify(request.schema));
  }

  const response = await fetch(`${API_BASE_URL}/ocr/process`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

/**
 * Пакетная обработка документов
 */
export async function batchProcessDocuments(files: File[]): Promise<any> {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });

  const response = await fetch(`${API_BASE_URL}/ocr/batch-process`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

/**
 * Расчет метрик качества OCR
 */
export async function calculateMetrics(
  extracted_text: string,
  ground_truth: string,
  expected_fields?: string[]
): Promise<OCRMetrics> {
  const response = await fetch(`${API_BASE_URL}/metrics/calculate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      extracted_text,
      ground_truth,
      expected_fields,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

/**
 * Обработка зашумленного документа
 */
export async function processNoisyDocument(file: File, ground_truth?: string): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  
  if (ground_truth) {
    formData.append('ground_truth', ground_truth);
  }

  const response = await fetch(`${API_BASE_URL}/noise/process`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

/**
 * Обработка PDF документа
 */
export async function processPDFDocument(
  file: File,
  ground_truth?: string,
  expected_fields?: string[],
  schema?: Record<string, any>
): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  
  if (ground_truth) {
    formData.append('ground_truth', ground_truth);
  }
  
  if (expected_fields) {
    formData.append('expected_fields', JSON.stringify(expected_fields));
  }
  
  if (schema) {
    formData.append('schema', JSON.stringify(schema));
  }

  const response = await fetch(`${API_BASE_URL}/pdf/process`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

/**
 * Проверка состояния API
 */
export async function checkAPIHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * Тестовый OCR без файла
 */
export async function testOCR(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/test/ocr`, {
    method: 'POST',
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}
