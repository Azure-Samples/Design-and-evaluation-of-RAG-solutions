import ast
import concurrent.futures
import json
import os
import pandas as pd
import re
import time

from azure.ai.documentintelligence.models import ContentFormat
from azure.search.documents import SearchClient
from azure.search.documents import SearchIndexingBufferedSender
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SimpleField, SearchFieldDataType, SearchableField, SearchField, VectorSearch, HnswAlgorithmConfiguration,
    VectorSearchProfile, SemanticConfiguration, SemanticPrioritizedFields, SemanticField, SemanticSearch,
    SearchIndex, VectorSearchAlgorithmKind, HnswParameters, VectorSearchAlgorithmMetric
)
from azure.search.documents.models import VectorizedQuery, VectorFilterMode, QueryType, QueryCaptionType, QueryAnswerType
from bs4 import BeautifulSoup
from langchain_text_splitters import TokenTextSplitter

from .text_functions import cut_max_tokens, extract_text

THRESHOLD_CONFIDENCE = 90

# Send a call to the model deployed on Azure OpenAI
def call_aoai(aoai_client, aoai_model_name, system_prompt, user_prompt, temperature, max_tokens):
    messages = [{'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}]
    try:
        response = aoai_client.chat.completions.create(
            model=aoai_model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        json_response = json.loads(response.model_dump_json())
        response = json_response['choices'][0]['message']['content']
    except Exception as ex:
        print(ex)
        response = None

    print(f'RESPONSE: {response}')

    return response


# Semantic Hybrid Search with filter (the filter is optional)
# Create first the index and upload documents with 'create_index_and_index_documents.ipynb'
def semantic_hybrid_search_with_filter(search_client: SearchClient, query: str, aoai_embedding_client, embedding_model_name, embedding_fields, max_docs, select_fields, filter=''):
    # Semantic Hybrid Search

    embedding = aoai_embedding_client.embeddings.create(input=query, model=embedding_model_name).data[0].embedding
    vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=max_docs, fields=embedding_fields)

    if filter == '':
        results = search_client.search(
            search_text=query,
            vector_queries=[vector_query],
            select=select_fields,
            query_type=QueryType.SEMANTIC,
            semantic_configuration_name='semantic-config',
            query_caption=QueryCaptionType.EXTRACTIVE,
            query_answer=QueryAnswerType.EXTRACTIVE,
            include_total_count=True,
            top=max_docs
        )
    else:
        results = search_client.search(
            search_text=query,
            vector_queries=[vector_query],
            select=select_fields,
            query_type=QueryType.SEMANTIC,
            semantic_configuration_name='semantic-config',
            query_caption=QueryCaptionType.EXTRACTIVE,
            query_answer=QueryAnswerType.EXTRACTIVE,
            include_total_count=True,
            top=max_docs,
            vector_filter_mode=VectorFilterMode.PRE_FILTER,
            filter=filter
        )

    return results


# Calculate the confidence and generate the 'answer' from the content
def calculate_rank(aoai_rerank_client, rerank_model_name, id, title, content, text, question):
    # Include every relevant detail from the text to ensure all pertinent information is retained.
    system_prompt = """You are an assistant that returns content relevant to a search query from an telecommunications company agent serving customers.
    Return the content needed to understand the context of the answer and only what is relevant to the search query in a field called "answer".
    Include every relevant detail from the text to ensure all pertinent information is retained.
    In your response, include a percentage between 0 and 100 in a "confidence" field indicating how confident you are the answer provided includes content relevant to the search query.
    If the user asked a question, your confidence score should be based on how confident you are that it answered the question.
    Answer ONLY from the information listed in the text below.
    Respond in JSON format as follows, for instance:
    {
        "confidence": 100,
        "answer": "Our company offers a range of telecommunication products for home customers."
    }
    """

    user_prompt = """Search Query: """ + question + """
    Text:  """ + text + """
    """
    #print(f'USER PROMPT CALCULATE RANK: {user_prompt}')
    response = call_aoai(aoai_rerank_client, rerank_model_name, system_prompt, user_prompt, 0.0, 800)

    if response is not None:
        confidence = extract_text(response, 'confidence": ', ',')
        answer = extract_text(response, 'answer": ', '\n}')
        if answer is None or answer == '':
            answer = ''
        if confidence is None or confidence == '':
            confidence = 0
    else:
        confidence = 0
        answer = ''

    return id, title, content, confidence, answer


# Generate the answer with the chunks filtered by the re-ranker
def generate_answer(aoai_answer_client, aoai_answer_model_name, texts, question, field='content'):

    system_prompt = """
        You are an assistant for a telecommunication company's agents (not for an end customer). You are replying to questions with information contained in a specific knowledge base provided.
        To carry out this task, follow these steps:
        1. It's very important that you read carefully all the Document ID, Titles and Sections of the knowledge base provided.
        2. Analyse the user Question provided.
        3. Reply to the question at step 2 using exclusively the information listed in step 1. In addition, when answering the question, follow these instructions:
            - The response should be as explanatory and orderly as possible, as it will contain the steps to carry out certain operations.
            - If more information or clarification is needed, it will ask the agent a question to disambiguate and give the correct information.
            - You must refrain from making up any information and ensure not to respond with data not explicitly mentioned in the provided knowledge base.
            - If your are not confident that the context is answering the query, please answer:
                "No tengo suficiente información par responder a la pregunta, quizas si la reformulalas, podré encotnrar la respuesta"
            - Do not refer to any telephone channel at the end of the answer, remember that you are talking with an agent now, not with an end customer.
            - Avoid any kind of profanity.
            - Avoid expressions of regret, or admission of errors in your responses.
            - Ensure that responses are concise and to the point, incorporating only the necessary information.
            - Use assertive statements.
            - It is better to give less but more useful information than a lot of information about the asked question.
            - Make a list of bullet points things whenever it is possible, so you dont give extra information.
            - Under no circumstances should references to websites or the provision of phone numbers be included in the responses.
            - It is essential to avoid any mention that could lead agents to seek information outside of the provided documents or suggest direct contact through external services to a telecommunication company.
            - Focus solely on the content of the supplied documents, without facilitating external points of contact.
            - Each response must rigorously adhere to the sequence of information exactly as it is laid out in the documents.
            - It is imperative to maintain this order with utmost precision, as any deviation or rearrangement of the information could lead to inaccuracies and misinterpretations.
            - Under no circumstances is altering the order of information acceptable, as doing so compromises the accuracy and reliability of the provided guidance.
                This requirement applies to all responses, not only for procedures or lists but for every piece of information shared.
                Each answer must reflect the order and structure of the information in the documents without alterations, even if the question does not specify a procedure or list.
            - Do not be verbose and add only the necessary information in the response.
            - Whenever you give any price in the response, specify if that price is with IVA (VAT) or without IVA. This information should be searched for in the document.
            If the document does not specify whether the price includes IVA, it must be explicitly stated that the inclusion of IVA is not clear.
            - When providing responses, it is essential to use language and terminology that directly mirror those found within the source documents.
                The use of exact words and terms from the documents is crucial for preserving the fidelity of the information and facilitating clear, unambiguous communication with the agents.
            - Do not include any text between [] or <<>> in your search terms.
            - Do not exceed 1200 characters.
        4. After generating the answer, identify the document ID or IDs used in the response by referring to the documents from step one. The answer may come from one or more document IDs.
        5. Integrate at the start and at the end of EVERY sentence or paragraph of the response the identified document ID or IDs, using this format: ((ID)).
            Important: Ensure that the selected document ID or IDs belong to the provided sections. Do not invent or use other document IDs that are not part of the given sections.
            Here two examples on how to integrate the document ID:
                - Response before integrating document ID: Las líneas móviles extras incluidas en Fusión se facturan de manera unificada en la factura Fusión.
                    Sin embargo, los módulos y opciones de TV Satélite se facturan fuera de Movistar.
                - Response after integrating document ID: ((709094)) Las líneas móviles extras incluidas en Fusión se facturan de manera unificada en la factura Fusión.
                    Sin embargo, los módulos y opciones de TV Satélite se facturan fuera de Movistar. ((709094))
                - Response before integrating document ID: Para acceder al Configurador de las Islas, hay dos opciones: a través del banner NBA o pinchando directamente en Configurador.
                    Una vez dentro, se debe introducir la dirección del cliente para hacer la consulta de cobertura y zonificación.
                    El configurador mostrará las ofertas adecuadas a la cobertura y zonificación de la dirección del cliente.
                - Response after integrating document ID: ((566754)) Para acceder al Configurador de las Islas, hay dos opciones: a través del banner NBA o pinchando directamente en Configurador.
                    Una vez dentro, se debe introducir la dirección del cliente para hacer la consulta de cobertura y zonificación.
                    ((566754)) ((896732)) El configurador mostrará las ofertas adecuadas a la cobertura y zonificación de la dirección del cliente. ((896732))
    """

    user_prompt = """Knowledge base:\n"""
    for text in texts:
        user_prompt = user_prompt + f"Document ID: {text['id']}. Title: {text['title']}. Section: {text[field]}\n"
    user_prompt = user_prompt + "\nQuestion: " + question + "\nFinal Response:"

    #print(f'USER PROMPT: {user_prompt}')

    return call_aoai(aoai_answer_client, aoai_answer_model_name, system_prompt, user_prompt, 0.0, 800)


# Re-ranker: calculate in parallel the percentage of confidence and the answer comparing with the query
def get_filtered_chunks(aoai_rerank_client, rerank_model_name, results, query, max_docs):
    i = 1
    chunks = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_docs) as executor:
        futures = []
        for result in results:
            text = f"{result['title']}. {result['content']}"
            futures.append(executor.submit(calculate_rank, aoai_rerank_client, rerank_model_name, result['id'], result['title'], result['content'], text, query))

        for future in concurrent.futures.as_completed(futures):
            id, title, content, confidence, answer = future.result()
            print(f'\ttitle: {title}, confidence: {confidence}, \n\tanswer: {answer}')
            if int(confidence) >= THRESHOLD_CONFIDENCE:
                chunks.append({
                    "id": int(id),
                    "title": title,
                    "content": content,
                    "confidence": int(confidence),
                    "answer": answer
                    }
                )

            i += 1
            if i == max_docs:
                break

    return chunks


# Convert HTML to markdown format with Document Intelligence
def get_markdown_with_doc_intel(doc_intel_client, content):

    if content is None:
        return None

    # Create a temporal file with the content to convert in HTML format
    output_path = 'temp.html'
    with open(output_path, "w", encoding='utf-8') as f:
        f.write(content)

    # Read the temporal file
    with open(output_path, "rb") as file:
        html_content = file.read()

    try:
        # Convert to markdown with Document Intelligence
        poller = doc_intel_client.begin_analyze_document("prebuilt-layout",
                                                        analyze_request=html_content,
                                                        output_content_format=ContentFormat.MARKDOWN,
                                                        content_type="application/octet-stream")
        result = poller.result()
        markdown = result['content']

    except Exception as ex:
        print(ex)
        # If Document Intelligence fails to convert HTML to markdown, use Beautiful soap
        soup = BeautifulSoup(html_content, "html.parser")
        markdown = soup.get_text()

    return markdown


# Chunking with Langchain and tiktoken
def chunk_with_max_tokens(text, max_tokens, overlap):
    # Langchain text chunking with tiktoken client, specifing maximum number of tokens and number of token of overlapping
    text_splitter = TokenTextSplitter(
        chunk_size=max_tokens,
        chunk_overlap=int(max_tokens * overlap))

    chunks = text_splitter.split_text(text)

    return chunks


# Chunk text with GPT-4o
def generate_chunks_with_aoai(aoai_client, aoai_model_name, text, max_chunk_token_size):

    system_prompt = f"""Analyze the document provided and divide it into distinct sections where each section contains information that can answer typical customer questions for a Telco scenario.
    Group related topics together to form semantically coherent chunks.
    Ensure that each chunk is concise enough to stay within the token limits of the model, with a maximum of {max_chunk_token_size} tokens,
    but comprehensive enough to provide a thorough answer to potential customer inquiries.
    If there are chunks with a size less than 100 tokens put them together in the same chunk.
    Additionally, label each chunk with a descriptive title based on its content to facilitate easy navigation and reference.
    The response has to be in the same language than the document.
    Respond with a format as follows with a line per title and chunk pair generated. For instance:
    title: "Informacion sobre Datos (Móvil)",
        "chunk": "Cliente que necesita estar constantemente conectado a Internet (p ej un agente de bolsa que trabaja en movilidad, un comercial que hace los pedidos contra el stock del almacén?).
        En este caso le interesa el contrato Plus Datos / Plus Datos UMTS, opcionalmente para este último podrá contratar el Módulo C  o la Tarifa plana datos."
    title: "Descripción de Internet",
        "chunk": "Internet es una red compuesta de páginas Web a la que se accede desde un PC (y desde determinados modelos de terminales o PDA´s )
        utilizando un móvil como módem mediante un cable de conexión, puerto de infrarrojos o bluetooth o con una tarjeta PCMCIA."
    """
    user_prompt = f'Document: "{text}"'

    response = call_aoai(aoai_client, aoai_model_name, system_prompt, user_prompt, 0.5, 4096)
    print(f'RESPONSE: [{response}]')

    if response is not None:
        # GPT-4-0409: Parse answer with ", " as the separator between title and chunk
        pattern = r'title: "(.*?)", chunk: "(.*?)"'
        matches = re.findall(pattern, response)
        # Extract values of title and chunk from the response
        chunks = [match[1] for match in matches]

        data = [{"title": match[0], "content": match[1]} for match in matches]

        for chunk in data:
            print(f'chunk: {chunk}')

        return chunks
    else:
        return None


# Create AI Search index
def create_index(ai_search_endpoint, ai_search_credential, index_name, embedding_model_name):

    # Create an Azure AI Search index client
    index_client = SearchIndexClient(endpoint=ai_search_endpoint, credential=ai_search_credential)

    if embedding_model_name == 'ada':
        dimensions = 1536
    else:
        dimensions = 3072
    # Fields definition
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchField(name="embeddingTitle", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True, vector_search_dimensions=dimensions, vector_search_profile_name="myHnswProfile"),
        SearchField(name="embeddingContent", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True, vector_search_dimensions=dimensions, vector_search_profile_name="myHnswProfile")
    ]

    # Configure the vector search configuration
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="myHnsw",
                kind=VectorSearchAlgorithmKind.HNSW,
                parameters=HnswParameters(
                    m=4,
                    ef_construction=400,
                    ef_search=500,
                    metric=VectorSearchAlgorithmMetric.COSINE
                )
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="myHnswProfile",
                algorithm_configuration_name="myHnsw",
            )
        ]
    )

    # Semantic ranker configuration
    semantic_config = SemanticConfiguration(
        name="semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="title"),
            content_fields=[SemanticField(field_name="content")]
        )
    )

    # Create the semantic settings with the configuration
    semantic_search = SemanticSearch(configurations=[semantic_config])

    # Create the search index with the semantic settings
    index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search, semantic_search=semantic_search)
    result = index_client.create_or_update_index(index)
    print(f'Index {result.name} created')


