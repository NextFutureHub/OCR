'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { ChevronLeft, ChevronRight, FileText, Columns, Languages } from 'lucide-react';
import { type OCRResponse, type PageData, type ColumnData } from '@/lib/ocr-api';

interface OCRColumnsDisplayProps {
  result: OCRResponse;
}

export function OCRColumnsDisplay({ result }: OCRColumnsDisplayProps) {
  const [currentPage, setCurrentPage] = useState(0);
  const [activeView, setActiveView] = useState<'full' | 'columns' | 'pages'>('full');

  // Определяем, есть ли страницы или столбцы
  const hasPages = result.pages && result.pages.length > 0;
  const hasColumns = result.columns && result.columns.length > 0;
  const hasMultipleColumns = result.has_multiple_columns || false;

  const goToPrevPage = () => {
    if (hasPages && result.pages) {
      setCurrentPage(p => Math.max(0, p - 1));
    }
  };

  const goToNextPage = () => {
    if (hasPages && result.pages) {
      setCurrentPage(p => Math.min(result.pages!.length - 1, p + 1));
    }
  };

  const getLanguageLabel = (language: string) => {
    switch (language) {
      case 'ru': return 'Русский';
      case 'en': return 'English';
      case 'mixed': return 'Смешанный';
      default: return language;
    }
  };

  const getLanguageColor = (language: string) => {
    switch (language) {
      case 'ru': return 'bg-blue-100 text-blue-800';
      case 'en': return 'bg-green-100 text-green-800';
      case 'mixed': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const renderColumns = (columns: ColumnData[]) => {
    if (columns.length === 0) return null;

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {columns.map((column, index) => (
          <Card key={index} className="h-full">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Columns className="h-4 w-4" />
                  {column.side === 'left' ? 'Левый столбец' : 'Правый столбец'}
                </CardTitle>
                <div className="flex gap-2">
                  <Badge className={getLanguageColor(column.language)}>
                    {getLanguageLabel(column.language)}
                  </Badge>
                  <Badge variant="outline">
                    {Math.round(column.confidence_avg * 100)}%
                  </Badge>
                </div>
              </div>
              <CardDescription>
                {column.items_count} элементов, средняя уверенность: {Math.round(column.confidence_avg * 100)}%
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-64">
                <p className="text-sm whitespace-pre-wrap leading-relaxed">
                  {column.text}
                </p>
              </ScrollArea>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  };

  const renderPages = (pages: PageData[]) => {
    if (pages.length === 0) return null;

    const currentPageData = pages[currentPage];

    return (
      <div className="space-y-4">
        {/* Навигация по страницам */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={goToPrevPage}
              disabled={currentPage === 0}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm text-muted-foreground">
              Страница {currentPage + 1} из {pages.length}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={goToNextPage}
              disabled={currentPage === pages.length - 1}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
          <Badge variant="outline">
            {currentPageData.has_multiple_columns ? '2 столбца' : '1 столбец'}
          </Badge>
        </div>

        {/* Содержимое страницы */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Страница {currentPageData.page_number}
            </CardTitle>
            <CardDescription>
              {currentPageData.columns_count} столбцов, {currentPageData.text.length} символов
            </CardDescription>
          </CardHeader>
          <CardContent>
            {currentPageData.has_multiple_columns ? (
              renderColumns(currentPageData.columns)
            ) : (
              <ScrollArea className="h-96">
                <p className="text-sm whitespace-pre-wrap leading-relaxed">
                  {currentPageData.text}
                </p>
              </ScrollArea>
            )}
          </CardContent>
        </Card>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {/* Переключатель представлений */}
      <Tabs value={activeView} onValueChange={(value) => setActiveView(value as any)}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="full" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Полный текст
          </TabsTrigger>
          {hasColumns && (
            <TabsTrigger value="columns" className="flex items-center gap-2">
              <Columns className="h-4 w-4" />
              Столбцы ({result.columns_count})
            </TabsTrigger>
          )}
          {hasPages && (
            <TabsTrigger value="pages" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Страницы ({result.total_pages})
            </TabsTrigger>
          )}
        </TabsList>

        <TabsContent value="full" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Извлеченный текст</CardTitle>
              <CardDescription>
                Полный текст документа ({result.extracted_text.length} символов)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                <p className="text-sm whitespace-pre-wrap leading-relaxed">
                  {result.extracted_text}
                </p>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        {hasColumns && (
          <TabsContent value="columns" className="mt-4">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Languages className="h-5 w-5" />
                <h3 className="text-lg font-semibold">Анализ столбцов</h3>
                <Badge variant="outline">
                  {result.columns_count} столбцов
                </Badge>
              </div>
              {renderColumns(result.columns!)}
            </div>
          </TabsContent>
        )}

        {hasPages && (
          <TabsContent value="pages" className="mt-4">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                <h3 className="text-lg font-semibold">Страницы документа</h3>
                <Badge variant="outline">
                  {result.total_pages} страниц
                </Badge>
              </div>
              {renderPages(result.pages!)}
            </div>
          </TabsContent>
        )}
      </Tabs>

      {/* Информация о структуре */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Информация о структуре</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="font-medium">Страниц:</span>
              <span className="ml-2">{result.total_pages || 1}</span>
            </div>
            <div>
              <span className="font-medium">Столбцов:</span>
              <span className="ml-2">{result.columns_count || 1}</span>
            </div>
            <div>
              <span className="font-medium">Многоязычный:</span>
              <span className="ml-2">{hasMultipleColumns ? 'Да' : 'Нет'}</span>
            </div>
            <div>
              <span className="font-medium">Символов:</span>
              <span className="ml-2">{result.extracted_text.length}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
