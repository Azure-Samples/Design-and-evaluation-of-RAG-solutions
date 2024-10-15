# 4. Search and retrieval

As explained in the sections above, an index is defined through a schema of different fields containing different values. These fields have different purposes (normally text-based search, vector search, sorting or filtering), so it’s important that the right configuration is set in the index for the queries to retrieve the information correctly. This is done by setting specific attributes to each field based on the purpose they serve. The possible attributes are:

- Searchable
- Filterable
- Sortable
- Facetable
- Key
- Retrievable

These are set for each field when creating the index through the index schema. More details can be found at: [Search index overview - Azure AI Search | Microsoft Learn](https://learn.microsoft.com/en-us/azure/search/search-what-is-an-index).

## 4.1. Azure AI Search configuration

As explained above, it is essential that the fields that contain information related to the search query have the right attributes, so they have to be searchable or filterable, etc., depending of the use in the solution.

Another aspect to consider for the index configuration is the **NLP Analyzer**. An analyzer is part of the full-text search engine that handles the processing of strings during both indexing and query execution. This text processing, or lexical analysis, transforms a string through several actions:

- Removing unnecessary words (stopwords) and punctuation.
- Breaking down phrases and hyphenated words into their individual parts.
- Converting uppercase words to lowercase.
- Reducing words to their basic root forms for efficient storage and to ensure matches are found regardless of tense.

In general, it is important to configure the same analyzer in every searchable field to have a consistent NLP. For example, if the content are in Spanish the most appropriate is “es.microsoft”. More information about analyzers and the full list of options is available at: [Analyzers for linguistic and text processing - Azure AI Search | Microsoft Learn](https://learn.microsoft.com/en-us/azure/search/search-analyzers).

## 4.2. Create index and index documents

Before searching for documents you need to create the index and index documents.

Here is the [notebook](4.1.-create-index-and-index-documents/create_index_and_index_documents.ipynb) to do it, that is beeing used before searching duplicates and before testing the search.

## 4.3. Search retrieval and ranking

Search Retrieval, often called L1, is designed to quickly find all the documents from the index that satisfy the search criteria, potentially across millions or billions of documents. These documents are then scored to select the top few (typically around 50) to return to the user or feed into the next layer.

Azure AI Search supports the following L1 modes:

- **Keyword search:** Uses traditional full-text search methods (content is broken into terms through language-specific text analysis) with probabilistic model for scoring based Term Frequency, Inverse Document Frequency and Field Length. It is useful because it prioritizes matching specific, important words that might be diluted in an embedding.
- **Vector search:** Documents are converted from text to vector representations using an embedding model. Retrieval is performed by generating a query embedding and finding the documents whose vectors are closest to the query’s. is powerful because embeddings are less sensitive to misspellings, synonyms, and phrasing differences and can even work in cross lingual scenarios.
Vector search algorithms include exhaustive k-nearest neighbors (KNN) and Hierarchical Navigable Small World (HNSW).
Exhaustive KNN performs a brute-force search that scans the entire vector space.
HNSW performs an approximate nearest neighbor (ANN) search.
- **Hybrid search:** Performs both keyword and vector retrieval and applies a fusion step to select the best results from each technique.

**Ranking**, also called L2, takes a subset of the top L1 results and computes higher quality relevance scores to reorder the result set. The L2 can improve the L1's ranking because it applies more computational power to each result. The L2 ranker can only reorder what the L1 already found – if the L1 missed an ideal document, the L2 can't fix that. L2 ranking is critical for RAG applications to make sure the best results are in the top positions.

**Semantic ranking** is performed by Azure AI Search's L2 ranker which utilizes multi-lingual, deep learning models adapted from Microsoft Bing. The Semantic ranker can rank the top 50 results from the L1.

**The best combination of search retrieval and ranking is the** **Hybrid Retrieval + Semantic Ranking**.

In general, in order to improve the search results, we recommend to create a **scoring profile** that includes a multiplier by 5 in the field **Title**, because this is an important field that provides relevant information about the documents, so if the words included in the user’s query appears in the Title those documents has to be prioritized.

## [4.4. Search results re-ranking](./4.4.-Search-results-re-ranking/README.md)

Reranking search results reranking is a good technique to improve the performance and the quality of the answers generated by the model. It is also relevant from an optimization perspective, as it can be implemented using a lighter and cheaper model, and then sending a shorter prompt to the more powerful and costly model to build the final answer.

Here are the [details](./4.4.-Search-results-re-ranking/README.md) and the code snippet.
## 4.5. Search filtering
In many applications it is important to have a possiblity of deterministic filtering of the search results by a field or set of fields defined in the index. For that to be possbile the fields need to be indicated as 'Filtrable' in the index definition. Application of the filters can happen either pre vector search or post vector search and the choice of either of it depends on the dataset size and customer priorities. For more detailed instructions and guidelines follow the documentation link: [link](https://learn.microsoft.com/en-us/azure/search/vector-search-filters?tabs=filter-2024-07-01)


## 4.6. Search orchestration

When implementing RAG, it is necessary to orchestrate the connection between the LLM to the search index so that once a user sends an input, a search query is triggered, and its results are sent back to the model to build a response. There are different ways to do this, from custom code to built-in features.

- **Custom development:** The orchestration can be implemented directly by developing code that triggers the search query from the user question. It provides full control for the developer to decide when a query needs to be run, which includes defining a specific logic to detect when the user is changing the topic and the retrieved information is no longer relevant or an additional query is required.
- **Pre-built library:** There are some existing libraries that can act as a wrapper, making it simpler to connect the user input to the LLM to the Azure AI Index (Sample reference: [Azure AI Search | 🦜️🔗 LangChain](https://python.langchain.com/v0.2/docs/integrations/vectorstores/azuresearch/))
- **LLM-based orchestration:** Another option instead of defining a number of messages or interactions before running a new query, or running a new query with every interaction, is to use the LLM to decide when running a query is required or if it can answer with the existing information. This can be done by 
1. Using native function calling, a built-in feature in Azure Open AI which enables that the model generates a function call with relevant options and parameters. The application logic can then inercept the call and trigger it either automatically or with the user interaction.  
For this to be possible, the LLM call would include the parameter functions names, descriptions and specifications, which is linked to a pre-defined python function – in this case to search the index with a specific configuration. These can be helpful when there are multiple interactions and it’s the ratio between messages and queries is not straightforward. (Sample reference: [openai/Basic_Samples/Functions/functions_with_azure_search.ipynb at main · Azure-Samples/openai (github.com)](https://github.com/Azure-Samples/openai/blob/main/Basic_Samples/Functions/functions_with_azure_search.ipynb))
2. Using an agent framework such as Semantic Kernel, Langchain, Llamaindex etc. In such framework an agent or ochestrator is taking the function of deciding for action sequence and if needed triggers the function execusion on the application side. 
3. The preprocessing of the query and transformation to the correct formfactor for a database or search enging such as Azure AI Search can be facilitated by libraries that allow for model output control. This is possible only for the models that are deployed and run the GPU server controlled by the application and only those that allow for inference modification. One such example can be Phi3 deployed on premis and usage of Guidance library that allow for optimized text trasnformations. 
