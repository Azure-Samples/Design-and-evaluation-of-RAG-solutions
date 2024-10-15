# 6. Summary of recommendations

In this section we structure our recommendations in two areas, the first one is related to errors or problems that we could detect in the current solution, and the second one is related to improvements that we recommend following the best practices in this kind of projects.

## 6.1. Recommendations related to issues detected

The following table includes some samples of issues that could be identified in a project with the recommendation for fixing them:

| Area of interest | Issue | Action | Potential Benefits |
| --- | --- | --- | --- |
| Data quality | Low value documents: very small, less than 50 tokens | Review them and decide to remove them or not from the knowledge base if the document can’t help the model to answer any question | Reduce the noise in the knowledge base improving the search results and avoiding using low value documents to generate the answer by the model |
|  | Low value documents classified as “TABLE-ONLY” | Review them and decide to remove them or not from the knowledge base if the document can’t help the model to answer any question | Reduce the noise in the knowledge base improving the search results and avoiding using low value documents to generate the answer by the model |
|  | Duplicated documents with a similarity of 97% or more | Review them and decide to remove them or not from the knowledge base | Reduce the noise in the knowledge base improving the search results and avoiding using low value documents to generate the answer by the model |
| Azure AI Search index configuration | Relevant fields not configured as searchable | Configure those high value fields as searchable | The data inside those fields would be used in the search so the search results will be improved |
|  | Different NLP analyzer in searchable fields | Configure the same NLP analyzer in every searchable field, es.microsoft because the content is in Spanish | Improve the search results with better NLP processing |
| User Acceptance Tests | Get a representative test set of questions with expected answers from the client’s business area | - Define with business area a more representative set of questions and the expected answer. - Generate synthetic questions and answers pairs and review them with the business area to have more questions. | To have a way to measure the improvements with changes in the solution |

## 6.2. Recommendations related to improvements

The following table includes some samples of recommendation to improve the solution:

| Area of interest | Action | Potential Benefits |
| --- | --- | --- |
| Document processing | Convert sections from html to markdown format | Better chunk and improvements of model understanding avoiding the noise of styles and html tags |
|  | Stich every sub-document/section in one document before chunking | Have a complete information unit for chunking to have a better context to generate the answers by the LLM |
| Azure AI Search index configuration and searching | Find the best vector field combination according to the search tests and quality tests to use in the Semantic Hybrid Search | Improve the search results with the vector search capabilities |
|  | Create a scoring profile setting for the most important fields (i.e. Title) with higher score when the words included in the user’s query appears in those fields. | Improve the search results giving higher score to documents that have the words included in the query in those fields |
|  | Execute the search with the user's query converted to lowercase | Improve the search results because vector fields are case sensitives, and most of the content are in lowercase |
| Re-ranker and filtering chunks before answer generation by the model | Implement the chunk evaluation and how it can help to response the user’s query, filtering the chunks with less than 90% of confidence | Reduce the number of tokens send to the model, reducing cost and time to answer and improving the answer reducing low value chunks to response the question |
| Chunking technique | Implement the chunking technique according to the test results. | Generate more answers well aligned with the ground-truth (expected answers defined by the business area) |
| Answer evaluation | Implement an objective technique to evaluate the quality of answer, as Azure AI Studio using a csv with the Question, Context (the chunks), Answer generated and Ground truth (expected answer) | To have a way to measure the improvements with changes in the solution |
| Automatic question and answer generation for testing | Create synthetic questions and answers pairs from complete documents (stitched sections) to execute automatic testing of generated answers quality | To have an incremental and automatic testing environment that will help to review generated answer quality avoiding the dependency with business area |
