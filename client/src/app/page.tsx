'use client';

import { useState } from 'react';
import { parsePdf, summarizeText } from './actions';
import { useToast } from '@/hooks/use-toast';
import { DocUpload } from '@/components/doc-upload';
import { OCRUpload } from '@/components/ocr-upload';
import { OCRMetrics } from '@/components/ocr-metrics';
import { OCRColumnsDisplay } from '@/components/ocr-columns-display';
import { ChatPanel } from '@/components/chat-panel';
import { Logo } from '@/components/icons';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileText, ChevronLeft, ChevronRight, FileImage, BarChart3, Columns } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { type OCRResponse } from '@/lib/ocr-api';

type Document = {
  name: string;
  text: string; // Full text for analysis
  pages: string[]; // Text per page
};

export default function Home() {
  const [doc, setDoc] = useState<Document | null>(null);
  const [summary, setSummary] = useState<string | null>(null);
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [chatKey, setChatKey] = useState(0);
  const [currentPage, setCurrentPage] = useState(0);
  const [ocrResult, setOcrResult] = useState<OCRResponse | null>(null);
  const [activeTab, setActiveTab] = useState('text');
  const { toast } = useToast();

  const handleFileUpload = async (file: File) => {
    if (!file) return;

    setIsSummarizing(true);
    setDoc(null);
    setSummary(null);
    setCurrentPage(0);

    const processFile = (fullText: string, pages: string[]) => {
        const newDoc = { name: file.name, text: fullText, pages: pages };
        setDoc(newDoc);
        setChatKey(prev => prev + 1);

        summarizeText(fullText).then(result => {
            if (result) {
                setSummary(result);
            } else {
                throw new Error('Failed to generate summary.');
            }
        }).catch(error => {
            console.error(error);
            toast({
              variant: 'destructive',
              title: 'Error processing document',
              description: error instanceof Error ? error.message : 'An unknown error occurred.',
            });
            setDoc(null);
        }).finally(() => {
            setIsSummarizing(false);
        });
    }

    if (file.type === 'application/pdf') {
        const reader = new FileReader();
        reader.onload = async (e) => {
            try {
                const buffer = e.target?.result as ArrayBuffer;
                if (!buffer) {
                    throw new Error('File could not be read.');
                }
                const data = new Uint8Array(buffer);
                const pages = await parsePdf(data);
                if (pages === null) {
                  throw new Error('Failed to parse PDF.');
                }
                processFile(pages.join('\n\n'), pages);
            } catch (error) {
                console.error(error);
                toast({
                    variant: 'destructive',
                    title: 'Error processing PDF',
                    description: error instanceof Error ? error.message : 'An unknown error occurred.',
                });
                setIsSummarizing(false);
            }
        };
        reader.onerror = () => {
            toast({
                variant: 'destructive',
                title: 'File Reading Error',
                description: 'Could not read the selected file.',
            });
            setIsSummarizing(false);
        }
        reader.readAsArrayBuffer(file);

    } else {
        const reader = new FileReader();
        reader.onload = async (e) => {
          try {
            const text = e.target?.result as string;
            if (text === null) {
              throw new Error('File could not be read.');
            }
            processFile(text, [text]);
          } catch (error) {
            console.error(error);
            toast({
              variant: 'destructive',
              title: 'Error processing document',
              description: error instanceof Error ? error.message : 'An unknown error occurred.',
            });
            setIsSummarizing(false);
          }
        };
        reader.onerror = () => {
            toast({
                variant: 'destructive',
                title: 'File Reading Error',
                description: 'Could not read the selected file.',
              });
            setIsSummarizing(false);
        }
        reader.readAsText(file);
    }
  };

  const handleOCRComplete = (result: OCRResponse) => {
    setOcrResult(result);
    setActiveTab('ocr');
  };

  const resetApp = () => {
    setDoc(null);
    setSummary(null);
    setIsSummarizing(false);
    setCurrentPage(0);
    setOcrResult(null);
    setActiveTab('text');
  };
  
  const goToPrevPage = () => {
    setCurrentPage(p => Math.max(0, p - 1));
  };

  const goToNextPage = () => {
    if (!doc) return;
    setCurrentPage(p => Math.min(doc.pages.length - 1, p + 1));
  };


  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground">
      <header className="flex items-center h-16 px-4 md:px-8 border-b shrink-0 bg-card/80 backdrop-blur-sm">
        <div className="flex items-center gap-3 cursor-pointer" onClick={resetApp}>
          <Logo className="h-8 w-8 text-primary" />
          <h1 className="text-xl font-bold tracking-tight">DocuChat</h1>
        </div>
      </header>

      <main className="flex-grow flex flex-col items-center justify-center p-4 md:p-8">
        {!doc && !ocrResult ? (
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full max-w-4xl">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="text" className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Текстовые документы
              </TabsTrigger>
              <TabsTrigger value="ocr" className="flex items-center gap-2">
                <FileImage className="h-4 w-4" />
                OCR обработка
              </TabsTrigger>
            </TabsList>
            <TabsContent value="text" className="mt-6">
              <DocUpload onFileUpload={handleFileUpload} isLoading={isSummarizing} />
            </TabsContent>
            <TabsContent value="ocr" className="mt-6">
              <OCRUpload onOCRComplete={handleOCRComplete} />
            </TabsContent>
          </Tabs>
        ) : doc ? (
          <div className="w-full max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8 flex-grow min-h-0">
            <Card className="flex flex-col h-full max-h-[calc(100vh-12rem)] bg-card/80 backdrop-blur-sm">
              <CardHeader className='pb-4'>
                <CardTitle className="flex items-center gap-2 text-primary-foreground">
                  <FileText className="h-5 w-5" />
                  {doc.name}
                </CardTitle>
                <CardDescription className="text-muted-foreground/80 pt-1">Summary</CardDescription>
                {isSummarizing ? (
                    <div className="space-y-2 pt-2">
                        <Skeleton className="h-4 w-full bg-muted/50" />
                        <Skeleton className="h-4 w-full bg-muted/50" />
                        <Skeleton className="h-4 w-3/4 bg-muted/50" />
                    </div>
                ) : (
                    <p className="text-sm text-muted-foreground pt-1">{summary || "No summary available."}</p>
                )}
              </CardHeader>
              <Separator className="bg-border/50" />
              <CardContent className="flex-grow flex flex-col min-h-0 pt-4">
                <div className="flex justify-between items-center mb-2">
                    <h3 className="text-sm font-semibold text-primary-foreground/90">Full Text</h3>
                    {doc.pages.length > 1 && (
                        <div className="flex items-center gap-2">
                            <Button variant="outline" size="icon" className="h-7 w-7" onClick={goToPrevPage} disabled={currentPage === 0}>
                                <ChevronLeft className="h-4 w-4" />
                            </Button>
                            <span className="text-sm text-muted-foreground font-mono">
                                {currentPage + 1} / {doc.pages.length}
                            </span>
                            <Button variant="outline" size="icon" className="h-7 w-7" onClick={goToNextPage} disabled={currentPage === doc.pages.length - 1}>
                                <ChevronRight className="h-4 w-4" />
                            </Button>
                        </div>
                    )}
                </div>
                <div className="flex-grow relative rounded-md border bg-black/30 overflow-hidden">
                    <ScrollArea className="absolute inset-0">
                        <p className="text-sm font-mono whitespace-pre-wrap break-words p-4">{doc.pages[currentPage]}</p>
                    </ScrollArea>
                </div>
              </CardContent>
            </Card>

            <div className="flex flex-col h-full max-h-[calc(100vh-12rem)]">
                <ChatPanel key={chatKey} documentText={doc.text} />
            </div>
          </div>
        ) : ocrResult ? (
          <div className="w-full max-w-7xl mx-auto space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <FileImage className="h-6 w-6" />
                Результаты OCR обработки
              </h2>
              <Button variant="outline" onClick={resetApp}>
                Новый документ
              </Button>
            </div>
            
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="text" className="flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  Текст и структура
                </TabsTrigger>
                <TabsTrigger value="metrics" className="flex items-center gap-2">
                  <BarChart3 className="h-4 w-4" />
                  Метрики качества
                </TabsTrigger>
                <TabsTrigger value="columns" className="flex items-center gap-2">
                  <Columns className="h-4 w-4" />
                  Столбцы и страницы
                </TabsTrigger>
              </TabsList>
              
              <TabsContent value="text" className="mt-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Извлеченный текст</CardTitle>
                    <CardDescription>
                      Текст, извлеченный с помощью OCR технологии
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="p-4 bg-muted rounded-lg max-h-96 overflow-y-auto">
                      <p className="text-sm whitespace-pre-wrap">{ocrResult.extracted_text}</p>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
              
              <TabsContent value="metrics" className="mt-6">
                <OCRMetrics result={ocrResult} />
              </TabsContent>
              
              <TabsContent value="columns" className="mt-6">
                <OCRColumnsDisplay result={ocrResult} />
              </TabsContent>
            </Tabs>
          </div>
        ) : null}
      </main>
    </div>
  );
}
