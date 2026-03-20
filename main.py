import arxiv

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
        chosenPaper.download_pdf(dirpath="./arxiv_pdfs")

        # up to here, the code allows the user to pick which paper they want to base their idea
        # generation on. The pdf of the downloaded paper is located in the arxiv.pdfs folder.
        # the next step would just be to use AI (Gemini?) to read the pdf and generate ideas based on its contents. 

if __name__=="__main__":
    main()