import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
       
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    prob_distribution = {}
    for key in corpus:
        prob_distribution[key] = (1 - damping_factor) * (1 / len(corpus))

    # If page has no outgoing links
    if len(corpus[page]) == 0:
        for key in prob_distribution:
            prob_distribution[key] /= (1 - damping_factor)
        return prob_distribution

    for value in corpus[page]:
        prob_distribution[value] += damping_factor * (1 / len(corpus[page]))

    return prob_distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pageRank = {}

    # Get first sample
    page = random.choice(list(corpus.keys()))
    pageRank[page] = 1
    counter = 1

    while counter <= n:
        prob_distribution = transition_model(corpus, page, damping_factor)

        # Choose randomly from the probability distribution
       
        random_num = random.random() # float between 0 and 1
        cumulative_prob = 0
        for key in prob_distribution:
            cumulative_prob += prob_distribution[key]
            if cumulative_prob >= random_num:
                next_page = key
                break
        
        page = next_page
        if page not in pageRank:
            pageRank[page] = 1
        else:
            pageRank[page] += 1

        counter += 1

    # Convert counts into probabilities
    for key in pageRank:
        pageRank[key] = pageRank[key] / n

    return pageRank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pageRank = {}
    N = len(corpus)

    for key in corpus:
        pageRank[key] = 1 / N

    # A page that has no links at all should be interpreted as having one line for every page in the corpus including themselves
    for page in corpus:
        if len(corpus[page]) == 0:
            links = set()
            links.update(list(corpus.keys()))
            corpus[page] = links
            
    # Update each pageRank one by one
    count = 0
    while count < N:

        for page in corpus:

            # Find other pages that contain a link to the page that we want to update
            summation = 0
            for other_page in corpus:
                # If there is a link to the page that we want to update, add it to our summation
                if page in corpus[other_page]:
                    summation += pageRank[other_page] / len(corpus[other_page])

            new_pagerank = ((1 - damping_factor) / N) + damping_factor * summation
            
            difference = abs(pageRank[page] - new_pagerank)
            if difference <= 0.001:
                count += 1

            pageRank[page] = new_pagerank

        norm_factor = sum(pageRank.values())
        for page in pageRank:
            pageRank[page] /= norm_factor

    return pageRank


if __name__ == "__main__":
    main()
