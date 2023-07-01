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
                print(one_gene, two_genes, have_trait)
                print(p)
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
    p = {}
    pool = people.copy()


    # algorithm that runs until pool is empty:
    # checks if we can deduce somethjing -> if can then delete from pool
    # we can use that deduction to get probabilities of future ones
    for person in pool.copy():
        if pool[person]["trait"] == None:
            pool[person]["trait"] = False

    while pool:
        for person in pool.copy():

            if pool[person]["mother"] == None and pool[person]["father"] == None:
                if person in one_gene:
                    p[person] = PROBS["gene"][1] * PROBS["trait"][1][pool[person]["trait"]]
                elif person in two_genes:
                    p[person] = PROBS["gene"][2] * PROBS["trait"][2][pool[person]["trait"]]
                else:
                    p[person] = PROBS["gene"][0] * PROBS["trait"][0][pool[person]["trait"]]

                del pool[person]

            # Skip over cases where we don't have enough information to get a probability
            elif (pool[person]["mother"] or pool[person]["father"]) and not (pool[person]["mother"] and pool[person]["father"]):
                continue

            else:
                # Probability of mother passing the gene
                if pool[person]["mother"] in one_gene:
                    p_mother = 0.5# - PROBS["mutation"]
                elif pool[person]["mother"] in two_genes:
                    p_mother = 1 - PROBS["mutation"]
                else:
                    p_mother = PROBS["mutation"]


                # Probability of father passing the gene
                if pool[person]["father"] in one_gene:
                        p_father = 0.5# - PROBS["mutation"]
                elif pool[person]["father"] in two_genes:
                    p_father = 1 - PROBS["mutation"]
                else:
                    p_father = PROBS["mutation"]             


                if person in one_gene:
                    # Either person gets gene from mother but not father or vice versa
                    p[person] = (p_mother * (1 - p_father) + (1 - p_mother) * p_father) * PROBS["trait"][1][people[person]["trait"]]
                elif person in two_genes:
                    p[person] = (p_mother * p_father) * PROBS["trait"][2][people[person]["trait"]]
                else:
                    p[person] = ((1 - p_mother) * (1 - p_father)) * PROBS["trait"][0][people[person]["trait"]]


                del pool[person]

    joint_p = 1             
    for person in p:
        joint_p *= p[person]

    return joint_p


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

        gene_total = sum(probabilities[person]['gene'].values())
        trait_total = sum(probabilities[person]['trait'].values())

        for i in range(3):
            probabilities[person]['gene'][i] = probabilities[person]['gene'][i] / gene_total
        
        for i in range(2):
            probabilities[person]['trait'][i] = probabilities[person]['trait'][i] / 1

if __name__ == "__main__":
    main()