# Index documents in the Azure AI Search index
# Index the batch in Azure AI Search index
def index_lote(batch_client, lote, i):
    try:
        print(f'Indexing until document {i}...')
        batch_client.upload_documents(documents=lote)
        print('Waiting 15 seconds...')
        time.sleep(15)
    except Exception as ex:
        print(ex)


# Index the chunks in files
def index_documents(ai_search_endpoint, ai_search_credential, index_name, embedding_client, embedding_model_name, chunk_contents):

    # Create an index batch client
    batch_client = SearchIndexingBufferedSender(
                endpoint=ai_search_endpoint,
                index_name=index_name,
                credential=ai_search_credential
            )

    lote = []
    for i, chunk_content in enumerate(chunk_contents):  # Index the chunks using the file name as title
        #print('=================================================================')
        title = chunk_content['title']
        content = chunk_content['content']
        print(f"[{i + 1}]: title: {title}")
        #print(f"\t[{content}]")
        document = {
            "id": str(i),
            "title": title,
            "content": content,
            # Create embeddings with ADA-2
            "embeddingTitle": embedding_client.embeddings.create(input=cut_max_tokens(title), model=embedding_model_name).data[0].embedding,
            "embeddingContent": embedding_client.embeddings.create(input=cut_max_tokens(content), model=embedding_model_name).data[0].embedding,
        }
        # Add the document to the batch
        lote.append(document)
        # Index every 10 documents in the batch
        if (i + 1) % 10 == 0:
            # Upload documents
            print(f'INDEXING BATCH {i + 1}')
            index_lote(batch_client, lote, i)
            lote = []

    # Index the rest of documents after the last batch
    if len(lote) > 0:
        index_lote(batch_client, lote, i)


