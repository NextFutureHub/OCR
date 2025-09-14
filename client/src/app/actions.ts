'use server';

import { llmChatWithDocument } from '@/ai/flows/llm-chat-with-document';
import { summarizeDocument } from '@/ai/flows/summarize-uploaded-document';
import pdf from 'pdf-parse/lib/pdf-parse.js';

/**
 * Summarizes the provided text using an AI model.
 * @param documentText The text to summarize.
 * @returns The summary string, or null on failure.
 */
export async function summarizeText(documentText: string): Promise<string | null> {
  try {
    if (!documentText.trim()) {
      return 'Document is empty.';
    }
    const { summary } = await summarizeDocument({ documentText });
    return summary;
  } catch (error) {
    console.error('Error in summarizeText:', error);
    return null;
  }
}

/**
 * Asks a question about a document and gets an answer from an AI model.
 * @param documentText The context from the document.
 * @param userQuestion The user's question.
 * @returns The answer string, or a default error message on failure.
 */
export async function askQuestion(
  documentText: string,
  userQuestion: string
): Promise<string> {
  try {
    const { answer } = await llmChatWithDocument({ documentText, userQuestion });
    return answer;
  } catch (error) {
    console.error('Error in askQuestion:', error);
    return 'Sorry, I encountered an error while processing your question.';
  }
}

/**
 * Parses a PDF file buffer and extracts the text content page by page.
 * @param pdfBuffer The PDF file as a Uint8Array.
 * @returns An array of strings, where each string is the text of a page, or null on failure.
 */
export async function parsePdf(pdfBuffer: Uint8Array): Promise<string[] | null> {
  try {
    const data = await pdf(Buffer.from(pdfBuffer), {
        pagerender: (pageData: any) => pageData.getTextContent().then((textContent: any) => {
            return textContent.items.map((item: any) => item.str).join(' ');
        })
    });
    
    if (!data || !data.numpages || !Array.isArray(data.text.split('\n\n\n'))) {
        // Fallback to all text if page-by-page fails for some reason.
        const allTextData = await pdf(Buffer.from(pdfBuffer));
        return allTextData ? [allTextData.text] : null;
    }

    const pages = data.text.split('\n\n\n').map(page => page.trim()).filter(page => page);

    if (pages.length > 0) {
        return pages;
    }
    
    const allTextData = await pdf(Buffer.from(pdfBuffer));
    return allTextData ? [allTextData.text] : null;

  } catch (error) {
    console.error('Error parsing PDF:', error);
    return null;
  }
}
