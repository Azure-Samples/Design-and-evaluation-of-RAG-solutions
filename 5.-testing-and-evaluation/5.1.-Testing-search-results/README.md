## 5.1. Testing search results

The purpose of these tests is to evaluate that the search results retrieved from the AI search index contain the relevant information to answer to a specific question, meaning the index and the search configuration are optimal for the solution.

An easy way, is checking if the expected document ID associated to the question defined by the client’s business area is included in the chunk retrieved in the search and the is included in the generated answer.

The search tests have to include the following combinations:

- Searching with the query in lowercase and uppercase because the vector search is sensitive to this, so results can vary. As a general recommendation lowercase provides better results, although like other configuration elements, we recommend doing this validation per use case and document collection.
- Chunks techniques:
  - Langchain’s semantic chunking.
  - GPT-4T semantic chunking.
  - Langchain & tiktoken max. 512 tokens with 25% overlapping.
  - Langchain & tiktoken max. 1024 tokens with 25% overlapping.
- Vector search with:
  - 1 vector field generated with the model ada-02 and large-03 from the Content of the chunk.
  - 1 vector field generated with the model ada-02 and large-03 from the Title and the Content of the chunk.
  - 2 vector fields, one generated with the model ada-02 and large-03 from the Title and the other one from the Content of the chunk.
  - 3 vector fields, one generated with the model ada-02 and large-03 from the Title, other one from the Content of the chunk and another from the rest of searchable fields (summary, keywords, etc.).
- Maximum number of chunks retrieved, and maximum number of chunks used to generate the answers (the identified by the re-ranker with best confidence, >90%):
  - Retrieve 10 chunks and use a maximum of 10 chunks.
  - Retrieve 20 chunks and use a maximum of 20 chunks.
  - Retrieve 20 chunks and use a maximum of 10 chunks.

The table of results will be like this:

| Chunking technique | Embedding fields | Total search results with expected document ID |     |     |     | Total generated answers with expected document ID |     |     |     |     |     |
| --- | --- | --- |     |     |     | --- |     |     |     |     |     | --- | --- | --- | --- | --- | --- |
| Search uppercase |     | Search lowercase |     | Search uppercase |     | Search lowercase |     |     |
| --- |     | --- |     | --- |     | --- |     |     | --- | --- | --- | --- | --- | --- |
| ada-02 | large-03 | ada-02 | large-03 | ada-02 | large-03 | ada-02 | large-03 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Langchain semantic chunking | 1 vector field with Content |     |     |     |     |     |     |     |     |
| 1 vector field with Title and Content |     |     |     |     |     |     |     |     |
| 2 vector fields with title and content |     |     |     |     |     |     |     |     |
| 3 vector fields with title, content and Others |     |     |     |     |     |     |     |     |
| GPT-4T semantic chunking | 1 vector field with Content |     |     |     |     |     |     |     |     |
| 1 vector field with Title and Content |     |     |     |     |     |     |     |     |
| 2 vector fields with title and content |     |     |     |     |     |     |     |     |
| 3 vector fields with title, content and Others |     |     |     |     |     |     |     |     |
| Langchain & tiktoken max. 512 tokens with 25% overlapping | 1 vector field with Content |     |     |     |     |     |     |     |     |
| 1 vector field with Title and Content |     |     |     |     |     |     |     |     |
| 2 vector fields with title and content |     |     |     |     |     |     |     |     |
| 3 vector fields with title, content and Others |     |     |     |     |     |     |     |     |
| Langchain & tiktoken max. 1024 tokens with 25% overlapping | 1 vector field with Content |     |     |     |     |     |     |     |     |
| 1 vector field with Title and Content |     |     |     |     |     |     |     |     |
| 2 vector fields with title and content |     |     |     |     |     |     |     |     |
| 3 vector fields with title, content and Others |     |     |     |     |     |     |     |     |

**Code Snippet:**
[search_and_answer_generation_tests.ipynb](./search_and_answer_generation_tests.ipynb)