# Create the Excel file with question and answer pairs to evaluate the answers generated
def generate_answers_and_questions(aoai_client, aoai_model_name, text):

    system_prompt = """
    Your mission is to generate questions and answers targeting the context provided with the following format:
    "question": "text of the question", "answer": "text of the answer"
    The answers and questions pairs has to be in the same language than the Context.
    Here you have some examples of context and the question and answer pairs as your response in json format:
    Context: Sarah found a lost kitten on the street and decided to take it home.
    Response:
    [
        {"question": "why did Sarah decide to take the kitten home?",
         "answer": "the kitten was lost"},
        {"question": "where did Sarah find the kitten?",
         "answer": "on the street"},
    ]
    Context: Jack saw a friendly group of kids playing in the park, so he decided to join them.
    Response:
    [
        {"question": "why did Jack decide to join the group of kids playing in the park?",
         "answer": "the group of kids was friendly"},
        {"question": "what were the group of kids doing?",
         "answer": "playing in the park"}
    ]
    """

    user_prompt = f'Context: "{text}". Response: '

    response = extract_text(call_aoai(aoai_client, aoai_model_name, system_prompt, user_prompt, 0.5, 4096), '```json', '```')

    qa_list = []
    if response is not None:
        qa_pairs = json.loads(response)
        i = 1
        for qa_pair in qa_pairs:
            print(f'\t[{i}]: question: [{qa_pair["question"]}]')
            print(f'\t answer: [{qa_pair["answer"]}]')
            qa_list.append(qa_pair)
            i += 1

    return qa_list


