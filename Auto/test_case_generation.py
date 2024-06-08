from deap import base, creator, tools, algorithms
import random

def generate_test_paths(control_flow_graph):
    def dfs(node, path):
        path.append(node)
        if node == "End":
            test_paths.append(path)
        else:
            if "next" in control_flow_graph[node]:
                dfs(control_flow_graph[node]["next"], path.copy())
            if "true" in control_flow_graph[node]:
                dfs(control_flow_graph[node]["true"], path.copy())
            if "false" in control_flow_graph[node]:
                dfs(control_flow_graph[node]["false"], path.copy())

    test_paths = []
    dfs("Start", [])
    return test_paths

def evaluate_test_case(individual, control_flow_graph):
    covered_transitions = set()
    current_node = "Start"
    for gene in individual:
        if gene == 1 and "true" in control_flow_graph[current_node]:
            covered_transitions.add((current_node, control_flow_graph[current_node]["true"]))
            current_node = control_flow_graph[current_node]["true"]
        elif gene == 0 and "false" in control_flow_graph[current_node]:
            covered_transitions.add((current_node, control_flow_graph[current_node]["false"]))
            current_node = control_flow_graph[current_node]["false"]
        elif "next" in control_flow_graph[current_node]:
            covered_transitions.add((current_node, control_flow_graph[current_node]["next"]))
            current_node = control_flow_graph[current_node]["next"]

    return len(covered_transitions),

def optimize_test_cases(test_paths, control_flow_graph):
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    toolbox.register("attr_bool", random.randint, 0, 1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, n=len(test_paths[0]))
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate_test_case, control_flow_graph=control_flow_graph)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)

    population = toolbox.population(n=50)

    NGEN = 40
    for gen in range(NGEN):
        offspring = algorithms.varAnd(population, toolbox, cxpb=0.5, mutpb=0.1)
        fits = toolbox.map(toolbox.evaluate, offspring)
        for fit, ind in zip(fits, offspring):
            ind.fitness.values = fit
        population = toolbox.select(offspring, k=len(population))

    best_individuals = tools.selBest(population, k=5)
    return best_individuals
