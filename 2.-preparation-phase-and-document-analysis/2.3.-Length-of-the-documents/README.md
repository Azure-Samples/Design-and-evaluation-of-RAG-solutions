#### 2.3. Document format: Length of the documents

Another important aspect to assess is the length of the documents and paragraphs or sections in them. This is defined by number of tokens, which are fundamental units of text processed by language models, so for this analysis we will investigate token distribution across the document collection. There is no standard recommendation based on document length, it needs to be assessed for the specific use case and validate different strategies to find the most suitable one.

LLMs typically have a predefined token limit they can process in a single call, so the total number of tokens in the chunks or sections used to build the final answer needs to stay below that limit. Even if using a model with a high limit of tokens per single call, it is recommended to maintain the total token number within a threshold so that all the necessary information is included but not too much that can confuse the LLM to include additional non relevant details. This is also relevant from an optimization perspective, as these models are typically billed on volume or usage of dedicated capacity.

We recommend using a library such as [tiktoken](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb) which can look into each document and extract token numbers to define the chunking and indexing strategy. By doing this we can understand better the token distribution, which looks like the following:

| Token Range | Document type A | Document type B |
| --- | --- | --- |
|  | Count - %  | Count - %  |
| 0-511 | 999 - 9,99% | 999 - 9,99% |
| 512-999 | 999 - 9,99% | 999 - 9,99% |
| 1.000-1.999 | 999 - 9,99% | 999 - 9,99% |
| +2.000 | 999 - 9,99% | 999 - 9,99% |

Inspecting the distribution of tokens for documents shorter than 600 tokens, we will find a table like this:

| Number of tokens | Document type A | Document type B |
| --- | --- | --- |
|   | Count - %  | Count - %   |
| Less than 50 tokens | 999 - 9,99% | 999 - 9,99% |
| Less than 100 tokens | 999 - 9,99% | 999 - 9,99% |
| Less than 150 tokens | 999 - 9,99% | 999 - 9,99% |
| Less than 200 tokens | 999 - 9,99% | 999 - 9,99% |
| Less than 300 tokens | 999 - 9,99% | 999 - 9,99% |
| Less than 512 tokens | 999 - 9,99% | 999 - 9,99% |
| Less than 600 tokens | 999 - 9,99% | 999 - 9,99% |

**Document length analysis (per document type):**

- Identify the number of **documents shorter than 512 tokens**, meaning for this subset it could make sense to index the full document in a single index unit instead to chunk it in several sub-documents.
- Identify the number of **documents below 150 tokens**. This might require additional inspection as from a high-level review it seems like there is little context or relevant information in this subset of documents, potentially making them irrelevant for the overall solution. If this is the case, we recommend removing them from the index
- For the rest of the documents above this number it is necessary to **define a chunking strategy** as they are too long to be included as complete documents in the answer generation. We will look into options in the next section.

**Code Snippet:**
[calculate_length_of_the_documents.ipynb](./calculate_length_of_the_documents.ipynb)