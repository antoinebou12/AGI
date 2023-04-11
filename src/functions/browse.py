import httpx
from bs4 import BeautifulSoup
from config import Config
from llm_utils import create_chat_completion
from rich.console import Console

console = Console()

cfg = Config()

# Define and check for local file address prefixes
def check_local_file_access(url):
    local_prefixes = ['file:///', 'file://localhost', 'http://localhost', 'https://localhost']
    return any(url.startswith(prefix) for prefix in local_prefixes)

def scrape_text(url):
    """Scrape text from a webpage"""
    if not url.startswith('http'):
        return "Error: Invalid URL"

    if check_local_file_access(url):
        return "Error: Access to local files is restricted"

    try:
        response = httpx.get(url, headers=cfg.user_agent_header)
    except httpx.RequestError as e:
        return f"Error: {str(e)}"

    if response.status_code >= 400:
        return f"Error: HTTP {str(response.status_code)} error"

    soup = BeautifulSoup(response.text, "html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text

def extract_hyperlinks(soup):
    """Extract hyperlinks from a BeautifulSoup object"""
    return [(link.text, link['href']) for link in soup.find_all('a', href=True)]


def format_hyperlinks(hyperlinks):
    """Format hyperlinks into a list of strings"""
    return [f"{link_text} ({link_url})" for link_text, link_url in hyperlinks]


def scrape_links(url):
    """Scrape links from a webpage"""
    response = httpx.get(url, headers=cfg.user_agent_header)

    # Check if the response contains an HTTP error
    if response.status_code >= 400:
        return "error"

    soup = BeautifulSoup(response.text, "html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    hyperlinks = extract_hyperlinks(soup)

    return format_hyperlinks(hyperlinks)


def split_text(text, max_length=8192):
    """Split text into chunks of a maximum length"""
    paragraphs = text.split("\n")
    current_length = 0
    current_chunk = []

    for paragraph in paragraphs:
        if current_length + len(paragraph) + 1 <= max_length:
            current_chunk.append(paragraph)
            current_length += len(paragraph) + 1
        else:
            yield "\n".join(current_chunk)
            current_chunk = [paragraph]
            current_length = len(paragraph) + 1

    if current_chunk:
        yield "\n".join(current_chunk)

def summarize_text(text, question):
    if not text:
        return "Error: No text to summarize"

    text_length = len(text)
    console.print(f"Text length: {text_length} characters")

    summaries = []
    chunks = list(split_text(text))

    for i, chunk in enumerate(chunks):
        console.print(f"Summarizing chunk {i + 1} / {len(chunks)}")
        messages = [create_message(chunk, question)]

        summary = create_chat_completion(
            model=cfg.fast_llm_model,
            messages=messages,
            max_tokens=300,
        )
        summaries.append(summary)

    console.print(f"Summarized {len(chunks)} chunks.")

    combined_summary = "\n".join(summaries)
    messages = [create_message(combined_summary, question)]

    return create_chat_completion(
        model=cfg.fast_llm_model,
        messages=messages,
        max_tokens=300,
    )
