## 5.2. Automatic generation of synthetic Q&A pairs

A good option to create a relevant evaluation dataset is to automatically generate synthetic question-and-answer pairs from complete documents (including all sub-documents/sections). This allows end-to-end testing without having to manually generate each question one by one. The generated questions and answers pairs should be reviewed and improved by the business area and the final version should be added to the test set.

The prompts that we used to generate questions and answers pair from documents are the following:

**System prompt:** _"Your mission is to generate questions and answers targeting the context provided with the following JSON format:_

_\[_

_{"question": "text of the question", "answer": "text of the answer"}_

_\]_

_Generate the answers and questions in the same language than the context._

_Here you have some examples:_

_Context: Sarah found a lost kitten on the street and decided to take it home._

_Response:_
_\[_
_{"question": "why did Sarah decide to take the kitten home?", "answer": "the kitten was lost"},_
_{"question": "where did Sarah find the kitten?", "answer": "on the street"}_
_\]_

_Context: Jack saw a friendly group of kids playing in the park, so he decided to join them._

_Response:_
_\[_
_{"question": "why did Jack decide to join the group of kids playing in the park?", "answer": "the group of kids was friendly"},_
_{"question": "what were the group of kids doing?", "answer": "playing in the park"}_
_\]”_

**User prompt:** “Context: \[text\]”

Include an example of the questions and answers pairs generated and the rest in the appendix.

| **Document (in markdown format):** |
| --- |
| **Response (question and answer pairs):**<br><br>question:<br><br>answer:<br><br>question:<br><br>answer:<br><br>question:<br><br>answer: |

**Code Snippet:**
[generate_synthetic_qa_pairs.ipynb](./generate_synthetic_qa_pairs.ipynb)