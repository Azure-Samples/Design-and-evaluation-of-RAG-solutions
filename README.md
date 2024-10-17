# 1. Design and evaluation of a RAG implementation

The purpose of this repository is to reflect the recommendations for a RAG (Retrieval-Augmented Generation) solution following the best practices, along with tools and techniques for testing and evaluation. 

This document is divided in sections that follow the standard order of implementation for an end-to-end review of this type of solution, including an optional section to create an AI-generated collection of documents that can be used for leaning purposes.

RAG, or Retrieval Augmented Generation, is an advanced AI architecture that combines the power of information retrieval with generative AI models. The key idea is to enhance the generative AI model's output by retrieving relevant information from a collection of documents or data sources. This approach improves the accuracy and relevance of the generated content by grounding it in real-world data.

**How to use this repository**

This repository is designed as a comprehensive learning resource for building a Retrieval-Augmented Generation (RAG) implementation using Generative AI models and a search engine. Whether you're new to these concepts or looking to refine your skills, you can tailor your experience based on your needs. You have the flexibility to dive into specific sections, utilizing the specific notebooks and guidance provided to explore particular topics in depth. This approach allows you to leverage the repository's resources to address specific challenges or questions you might encounter in your projects.

Alternatively, if you're aiming for a holistic understanding of RAG implementations, you can follow the repository in a sequential manner. By proceeding through the sections in order, you'll gain a step-by-step overview of the entire process, from foundational concepts to advanced techniques. This pathway is ideal for those who want a complete end-to-end review, ensuring a thorough grasp of how to build and optimize RAG systems. Whichever approach you choose, this repository serves as a valuable educational tool to enhance your knowledge and skills in this cutting-edge area.

**Key components:**
- Retrieval: The system first retrieves relevant documents or data chunks from a database or corpus. In the case of this repository, it will retrieve document sections indexed in Azure AI Search. This step ensures that the generated responses are informed by curated information.
- Augmentation: The retrieved information is then used to augment the input to a generative model. This augmentation helps in producing contextually accurate and informative responses.
- Generation: Finally, the generative AI model, in this case Azure Open AI GPT models, generate responses or content based on the augmented input.

**How RAG works in Azure**

In this implementation, we leverage Azure AI Services to build a RAG system. The key services for this repository are:
- **Azure Open AI Service**: Provides state-of-the-art generative models capable of understanding and generating human-like text. More info: https://learn.microsoft.com/en-us/azure/ai-services/openai/
- **Azure AI Search**: A robust search service that helps retrieve relevant information from a large corpus, ensuring that the generative model has access to the most pertinent data. More info: https://learn.microsoft.com/en-us/azure/search/

The repository follows a structured process, and it is meant to be used to implement an end-to-end system as well as to only include certain components, such as testing and evaluation into an existing implementation.

The following diagram represents the reference standard process that encompasses many of the different aspects to consider for a successful implementation of this solution:

<img src="./images/RAG workflow.png" alt="architecture"/>

Table of contents
=================

<!--ts-->
   * [1. RAG Project Assurance](#1-rag-project-assurance)

   * [2. Preparation phase and document analysis](./2.-preparation-phase-and-document-analysis/README.md)

      * [2.1 Generate synthetic docs](./2.-preparation-phase-and-document-analysis/2.1.-Generate-synthetic-documents/README.md)

      * [2.2 Document format: Convert HTML to markdown](./2.-preparation-phase-and-document-analysis/2.2.-Convert-HTML-to-markdown/README.md)

      * [2.3 Document format: Length of the documents](./2.-preparation-phase-and-document-analysis/2.3.-Length-of-the-documents/README.md)

      * [2.4 Sub-document (or section) analysis](./2.-preparation-phase-and-document-analysis/2.4.-Sub-document-analysis/README.md)

      * [2.5. Duplicate documents](./2.-preparation-phase-and-document-analysis/2.5.-Duplicate-documents/README.md)

   * [3. Chunk processing](./3.-chunk-processing/README.md)

      * [3.1. Chunk documents](./3.-chunk-processing/3.1.-Semantic-Chunking-with-GPT-4o/README.md)

      * [3.2. Chunk enrichment](./3.-chunk-processing/3.2.-Chunking-with-Langchain-with-max-tokens-and-overlapping/README.md)

   * [4. Search and retrieval](./4.-search-and-retrieval/README.md)

      * [4.1. Search results re-ranking](./4.-search-and-retrieval/4.1.-Search-results-re-ranking/README.md)

   * [5. Testing and evaluation](./5.-testing-and-evaluation/README.md)

      * [5.1. Testing search results](./5.-testing-and-evaluation/5.1.-Testing-search-results/README.md)

      * [5.2. Automatic generation of synthetic Q&A pairs](./5.-testing-and-evaluation/5.2.-Automatic-generation-of-synthetic-QA-pairs/README.md)

      * [5.3. Testing end-to-end answer quality](./5.-testing-and-evaluation/5.3.-Evaluate-answer-quality/README.md)
      
      * [5.4	Testing the end-to-end process](./5.-testing-and-evaluation/5.4.-Testing-the-end-to-end-process/README.md)

   * [6. Summary of recommendations](./6.-summary-of-recommendations/README.md)

   * [7. List of code snippets](./7.-list-of-code-snippets/README.md)

   * [8. Appendices](./8.-appendices/README.md)
<!--te-->
