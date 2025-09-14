'use server';
/**
 * @fileOverview An LLM-powered chat interface for asking questions about
 * uploaded documents.
 *
 * - llmChatWithDocument - A function that allows users to ask questions
 *   about the content of an uploaded document.
 * - LLMChatWithDocumentInput - The input type for the
 *   llmChatWithDocument function.
 * - LLMChatWithDocumentOutput - The return type for the
 *   llmChatWithDocument function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const LLMChatWithDocumentInputSchema = z.object({
  documentText: z
    .string()
    .describe('The extracted text content of the document.'),
  userQuestion: z.string().describe('The user question about the document.'),
});
export type LLMChatWithDocumentInput = z.infer<
  typeof LLMChatWithDocumentInputSchema
>;

const LLMChatWithDocumentOutputSchema = z.object({
  answer: z.string().describe('The LLM answer to the user question.'),
});
export type LLMChatWithDocumentOutput = z.infer<
  typeof LLMChatWithDocumentOutputSchema
>;

export async function llmChatWithDocument(
  input: LLMChatWithDocumentInput
): Promise<LLMChatWithDocumentOutput> {
  return llmChatWithDocumentFlow(input);
}

const prompt = ai.definePrompt({
  name: 'llmChatWithDocumentPrompt',
  input: {schema: LLMChatWithDocumentInputSchema},
  output: {schema: LLMChatWithDocumentOutputSchema},
  prompt: `You are a helpful assistant designed to answer questions about a
document.

Document Text: {{{documentText}}}

User Question: {{{userQuestion}}}

Answer: `,
});

const llmChatWithDocumentFlow = ai.defineFlow(
  {
    name: 'llmChatWithDocumentFlow',
    inputSchema: LLMChatWithDocumentInputSchema,
    outputSchema: LLMChatWithDocumentOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
