import arxiv
import os
import PyPDF2
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDUQv-4dlkqNy6X_xEuZoxwXFGylLXoZ4o")

def extract_text_from_pdf(filepath, max_chars=12000):
    text = ""
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
            if len(text) >= max_chars:
                break
    return text[:max_chars]


def build_prompt(paper_title, paper_text):
    return f"""<role>You are a logical analyst specializing in research methodology and idea generation</role>

<action>Analyze the research paper titled {paper_title} with content {paper_text} and reason through possible knowledge gaps to generate 5 novel research ideas</action>

<context>You have been given a research paper with a specific title and content, and you need to identify knowledge gaps and generate novel research ideas based on its contents, ensuring each idea is distinct, one challenges an assumption in the paper, and at least one is interdisciplinary, without using external information beyond the provided paper</context>

<expectation>
1. Explain your reasoning step-by-step, including how you identify knowledge gaps, formulate research questions, and develop approaches for each idea
2. Highlight uncertainties or assumptions in the paper that your ideas aim to address, particularly for the idea that challenges an existing assumption
3. End with a concise conclusion presenting the 5 novel research ideas, each with a title, explanation of why it matters, approach to tackling it, potential impact, and main challenge, ensuring specificity and clarity in your proposals
</expectation>

<constraints>
- Each idea must be distinct and not already addressed in the paper
- One idea must directly challenge or question an assumption the paper makes
- At least one idea must be interdisciplinary, combining this field with another field like biology, economics, or computer science
- Be specific, avoid vague suggestions
- Only use information from the provided paper, no external sources
</constraints>"""


def generate_ideas(paper_title, paper_text):
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = build_prompt(paper_title, paper_text)
    print("\nAsking Gemini to generate research ideas...\n")
    response = client.models.generate_content(model="models/gemini-2.5-flash", contents=prompt)
    return response.text

def main():
    while True:
        userInput = input("What topic would you like to search for? ")

        client = arxiv.Client()
        search = arxiv.Search(
            query = userInput,
            max_results = 5,
            sort_by = arxiv.SortCriterion.Relevance,
            sort_order = arxiv.SortOrder.Descending
        )

        results = list(client.results(search))
        for result in results:
            print(results.index(result) + 1)
            print(f"Title: {result.title}")
            print(f"Authors: {', '.join([author.name for author in result.authors])}")
            print(f"Published: {result.published}")
            print(f"Summary: {result.summary}")
            print(f"URL: {result.entry_id}")
            print("\n")

        chosenIndex = input("Which paper would you like to generate ideas from? (Enter the number): ")
        chosenPaper = results[int(chosenIndex) - 1]
        print(f"Downloading {chosenPaper.title}")
        os.makedirs("./arxiv_pdfs", exist_ok=True)
        chosenPaper.download_pdf(dirpath="./arxiv_pdfs")

        # Grab whatever PDF was most recently added to the folder
        pdf_files = sorted(
        [f for f in os.listdir("./arxiv_pdfs") if f.endswith(".pdf")],
        key=lambda f: os.path.getmtime(f"./arxiv_pdfs/{f}"),
        reverse=True)
        pdf_path = f"./arxiv_pdfs/{pdf_files[0]}"
        print(f"Found PDF: {pdf_files[0]}")

        # Extract text from it
        print("Reading the PDF...")
        paper_text = extract_text_from_pdf(pdf_path)

        # Send to Gemini and get ideas
        ideas = generate_ideas(chosenPaper.title, paper_text)

        # Print the ideas
        print("\n" + "="*60)
        print("GENERATED RESEARCH IDEAS")
        print("="*60)
        print(ideas) 

if __name__=="__main__":
    main()