import sys

from crossword import *
from copy import deepcopy


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            # Dictionary mapping the variables as keys to all the words in the word file as value
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            to_remove = []
            for word in self.domains[var]:
                if var.length != len(word):
                    to_remove.append(word)

            for word in to_remove:
                self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        coord = self.crossword.overlaps[x, y]

        if coord is None:
            return False

        revision_made = False
        to_remove = []
        for word in self.domains[x]:
            has_solution = False

            for other_word in self.domains[y]:
                # If letters match up, then the word has a solution
                if word[coord[0]] == other_word[coord[1]]:
                    has_solution = True
                    break

            # If no word in y's domain matches up with current word
            if not has_solution:
                to_remove.append(word)
                revision_made = True
        
        # Remove words
        for word in to_remove:
            self.domains[x].remove(word)

        return revision_made

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        """
        Binary constraints:
        1. No two words can be the same
        2. Neighboring words must share the same letter at their intersection 
        """

        # Initial queue of all the arcs in the problem as a list of tuples
        if not arcs:
            arcs = []
            for x in self.domains.keys():
                for y in self.domains.keys():
                    if x == y:
                        continue
                    arcs.append((x, y))

        while arcs:

            # Dequeue first item
            x, y = arcs.pop(0)

            if self.revise(x, y):
            
                # No solution, return False
                if len(self.domains[x]) == 0:
                    return False
                
                # Enqueue all of x's neighbors besides y
                for z in (self.crossword.neighbors(x) - {y}):
                    arcs.append((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
            
        # If there is a variable in the puzzle not added to assignment yet
        for var in self.domains.keys():
            if var not in assignment.keys():
                return False
            
        return True


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # Check if dictionary only contains unique values
        all_values = assignment.values()
        if len(all_values) != len(set(all_values)):
            return False

        # Check if words fit in the crossword puzzle correctly
        for var in assignment:
            if var.length != len(assignment[var]):
                return False
            
        # Check for conflicting characters
        overlaps = self.crossword.overlaps
        for x, y in overlaps:

            # Overlap doesn't exist
            if overlaps[x, y] is None:
                    continue
            
            # Both variables are assigned a word, check if there is a conflict
            if (x in assignment.keys()) and (y in assignment.keys()):
                i, j = overlaps[x, y]
                if assignment[x][i] != assignment[y][j]:
                    return False
            
        return True
            

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        words_ruled_out = dict()

        # Dictionary of word as key, number of options ruled out as value
        words = self.domains[var]
        for word in words:
            num_ruled_out = 0

            for neighbor in self.crossword.neighbors(var):

                # The neighboring variables we affect do not include the assigned variables already 
                if neighbor in assignment:
                    continue

                for other_word in self.domains[neighbor]:
                    if word == other_word:
                        num_ruled_out += 1
                    else:
                        (i, j) = self.crossword.overlaps[var, neighbor]
                        if word[i] != other_word[j]:
                            num_ruled_out += 1

            words_ruled_out[word] = num_ruled_out

        # Sort a list of keys by their options ruled out in ascending order
        result = sorted(words_ruled_out.keys(), key=lambda x: words_ruled_out[x])
        return result
                

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # Unassigned variables as a list
        unassigned = list(set(self.domains.keys()) - set(assignment.keys()))

        # Get the variables with the minimum number of remaining values and put them in a list
        min = len(self.domains[unassigned[0]])
        ties = []
        for var in unassigned:

            # If there is a tie, add the variable to the tied list
            if len(self.domains[var]) == min:
                ties.append(var)

            # If there is a new min, clear list and add to tied list
            elif len(self.domains[var]) < min:
                ties.clear()
                ties.append(var)

        if len(ties) == 1:
            return ties[0]
        else:
            
            #If there is a tie, order by their degrees descending
            tied_degrees = dict()
            for var in ties:
                tied_degrees[var] = len(self.crossword.neighbors(var))

            sorted_results = sorted(tied_degrees.items(), key=lambda x: x[1], reverse=True)

            # Return the word of the first tuple in the list [('NINE', 3), ('FIVE', 4)]
            return sorted_results[0][0]


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        

        # Snapshot of the domain before making a possibly wrong choice
        preassigned_domain = deepcopy(self.domains)
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):

            # Check to see if value is consistent with variable in assignment
            assignment[var] = value
            if self.consistent(assignment):

                # Update the variable's value
                self.domains[var] = {value}
                self.enforce_node_consistency()

                # Remove inconsistent values using ac3
                for neighbor in self.crossword.neighbors(var):
                    self.ac3([(neighbor, var)])

                result = self.backtrack(assignment)
                if result:
                    return result
            
            # Assignment has not solution, remove assignment and revert the domain to where it was before the mistake
            del assignment[var]
            self.domains = preassigned_domain
        
        # Checked all values, no solution
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