# Evaluate answer quality
def evaluate_answer(aoai_answer_client, aoai_answer_model_name, question, correct_answer, answer):
    system_prompt = """You are an AI assistant that helps people validate the accuracy and completeness of a response against a ground trust.
    Given the user's question, the expected ground truth answer and the current answer generated by a RAG pattern,
    compare the meaning of both answers and assess if the current answer addresses the user's question.
    Then select a number that best describes this assessment considering the following guidelines:
    - 0: The generated answer and the expected answer have completely different meanings
        The generated answer does not address the user's question.
    - 1: The generated answer is very similar in meaning to the expected answer but lacks some crucial information, and it partially addresses the user's question.
    - 2: The generated answer is well-aligned with the expected answer, capturing the main points accurately, and fully addressing the user's question.
    - 3: The generated answer not only aligns with the expected ground truth and answers the user's question but also adds valuable additional details or insights.
    Based on these guidelines, provide only the number that best represents the relationship between the generated answer and the expected ground truth answer.
    Do not include any explaination, only the number.
    """

    user_prompt = f'\nQuestion: {question}\nExpected Ground Truth Answer: "{correct_answer}\nGenerated Answer: "{answer}"\n"\nYour evaluation: '

    return call_aoai(aoai_answer_client, aoai_answer_model_name, system_prompt, user_prompt, 0.0, 800)


