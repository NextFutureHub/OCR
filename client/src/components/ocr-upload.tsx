'use client';

import { useState, useRef, type DragEvent, type ChangeEvent } from 'react';
import { UploadCloud, Loader2, FileImage, FileText, Eye, EyeOff } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';
import { processDocumentOCR, type OCRResponse } from '@/lib/ocr-api';

interface OCRUploadProps {
  onOCRComplete?: (result: OCRResponse) => void;
  onError?: (error: string) => void;
}

export function OCRUpload({ onOCRComplete, onError }: OCRUploadProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<OCRResponse | null>(null);
  const [showMetrics, setShowMetrics] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const supportedFormats = [
    '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.pdf'
  ];

  const handleFile = async (file: File | undefined | null) => {
    if (!file) return;

    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!supportedFormats.includes(fileExtension)) {
      toast({
        variant: 'destructive',
        title: 'Неподдерживаемый формат файла',
        description: `Поддерживаемые форматы: ${supportedFormats.join(', ')}`,
      });
      return;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB
      toast({
        variant: 'destructive',
        title: 'Файл слишком большой',
        description: 'Максимальный размер файла: 10MB',
      });
      return;
    }

    setIsProcessing(true);
    setProgress(0);
    setResult(null);

    try {
      // Симуляция прогресса
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + Math.random() * 10;
        });
      }, 200);

      const ocrResult = await processDocumentOCR({ file });
      
      clearInterval(progressInterval);
      setProgress(100);
      
      setResult(ocrResult);
      onOCRComplete?.(ocrResult);

      toast({
        title: 'OCR обработка завершена',
        description: `Извлечено ${ocrResult.extracted_text.length} символов`,
      });

    } catch (error) {
      console.error('OCR processing error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Неизвестная ошибка';
      
      toast({
        variant: 'destructive',
        title: 'Ошибка OCR обработки',
        description: errorMessage,
      });
      
      onError?.(errorMessage);
    } finally {
      setIsProcessing(false);
      setTimeout(() => setProgress(0), 1000);
    }
  };

  const onDragEnter = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const onDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const onDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    handleFile(file);
  };

  const onFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    handleFile(file);
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  const resetUpload = () => {
    setResult(null);
    setProgress(0);
    setIsProcessing(false);
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Загрузка файла */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileImage className="h-5 w-5" />
            OCR Обработка документов
          </CardTitle>
          <CardDescription>
            Загрузите изображение или PDF для извлечения текста с помощью OCR
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            onDragEnter={onDragEnter}
            onDragLeave={onDragLeave}
            onDragOver={onDragOver}
            onDrop={onDrop}
            onClick={openFileDialog}
            className={cn(
              'relative flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer bg-secondary hover:bg-muted transition-colors',
              isDragging ? 'border-primary' : 'border-border'
            )}
          >
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              onChange={onFileChange}
              accept={supportedFormats.join(',')}
              disabled={isProcessing}
            />
            {isProcessing ? (
              <div className="flex flex-col items-center gap-4 text-center">
                <Loader2 className="h-12 w-12 text-primary animate-spin" />
                <p className="text-lg font-medium text-foreground">Обработка документа</p>
                <div className="w-64">
                  <Progress value={progress} className="w-full" />
                  <p className="text-sm text-muted-foreground mt-2">
                    {Math.round(progress)}% завершено
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center text-center">
                <UploadCloud className="w-12 h-12 mb-4 text-primary" />
                <p className="mb-2 text-lg font-semibold text-foreground">
                  <span className="text-primary">Нажмите для загрузки</span> или перетащите файл
                </p>
                <p className="text-sm text-muted-foreground">
                  Поддерживаемые форматы: {supportedFormats.join(', ')}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Максимальный размер: 10MB
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Результаты OCR */}
      {result && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Результаты OCR
              </CardTitle>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowMetrics(!showMetrics)}
                >
                  {showMetrics ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  {showMetrics ? 'Скрыть метрики' : 'Показать метрики'}
                </Button>
                <Button variant="outline" size="sm" onClick={resetUpload}>
                  Новый файл
                </Button>
              </div>
            </div>
            <CardDescription>
              Время обработки: {result.processing_time.toFixed(2)}с
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Извлеченный текст */}
            <div>
              <h4 className="font-semibold mb-2">Извлеченный текст:</h4>
              <div className="p-4 bg-muted rounded-lg max-h-64 overflow-y-auto">
                <p className="text-sm whitespace-pre-wrap">{result.extracted_text}</p>
              </div>
            </div>

            {/* Метрики качества */}
            {showMetrics && (
              <div className="space-y-4">
                <h4 className="font-semibold">Метрики качества:</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(result.metrics).map(([key, value]) => (
                    <div key={key} className="text-center">
                      <div className="text-2xl font-bold text-primary">
                        {typeof value === 'number' ? (value * 100).toFixed(1) + '%' : value}
                      </div>
                      <div className="text-sm text-muted-foreground capitalize">
                        {key.replace(/_/g, ' ')}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Статус валидации */}
            <div className="flex gap-2">
              <Badge variant={result.json_validity ? 'default' : 'destructive'}>
                JSON: {result.json_validity ? 'Валидный' : 'Невалидный'}
              </Badge>
              <Badge variant={result.schema_consistency ? 'default' : 'destructive'}>
                Схема: {result.schema_consistency ? 'Соответствует' : 'Не соответствует'}
              </Badge>
            </div>

            {/* Структурированные данные */}
            {Object.keys(result.structured_data).length > 0 && (
              <div>
                <h4 className="font-semibold mb-2">Структурированные данные:</h4>
                <div className="p-4 bg-muted rounded-lg">
                  <pre className="text-sm overflow-x-auto">
                    {JSON.stringify(result.structured_data, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
