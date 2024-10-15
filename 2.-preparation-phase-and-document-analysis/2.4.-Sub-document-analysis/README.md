### 2.4. Sub-document (or section) analysis

In the section above we looked at token distribution for complete documents, which we re-built by combining the corresponding sections for each unique document identification. We will now look into the separate sub-documents (or sections) to provide insights on what they contain as specific unit of information.

A deep analysis of every section using a prompt with GPT-4o will help us to identify three categories of content. The purpose of this task is to identify those sections that might contain tables without context, making it complex for the model to correctly process and answer based on them. We have classified them in the following categories:

- **TABLE-ONLY:** documents that contain only a table with no description that provides context to the model, so potentially it could not help the model to answer any question and should be reviewed to decide to remove or not from the knowledge base.
- **TABLE-WITH-CONTEXT:** documents that contains a table and some context that could help the model to understand the data inside the table and could help it to answer user’s questions.
- **TEXT-ONLY:** documents that contains only text, without a table.

The prompts for this analysis are the following:

**System prompt:** "You have to detect in this document a table and identify if there is any context or description that describes the meaning of the table. The context could be inside or outside of the table. The context will be a sentence with several or paragraph. If there is only a table with no context nor description return 'TABLE-ONLY', if there is no table at all return 'TEXT-ONLY', and if there is a table with context or description return 'TABLE-WITH-CONTEXT'. Add the explanation of your decision. Your answer must be with this format, one line per document: Type, Explanation."

**User prompt:** “Document: \[text\]”

The distribution of those categories of content in every section will be reflected in a table like this:

| Category | Document type A | Document type B |
| --- | --- | --- |
|  | Count - Percentage | Count - Percentage |
| TABLE-ONLY | 999 - 9,99% | 999 - 9,99% |
| TABLE-WITH-CONTEXT | 999 - 9,99% | 999 - 9,99% |
| TEXT-ONLY | 999 - 9,99% | 999 - 9,99% |

We recommend reviewing the different types of tables to define a scalable way to process them so that they are linked to the necessary context for a correct answer.

An additional consideration from these insights is that working with (sub-documents) sections instead of complete documents might be causing information loss, especially in sections that contain only tables.

**Code Snippet:**
[classify_markdown_content.ipynb](./classify_markdown_content.ipynb)