# Execute all the defined search tests
def execute_test(ai_search_endpoint,
                 ai_search_credential,
                 select_fields,
                 aoai_rerank_client,
                 rerank_model_name,
                 aoai_answer_client,
                 aoai_answer_model_name,
                 test_name,
                 embedding_fields,
                 case,
                 embedding_model,
                 embedding_client,
                 index_name,
                 max_retrieve,
                 max_generate,
                 q_a_filename_in):

    dir_out = "data_out"
    os.makedirs(dir_out, exist_ok=True)
    data_in = pd.read_excel(q_a_filename_in)

    print(f'test_name: {test_name}')
    print(f"\t embeddings_fields: {embedding_fields}")
    print(f"\t case: {case}")
    print(f"\t embedding_model: {embedding_model}")
    print(f"\t index_name: {index_name}")
    print(f"\t max_retrieve: {max_retrieve}")
    print(f"\t max_generate: {max_generate}")

    data_out = {
            'QUESTION': [],
            'EXPECTED_ANSWER': [],
            'ANSWER_WITH_ANSWERS': [],
            'EVALUATION_GPT_AA': [],
            'ANSWER_WITH_CHUNKS': [],
            'EVALUATION_GPT_AC': []
                }

    # Create Azure AI Search client
    ai_search_client = SearchClient(endpoint=ai_search_endpoint, index_name=index_name, credential=ai_search_credential)

    # FOR EVERY Q&A FILE IN THE INPUT FILE
    for index, row in data_in.iterrows():
        print(f"Row {index + 1}: =====================================================")

        user_question = row["question"]
        if case == 'upper':
            user_question = user_question.upper()
        else:
            user_question = user_question.lower()

        respuesta_best = row["answer"]

        data_out['QUESTION'].append(user_question)          # EXCEL COLUMN: QUESTION
        data_out['EXPECTED_ANSWER'].append(respuesta_best)  # EXCEL COLUMN: EXPECTED_ANSWER

        # SEMANTIC HYBRID SEARCH
        results = semantic_hybrid_search_with_filter(ai_search_client,
                                                     user_question.lower(),
                                                     embedding_client,
                                                     embedding_model,
                                                     embedding_fields,
                                                     max_retrieve,
                                                     select_fields)

        # Re-rank the chunks
        data = get_filtered_chunks(aoai_rerank_client, rerank_model_name, results, user_question, max_retrieve)
        # If the max number of docs to retrieve is higher than max number of docs to use in answer generation
        # sort them by confidence and leave only the max number of docs to generate
        if max_retrieve > max_generate:
            if data is not None:
                sorted_data = sorted(data, key=lambda x: x.get('confidence', float('-inf')), reverse=True)
                data = sorted_data[:max_generate]

        ids_in_search_results = ""
        for result in results:
            ids_in_search_results = ids_in_search_results + ' ' + result['id']

        # Si quedan contenidos para generar la respuesta
        if data != []:
            # ANSWER_WITH_ANSWERS: Generate the answer with the answers generated by the re-ranker with filtered chunks
            answer = generate_answer(aoai_answer_client, aoai_answer_model_name, data, user_question, 'answer')
            print(f'RESPONSE WITH ANSWERS: [{answer}]')
            data_out['ANSWER_WITH_ANSWERS'].append(answer)
            data_out['EVALUATION_GPT_AA'].append(evaluate_answer(aoai_answer_client, aoai_answer_model_name, user_question, respuesta_best, answer))
            print('------------------------------------------------------------------')

            # ANSWER_WITH_CHUNKS - Generate the answer with the chunks filtered by the re-ranker
            answer = generate_answer(aoai_answer_client, aoai_answer_model_name, data, user_question, 'content')
            print(f'RESPONSE WITH CHUNKS: [{answer}]')
            data_out['ANSWER_WITH_CHUNKS'].append(answer)
            data_out['EVALUATION_GPT_AC'].append(evaluate_answer(aoai_answer_client, aoai_answer_model_name, user_question, respuesta_best, answer))

            print('------------------------------------------------------------------')

        else:
            answer = 'There is not any content to generate the answer'
            data_out['ANSWER_WITH_ANSWERS'].append(answer)
            data_out['EVALUATION_GPT_AA'].append(0)
            data_out['ANSWER_WITH_CHUNKS'].append(answer)
            data_out['EVALUATION_GPT_AC'].append(0)

        if index > 5:
            break

    # Excel file with the results
    df = pd.DataFrame(data_out)
    filename_out = dir_out + '/' + test_name + '.xlsx'
    print(f'Writting file {filename_out}')
    df.to_excel(filename_out, index=False, header=True)


