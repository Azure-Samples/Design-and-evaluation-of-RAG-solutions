import os
import re
import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")


# Calculate number of tokens of a text
def token_len(input):
    # Returns number of tokens for the input. Only for models > gpt-3.5 supported as we use 'cl100k_base' encoding
    return len(encoding.encode(input))


# Cut a text to a maximum number of tokens
def cut_max_tokens(text):
    tokens = encoding.encode(text)
    max_tokens = 8191
    if len(tokens) > max_tokens:
        print(f'\t*** CUT TOKENS, tokens: {len(tokens)}')
        return encoding.decode(tokens[:max_tokens])
    else:
        return text


# Extract data between two delimiters
def extract_text(texto, start_delimiter, end_delimiter=''):
    if end_delimiter != '':
        # This regular expression searches for any text between the delimiters.
        patron = re.escape(start_delimiter) + '(.*?)' + re.escape(end_delimiter)
        resultado = re.search(patron, texto, re.DOTALL)
        if resultado:
            return resultado.group(1)
        else:
            return None
    else:
        # Find the position of the delimiter in the text
        delimiter_index = texto.find(start_delimiter)
        if delimiter_index != -1:
            # Extract the text from the delimiter to the end
            return texto[delimiter_index + len(start_delimiter):]
        else:
            return None


# Load in an array the content of every html file in a directory
def load_files(input_dir, ext):
    print(f'Loading files in {input_dir}...')
    files_content = []
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(ext):
            file_path = os.path.join(input_dir, filename)
            with open(file_path, 'r', encoding="utf-8") as f:
                row = {"title": filename.replace('_', ' ').replace('.txt', ''), "content": f.read()}
                files_content.append(row)
    return files_content
