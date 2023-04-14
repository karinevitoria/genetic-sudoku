"""
Created on 09/11/2019
@author: nidragedd
"""
import numpy as np
import random

from objects.sudoku import Sudoku


def create_generation(population_size, values_to_set):
    """
    Create the first generation knowing its size
    :param population_size: (int) size of the population we need to generate
    :param values_to_set: the values we have to set to init the objects
    :return: (array) of individuals randomly generated. Array has strictly <population_size> individuals
    """
    population = []
    for i in range(population_size):
        population.append(Sudoku(values_to_set).fill_random())
    return population


def rank_population(population):
    """
    Evaluate each individual of the population and give a ranking note whether it solves a lot or a little the problem
    (based on fitness method)
    :param population: (array) array of individuals to rank
    :return: (list) a sorted (asc) population. Individuals are sorted based on their fitness score
    """
    individuals_and_score = {}
    for individual in population:
        individuals_and_score[individual] = individual.fitness()
    return sorted(individuals_and_score, key=individuals_and_score.get)


def pick_from_population(ranked_population, selection_rate, random_selection_rate):
    """
    Select in a sorted population the best elements according to the given selection rate + add randomly some other
    elements
    :param ranked_population: (list) list of individuals sorted (asc) by the score, meaning that the best element is
    placed at the beginning and the worst at the end
    :param selection_rate: (float) given selection rate, it is a parameter that can be changed to act on the program
    :param random_selection_rate: (float) a random selection rate, it is a parameter that can also be changed to act
    on the program
    :return: (array) elements that have been selected in the given population. Not only the best are taken to avoid
    being stuck with a local minima
    """
    next_breeders = []

    nb_best_to_select = int(len(ranked_population) * selection_rate)
    nb_random_to_select = int(len(ranked_population) * random_selection_rate)

    # Keep n best elements in the population + randomly n other elements (note: might be the same)
    for i in range(nb_best_to_select):
        next_breeders.append(ranked_population[i])
    for i in range(nb_random_to_select):
        next_breeders.append(random.choice(ranked_population))

    # Shuffle everything to avoid having only the best (copyright Tina Turner) at the beginning
    np.random.shuffle(next_breeders)
    return next_breeders


def create_children(next_breeders, nb_children):
    """
    Create the children from the given breeders generation
    :param next_breeders: (array) the population that will be used to create the next one
    :param nb_children: (int) number of children to create per couple father/mother, it is a parameter that can be
    changed to act on the program
    :return: (array) children generated with this population. They represent the next generation to evaluate
    (after mutation)
    """
    next_population = []
    # Divided by 2: one 'father' and one 'mother'
    for i in range(int(len(next_breeders)/2)):
        for j in range(nb_children):
            # We take father at the beginning of the list, mother at the end (remember that elements have been shuffled)
            next_population.append(create_one_child(next_breeders[i], next_breeders[len(next_breeders) - 1 - i],
                                                    next_breeders[i].get_initial_values()))
    return next_population


def create_children_random_parents(next_breeders, nb_children):
    """
    Create the children from the given breeders generation
    :param next_breeders: (array) the population that will be used to create the next one
    :param nb_children: (int) number of children to create per couple father/mother, it is a parameter that can be
    changed to act on the program
    :return: (array) children generated with this population. They represent the next generation to evaluate
    (after mutation)
    """
    next_population = []
    # Randomly pick 1 father and 1 mother until new population is filled
    range_val = int(len(next_breeders)/2) * nb_children
    for _ in range(range_val):
        father = random.choice(next_breeders)
        mother = random.choice(next_breeders)
        next_population.append(create_one_child_random_elements(father, mother, father.get_initial_values()))
    return next_population


