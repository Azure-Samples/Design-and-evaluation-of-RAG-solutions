#### 3.1. Semantic Chunking with GPT-4o

We have used the following prompts to do semantic chunking (replace “Telco” for the client’s sector):

**System prompt:** Analyze the document provided and divide it into distinct sections where each section contains information that can answer typical customer questions for a Telco scenario. Group related topics together to form semantically coherent chunks. Ensure that each chunk is concise enough to stay within the token limits of the model, with a maximum of 512 tokens, but comprehensive enough to provide a thorough answer to potential customer inquiries. If there are chunks with a size less than 100 tokens put them together in the same chunk.

Additionally, label each chunk with a descriptive title based on its content to facilitate easy navigation and reference. The text will be in Spanish so answer also in Spanish.

Respond with a format as follows with a line per title and chunk generated. For instance:

title: "Informacion sobre Datos (Móvil)", chunk: "Cliente que necesita estar constantemente conectado a Internet (p ej un agente de bolsa que trabaja en movilidad, un comercial que hace los pedidos contra el stock del almacén?) En este caso le interesa el contrato Plus Datos / Plus Datos UMTS, opcionalmente para este último podrá contratar el Módulo C  o la Tarifa plana datos."

title: "Descripción de Internet", "chunk": "Internet es una red compuesta de páginas Web a la que se accede desde un PC (y desde determinados modelos de terminales o PDA´s ) utilizando un móvil como módem mediante un cable de conexión, puerto de infrarrojos o bluetooth o con una tarjeta PCMCIA."

**User prompt:** “Document: \[text\]”

**Code Snippet:**
[semantic_chunking_with_aoai.ipynb](./semantic_chunking_with_aoai.ipynb)