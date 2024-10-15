# 2. Preparation phase and document analysis

Before starting to build the solution, it is important to assess the data that will be used as a data source. This section focuses on the preprocessing and analysis of documents, which is crucial to create a clean and well-structured index. By converting formats, analyzing document lengths and handling duplicates or redundant information, you ensure the data is in optimal shape for efficient retrieval and relevance in a RAG system.

## Document collection for knowledge base

Before deciding on a chunking and indexing strategy, it is important to consider the distribution of information in the document collection. To understand distribution is necessary to explore the data and consider the right options based on said exploration and analysis. Some specific document types might require additional preprocessing, such as tables, images or special characters. 

The end product of the document analysis and preprocessing is a representation of the whole knowledge base in a strudcutred form: index with keyphrases fields and semantically structured vectorized fields. It is imprtant to understand that the structure of the index must reflect the business logic and purpose of the end user who might search through the documents. e.g. if it is iportnat  that the information retrieved is as up to date as possible, the 'last modification' or 'last update' field could be included as one of the fields in the index to enable prioritization of newest documents in a deterministic way. 

There is a synthetic knowledge base provided in the `data_in` folder, which can be used to go through all the steps in this document. 

### [2.1 Generate synthetic documents](./2.1.-Generate-synthetic-documents/README.md)
In case it's preferred to generate a different knowledge base with other characteristics, we have provided a notebook that can be leveraged for this purpose. It contains all the prompts that were used to generate the knowledge base that is provided, but can be modified to generate data for a different use case or industry. The notebook can be found [here](./2.1.-Generate-synthetic-documents/generate-synthetic-documents.ipynb).
<!--- this link doesn't work --->

## Document analysis

The first step is determining the types of the documents and the format and structure of each document types and sub-documents.

### [2.2 Document format: Convert HTML to markdown](./2.2.-Convert-HTML-to-markdown/README.md)

Every type of document could be in different format, as simple HTML, complex HTML with style tags, JSON, XML, etc.

If the original document is comprised of **HTML files that contain numerous style tags**, it could potentially be processed by the LLM and reformatted to the right style to build a response, but it is a good practice to clean the data and index only the semantically relevant content to optimize from a token usage perspective as well as to ensure this is not introducing noise in the final answer.

Here are the [details](./2.2.-Convert-HTML-to-markdown/README.md) and the code snippet.

### [2.3 Document format: Length of the documents](./2.3.-Length-of-the-documents/README.md)

Another important aspect to assess is the length of the documents and paragraphs or sections in them. This is defined by number of tokens, which are fundamental units of text processed by language models, so for this analysis we will investigate token distribution across the document collection. There is no standard recommendation based on document length, it needs to be assessed for the specific use case and validate different strategies to find the most suitable one.

Here are the [details](./2.3.-Length-of-the-documents/README.md) and the code snippet.

### [2.4 Sub-document (or section) analysis](./2.4.-Sub-document-analysis/README.md)

In the section above we looked at token distribution for complete documents, which we re-built by combining the corresponding sections for each unique document identification. We will now look into the separate sub-documents (or sections) to provide insights on what they contain as specific unit of information.

Here are the [details](./2.4.-Sub-document-analysis/README.md) and the code snippet.

### [2.5. Duplicate documents](./2.5.-Duplicate-documents/README.md)

In this section we analyze the appearance of very similar or duplicated documents that require a thorough review in order to potentially be removed or consolidated as a single document.

Here are the [details](./2.5.-Duplicate-documents/README.md) and the code snippet.
