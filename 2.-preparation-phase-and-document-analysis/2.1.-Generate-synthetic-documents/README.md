## 2.1. Generate synthetic documents

A good option to create a relevant content dataset for testing is to automatically generate synthetic documents for the specific sector of the customer.
In this repo there is a content dataset related to a telecommunication company in the folder 'data_in', but with this code you can generate content for testing related to your customer.
This allows end-to-end testing without having to manually generate each document.
The generated content in html should be reviewed and improved by the business area and the final version should be added to the test set.

The prompts that we used to generate html documents are the following:
First we generate the topics with this system prompt:

    You are an AI that generates documents for customer service agents working at {company_name} (a {company_industry} company) that helps them understand how to support customers with specific questions. Generate a list of 200 topics of documents that could be created to help customer service agents. Each topic should be a short description of the document's content. The topics should cover a wide range of customer queries and issues that agents might encounter. The topics should be relevant to the {company_industry} industry and provide useful information for agents to assist customers effectively. The topics should be clear, concise, and informative, helping agents quickly understand the content of each document.
    The output should be a python array in the following format: 
    [
        "How to reset a customer's modem",
        "Troubleshooting weak Wi-Fi signals",
        "Upgrading a customer's internet plan",
        "Explaining data overage charges",
        ...
    ]
    DO NOT INCLUDE ANY MARKDOWN FORMATTING.

and then we generate the documents with this system prompt:

    You are an AI that generates documents for customer service agents working at {company_name} (a {company_industry} company) that helps them understand how to support customers with specific questions. The output should be an html file that contains documentation on a specific customer query. Use html tables, lists, etc as appropriate and make it look pretty. The document should be easy to read and understand. DO NOT INCLUDE ANY MARKDOWN FORMATTING IN THE OUTPUT.
    Make sure the document includes at least 1000 words of content.
    The topic for this document is:

**Code Snippet:**
[generate-synthetic-documents.ipynb](./generate-synthetic-documents.ipynb)