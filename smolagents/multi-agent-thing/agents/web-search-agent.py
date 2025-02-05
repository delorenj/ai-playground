import re
import markdownify
from requests import RequestException
import requests
from smolagents import (
    CodeAgent,
    tool,
    ToolCallingAgent,
    HfApiModel,
    DuckDuckGoSearchTool,
    LiteLLMModel,
)

model_id = "Qwen/Qwen2.5-Coder-32B-Instruct"
model = HfApiModel(model_id)

@tool
def visit_webpage(url: str) -> str:
    """Visits a webpage at the given URL and returns its content as a markdown string.

    Args:
        url: The URL of the webpage to visit.

    Returns:
        The content of the webpage converted to Markdown, or an error message if the request fails.
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Convert the HTML content to Markdown
        markdown_content = markdownify(response.text).strip()

        # Remove multiple line breaks
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)

        return markdown_content

    except RequestException as e:
        return f"Error fetching the webpage: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

web_agent = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool(), visit_webpage],
    model=model,
    max_steps=10,
    name="search",
    description="Runs web searches for you. Give it your query as an argument.",
)

longest_word_finder = CodeAgent(
    tools=[],
    model=model,
    description="Finds the longest word in a given text.",
)

manager_agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[web_agent, longest_word_finder],
    additional_authorized_imports=["time", "numpy", "pandas"],
)


answer = manager_agent.run("Find the longest word on the Wikipedia page about cheetahs.")