# Generate a list of topics for the synthetic documents and Generate documents based on that list of topics
def generate_topics_and_documents(aoai_client, model_deployment_name, company_name, company_industry, output_folder):
    # Generate a list of topics for the synthetic documents
    prompt = f'''
    You are an AI that generates documents for customer service agents working at {company_name} (a {company_industry} company).
    You help them understand how to support customers with specific questions.
    Generate a list of 200 topics of documents that could be created to help customer service agents.
    Each topic should be a short description of the document's content.
    The topics should cover a wide range of customer queries and issues that agents might encounter.
    The topics should be relevant to the {company_industry} industry and provide useful information for agents to assist customers effectively.
    The topics should be clear, concise, and informative, helping agents quickly understand the content of each document.
    The output should be a python array in the following format:
    [
        "How to reset a customer's modem",
        "Troubleshooting weak Wi-Fi signals",
        "Upgrading a customer's internet plan",
        "Explaining data overage charges",
        ...
    ]
    DO NOT INCLUDE ANY MARKDOWN FORMATTING.
    '''

    response = aoai_client.chat.completions.create(
        model=model_deployment_name,
        messages=[
            {"role": "system", "content": prompt}
        ],
    )

    topics = ast.literal_eval(response.choices[0].message.content)
    print(topics)

    # Generate documents based on that list of topics
    prompt = f'''
    You are an AI that generates documents for customer service agents working at {company_name} (a {company_industry} company).
    You help them understand how to support customers with specific questions.
    The output should be an html file that contains documentation on a specific customer query.
    Use html tables, lists, etc as appropriate and make it look pretty. The document should be easy to read and understand.
    DO NOT INCLUDE ANY MARKDOWN FORMATTING IN THE OUTPUT.
    Make sure the document includes at least 1000 words of content.
    The topic for this document is:
    '''

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i in range(len(topics)):
        print(topics[i])
        prompt_topic = f"{prompt} {topics[i]}"
        response = aoai_client.chat.completions.create(
            model=model_deployment_name,
            messages=[
                {"role": "system", "content": prompt_topic}
            ],
            max_tokens=2000
        )
        document = response.choices[0].message.content

        filename = f"{output_folder}/{topics[i].replace(' ', '_')}.html"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(document)

        print(f"\tDocument {i+1} saved as {filename}")


