'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { type OCRResponse } from '@/lib/ocr-api';

interface OCRMetricsProps {
  result: OCRResponse;
}

export function OCRMetrics({ result }: OCRMetricsProps) {
  const metrics = result.metrics;
  
  // Подготовка данных для графика
  const chartData = Object.entries(metrics)
    .filter(([_, value]) => typeof value === 'number')
    .map(([key, value]) => ({
      metric: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      value: value * 100, // Конвертируем в проценты
      rawValue: value
    }));

  const getMetricColor = (value: number) => {
    if (value >= 0.9) return 'text-green-600';
    if (value >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getMetricBadgeVariant = (value: number) => {
    if (value >= 0.9) return 'default';
    if (value >= 0.7) return 'secondary';
    return 'destructive';
  };

  return (
    <div className="space-y-6">
      {/* Основные метрики */}
      <Card>
        <CardHeader>
          <CardTitle>Метрики качества OCR</CardTitle>
          <CardDescription>
            Оценка точности и качества распознавания текста
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(metrics).map(([key, value]) => {
              if (typeof value !== 'number') return null;
              
              const percentage = value * 100;
              const colorClass = getMetricColor(value);
              const badgeVariant = getMetricBadgeVariant(value);
              
              return (
                <div key={key} className="text-center space-y-2">
                  <div className={`text-3xl font-bold ${colorClass}`}>
                    {percentage.toFixed(1)}%
                  </div>
                  <div className="text-sm text-muted-foreground capitalize">
                    {key.replace(/_/g, ' ')}
                  </div>
                  <Badge variant={badgeVariant} className="text-xs">
                    {value >= 0.9 ? 'Отлично' : value >= 0.7 ? 'Хорошо' : 'Требует улучшения'}
                  </Badge>
                  <Progress value={percentage} className="w-full" />
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* График метрик */}
      {chartData.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Визуализация метрик</CardTitle>
            <CardDescription>
              Сравнение различных показателей качества
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="metric" 
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    fontSize={12}
                  />
                  <YAxis 
                    domain={[0, 100]}
                    tickFormatter={(value) => `${value}%`}
                  />
                  <Tooltip 
                    formatter={(value: number) => [`${value.toFixed(1)}%`, 'Значение']}
                    labelFormatter={(label) => `Метрика: ${label}`}
                  />
                  <Bar 
                    dataKey="value" 
                    fill="hsl(var(--primary))"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Информация о валидации */}
      <Card>
        <CardHeader>
          <CardTitle>Статус валидации</CardTitle>
          <CardDescription>
            Проверка корректности структурированных данных
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center gap-2">
              <Badge variant={result.json_validity ? 'default' : 'destructive'}>
                {result.json_validity ? '✓' : '✗'}
              </Badge>
              <span className="text-sm">
                JSON валидность: {result.json_validity ? 'Валидный' : 'Невалидный'}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant={result.schema_consistency ? 'default' : 'destructive'}>
                {result.schema_consistency ? '✓' : '✗'}
              </Badge>
              <span className="text-sm">
                Соответствие схеме: {result.schema_consistency ? 'Соответствует' : 'Не соответствует'}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Детальная информация */}
      <Card>
        <CardHeader>
          <CardTitle>Детальная информация</CardTitle>
          <CardDescription>
            Дополнительные параметры обработки
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium">Время обработки:</span>
              <span className="ml-2">{result.processing_time.toFixed(2)} секунд</span>
            </div>
            <div>
              <span className="font-medium">Длина текста:</span>
              <span className="ml-2">{result.extracted_text.length} символов</span>
            </div>
            <div>
              <span className="font-medium">Количество полей:</span>
              <span className="ml-2">{Object.keys(result.structured_data).length}</span>
            </div>
            <div>
              <span className="font-medium">Средняя точность:</span>
              <span className="ml-2">
                {(() => {
                  const numeric = Object.values(metrics).filter(
                    (v): v is number => typeof v === 'number' && isFinite(v as number)
                  );
                  if (numeric.length === 0) return '—';
                  const avg = numeric.reduce((a, b) => a + b, 0) / numeric.length;
                  return `${(avg * 100).toFixed(1)}%`;
                })()}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
