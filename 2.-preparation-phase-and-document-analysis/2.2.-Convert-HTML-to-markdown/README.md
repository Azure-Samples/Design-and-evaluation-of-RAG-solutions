#### 2.2. Document format: Convert HTML to markdown

Every type of document could be in different format, as simple HTML, complex HTML with style tags, JSON, XML, etc.

If the original document is comprised of **HTML files that contain numerous style tags**, it could potentially be processed by the LLM and reformatted to the right style to build a response, but it is a good practice to clean the data and index only the semantically relevant content to optimize from a token usage perspective as well as to ensure this is not introducing noise in the final answer.

Sample of a complex HTML document with style tags:

_"&lt;html&gt; &lt;head&gt; &lt;title&gt;Description&lt;/title&gt; &lt;link href=\\"\\" rel=\\"stylesheet\\" type=\\"text/css\\" /&gt; &lt;/head&gt; &lt;body&gt; &lt;br&gt; &lt;table width=\\"100%\\" border=\\"0\\" cellpadding=\\"0\\" cellspacing=\\"0\\" bordercolor=\\"#eeeeec\\"&gt; &lt;tr&gt; &lt;td bgcolor=\\"#FFFFFF\\" class=\\"contenido\\"&gt; &lt;p&gt;&lt;img src=\\"\\" alt=\\"Text\\" width=\\"4\\" height=\\"4\\" /&gt; Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis interdum, sem nec commodo convallis, urna risus volutpat lacus, at volutpat ligula massa vitae ligula.&lt;/p&gt; &lt;p&gt; &lt;img src=\\"\\" alt=\\"Text\\" width=\\"4\\" height=\\"4\\" /&gt; Maecenas tincidunt iaculis sollicitudin.&lt;/p&gt; &lt;ol&gt; &lt;li&gt; Sed eu magna at dolor porta luctus.&lt;/li&gt; &lt;li&gt; Curabitur egestas ex et nibh mattis, eget maximus turpis molestie. &lt;/li&gt; &lt;li&gt; Proin placerat molestie efficitur. &lt;/li&gt; &lt;li&gt; Vivamus at odio non augue commodo maximus. &lt;/li&gt; &lt;li&gt; Phasellus ultricies nibh eu lacus dictum, id dictum ipsum iaculis. &lt;/li&gt; &lt;/ol&gt; &lt;p&gt; &lt;img src=\\"\\" alt=\\"Vineta\\" width=\\"4\\" height=\\"4\\" /&gt; Sed consequat justo quis arcu varius tristique. Pellentesque a vulputate velit. Aliquam erat volutpat. &lt;/p&gt; &lt;/td&gt; &lt;/tr&gt; &lt;tr&gt; &lt;td height=\\"5%\\"&gt; &lt;p&gt; &lt;/p&gt; &lt;/td&gt; &lt;/tr&gt; &lt;/table&gt; &lt;/body&gt; &lt;/html&gt;"_

In this case, we recommend removing HTML tags and converting to **markdown format**.

For this purpose we used Azure Document Intelligence, that provides the markdown conversion feature ([Document layout analysis - Document Intelligence (formerly Form Recognizer) - Azure AI services | Microsoft Learn](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/concept-layout?view=doc-intel-4.0.0&tabs=sample-code)).

Markdown:

_Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis interdum, sem nec commodo convallis, urna risus volutpat lacus, at volutpat ligula massa vitae ligula._
_Maecenas tincidunt iaculis sollicitudin._
_1. Sed eu magna at dolor porta luctus._
_2. Curabitur egestas ex et nibh mattis, eget maximus turpis molestie._
_3. Proin placerat molestie efficitur._
_4. Vivamus at odio non augue commodo maximus._
_5. Phasellus ultricies nibh eu lacus dictum, id dictum ipsum iaculis._
_Sed consequat justo quis arcu varius tristique. Pellentesque a vulputate velit. Aliquam erat volutpat._

This allows us to look at the relevant information in the documents and understand token distribution as well as content.

If the document contains sub-documents, as sections, it is important to review if the content of a sub-document has got enough context to allow the LLM use it to generate an answer, or if it is needed to use the complete document to avoid losing the context.

If the sub-document is not enough to understand the complete context of the document, after converting the HTML inside every sub-document to markdown, as a good practice **we combined** them to generate the complete document (a document is formed by the union of all its sub-documents, or sections).

This preprocessing is specific to the format of the documents, but for any implementation of this type of solution it is important to look into the document collection and assess what needs to be excluded and what needs to be captured in the chunks so that the LLM can build an answer that is both correct and relevant to the user question. Some common elements to look for in documents for additional preprocessing are tables, images, charts, multi-column data or paragraphs, languages, Unicode characters, headers or footers, footnotes or watermarks. In these documents we have only found html tags and tables, which we cover in more detail, but if there were other additional elements they would require specific preprocessing to make them suitable for the LLM to process.

**Code Snippet:**
[convert_html_to_markdown.ipynb](./convert_html_to_markdown.ipynb)