import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):
        
        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    """
    Go through every person in people and calculate the probability that they have x genes and
    have_trait. Update the joint_prob number by multiplying joint_prob with the calculated probability

    If the person has no mother and father, then the person probability is just P(gene ^ trait) = P(gene) * P(trait | gene)

    Else if the person has a mother and father, then the person probability is dependant on the mother and father
    The probability that mother and father pass down the gene is only dependant on how many genes they have
    - calculate P(person inheriting from mother) and P(person inheriting from father)
    - calculate P(person having x genes)
    - multiply this by P(trait | x genes)
    - result is P(gene ^ trait) which is used in the joint probability

    """
    joint_prob = 1

    for person in people:

        mother = people[person]["mother"]
        father = people[person]["father"]

        # Put person genes, traits, and probability into variables
        person_prob = 1
        if person in two_genes:
            person_genes = 2
        elif person in one_gene:
            person_genes = 1
        else:
            person_genes = 0
        person_trait = person in have_trait


        if not mother and not father:
            # P(gene ^ trait) = P(gene) * P(trait | gene)
            # the P(trait | gene) is inculded later
            person_prob *= PROBS["gene"][person_genes]

        else:

            # Get the probability of mother passing down the gene
            if mother in two_genes:
                mother_prob =  1- PROBS["mutation"]
            elif mother in one_gene:
                mother_prob = 0.5
            else:
                mother_prob = PROBS["mutation"]

            # Get the probability of father passing down the gene
            if father in two_genes:
                father_prob =  1- PROBS["mutation"]
            elif father in one_gene:
                father_prob = 0.5
            else:
                father_prob = PROBS["mutation"]

            # Calculate all ways to get the correct number of genes for the person
            if person_genes == 2:
                person_prob *= mother_prob * father_prob
            elif person_genes == 1:
                # Person can get the no gene from mother and 1 gene from father and vice versa
                person_prob *= ((1 - mother_prob) * father_prob) + ((1 - father_prob) * mother_prob)
            else:
                person_prob *= (1 - mother_prob) * (1 - father_prob)

        # P(gene ^ trait) = P(gene) * P(trait | gene)
        person_prob *= PROBS["trait"][person_genes][person_trait]

        joint_prob *= person_prob

    return joint_prob


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """

    # Add up all the possible probabilities we calculated to get a complete probability distribution
    for person in probabilities:
        if person in two_genes:
            person_genes = 2
        elif person in one_gene:
            person_genes = 1
        else:
            person_genes = 0

        person_trait = person in have_trait

        probabilities[person]['gene'][person_genes] += p
        probabilities[person]['trait'][person_trait] += p



def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:

        # The alpha value to be multiplied by to normalize the values
        gene_alpha = 1 / sum(probabilities[person]['gene'].values())
        trait_alpha = 1 / sum(probabilities[person]['trait'].values())

        for i in range(3):
            probabilities[person]['gene'][i] = probabilities[person]['gene'][i] * gene_alpha
        
        for i in range(2):
            probabilities[person]['trait'][i] = probabilities[person]['trait'][i] * trait_alpha

if __name__ == "__main__":
    main()