def create_one_child(father, mother, values_to_set):
    """
    Concretely create a child from both parents. In our case we take a group of grids from father and another one from
    mother with a randomly selected crossover point
    :param father: (object) one of the 2 elements used to build/generate a new one
    :param mother: (object) one of the 2 elements used to build/generate a new one
    :param values_to_set: the values we have to set to init the objects
    :return: (object) a child which is the combination of both parents
    """
    # Avoid having only the whole father or the whole mother
    # sudoku_size = father.size()
    # crossover_point_1 = np.random.randint(1, sudoku_size - 2)  # make sure there is at least one cell for the second point
    # crossover_point_2 = np.random.randint(crossover_point_1 + 1, sudoku_size - 1)

    # # Swap the grids between the two points
    # child_grids = []
    # for i in range(sudoku_size):
    #     if i < crossover_point_1:
    #         child_grids.append(father.grids()[i])
    #     elif i < crossover_point_2:
    #         child_grids.append(mother.grids()[i])
    #     else:
    #         child_grids.append(father.grids()[i])
    # return Sudoku(values_to_set).fill_with_grids(child_grids)
    # Create an empty child Sudoku object
    child_grids = [[None] * 9 for _ in range(9)]
    child = Sudoku(values_to_set).fill_with_grids(child_grids)

    # Create an array to keep track of the visited positions
    visited = [[False] * 9 for _ in range(9)]

    # Perform cycle crossover
    for i in range(9):
        for j in range(9):
            # Skip visited positions
            if visited[i][j]:
                continue

            # Start a new cycle
            current_value = father.grids()[i][j]
            cycle = [(i, j)]

            # Follow the cycle
            while True:
                # Find the corresponding position in the mother Sudoku
                row_mother, col_mother = None, None
                for x in range(9):
                    for y in range(9):
                        if mother.grids()[x][y] == current_value:
                            row_mother, col_mother = x, y
                            break

                # Check if the cycle is complete
                if (row_mother, col_mother) == (i, j):
                    break

                # Add the corresponding position to the cycle
                cycle.append((row_mother, col_mother))
                visited[row_mother][col_mother] = True

                # Move to the corresponding position in the father Sudoku
                i, j = row_mother, col_mother
                current_value = father.grids()[i][j]

            # Set the values in the child Sudoku
            for i, j in cycle:
                child.set_grid_value(i, j, father.grids()[i][j])

    return child


def create_one_child_random_elements(father, mother, values_to_set):
    """
    Concretely create a child from both parents. In our case we take a group of grids from father and another one from
    mother with a randomly selected crossover point
    :param father: (object) one of the 2 elements used to build/generate a new one
    :param mother: (object) one of the 2 elements used to build/generate a new one
    :param values_to_set: the values we have to set to init the objects
    :return: (object) a child which is the combination of both parents
    """
    # Avoid having only the whole father or the whole mother
    sudoku_size = father.size()
    elements_from_mother = np.random.randint(0, sudoku_size, np.random.randint(1, sudoku_size - 1))

    child_grids = []
    for i in range(sudoku_size):
        if i in elements_from_mother:
            child_grids.append(mother.grids()[i])
        else:
            child_grids.append(father.grids()[i])
    return Sudoku(values_to_set).fill_with_grids(child_grids)


def mutate(self):
# Choose a random block, row, and column
    block_row, block_col = np.random.randint(3), np.random.randint(3)
    row, col = np.random.randint(3) + block_row * 3, np.random.randint(3) + block_col * 3

    # Choose two random positions within the block
    pos1 = np.random.randint(3)
    pos2 = np.random.randint(3)

    # Swap the values at the selected positions within the block
    temp = self._grids[block_row][block_col][pos1][col % 3]
    self._grids[block_row][block_col][pos1][col % 3] = self._grids[block_row][block_col][pos2][col % 3]
    self._grids[block_row][block_col][pos2][col % 3] = temp

    # Reset the fitness score
    self._fitness_score = None

    # Return the mutated individual
    return self

def mutate_population(population, mutation_rate):
    population_with_mutation = []
    for individual in population:
        if np.random.random() < mutation_rate:
            individual = individual.mutate()
        population_with_mutation.append(individual)
    return population_with_mutation 


