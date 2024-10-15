### 5.4. Testing the end-to-end process

To test the complete process in an integrated way we have included this code snippet:
1.	Convert HTML files to markdown format with convert_html_to_markdown.ipynb.
2.	Chunk markdown content with the maximum number of tokens specified with chunking_with_max_tokens.ipynb.
3.	Create the index and upload the chunks with the notebook [create_index_and_index_documents.ipynb](../../4.-search-and-retrieval/4.1.-create-index-and-index-documents/create_index_and_index_documents.ipynb).
4.	Test the search and answer generation creating the Excel files with the results of answers evaluation with search_and_answer_generation_tests.ipynb.

**Code Snippet:**
[end_to_end_process.ipynb](./end_to_end_process.ipynb)