### 2.5. Duplicate documents

In this section we analyze the appearance of very similar or duplicated documents that require a thorough review in order to potentially be removed or consolidated as a single document.

We used the following technique:

1. Stitch every section inside a document in markdown format into one document.
2. Calculate embedding of every document and index in a vector field in an index of Azure AI Search.
3. Iterating by every document vectorized and search it in the Azure AI Search index with a minimum score of 97% of similarity.

The results will be a table like this:

| Scope | Total documents | Possible duplicate count (97% of similarity) | Percentage |
| --- | --- | --- | --- |
| Document type A | 99.999 | 9999 | 99,99% |
| Document type B | 99.999 | 9999 | 99,99% |

As an example, highlight some documents from a document type that are very similar:

- Document ID: XXXXX, Title: “Lorem ipsum dolor sit amet - 01/06/2024”
- Document ID: XXXXX, Title: “Lorem ipsum dolor sit amet - 20/05/2024”

And include the complete list of possible duplicate documents of each document types in the appendix.

**Code Snippet:**
First create the Azure AI Search index and index sample documents: [create_index_and_index_documents.ipynb](../../4.-search-and-retrieval/4.1.-create-index-and-index-documents/create_index_and_index_documents.ipynb)

and then look for duplicate documents: [find_duplicates.ipynb](./find_duplicates.ipynb)