# Create variants of documents to simulate duplicates
def create_duplicate_documents(aoai_client, model_deployment_name, company_name, company_industry, output_folder):
    prompt = f'''
    You are an AI that generates variants of documents for customer service agents working at {company_name} (a {company_industry} company).
    YOu help them understand how to support customers with specific questions.
    The output should be a variant of the original document's content.
    The variant should provide alternative ways of explaining the same information or offer additional tips and suggestions.
    The variant should be relevant to the {company_industry} industry and provide useful information for agents to assist customers effectively.
    The variant should be clear, concise, and informative, helping agents quickly understand the content of each document.

    DO NOT INCLUDE ANY MARKDOWN FORMATTING.
    '''

    for filename in os.listdir(output_folder)[0:5]:
        if filename.endswith('.html'):
            with open(f'{output_folder}/{filename}', 'r', encoding='utf-8') as file:
                document = file.read()

            prompt_topic = f"{prompt} {document}"
            response = aoai_client.chat.completions.create(
                model=model_deployment_name,
                messages=[
                    {"role": "system", "content": prompt_topic}
                ],
                max_tokens=1000
            )
            variant = response.choices[0].message.content
            print(variant)
            variant_filename = f"{output_folder}/{os.path.splitext(filename)[0]}_2.html"
            with open(variant_filename, 'w', encoding='utf-8') as file:
                file.write(variant)
