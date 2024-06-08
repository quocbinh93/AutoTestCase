import tkinter as tk
from tkinter import ttk, filedialog
from graphviz import Digraph
from deap import base, creator, tools, algorithms
import random

def browse_file():
    global filepath
    filepath = filedialog.askopenfilename(
        initialdir="/",
        title="Select a File",
        filetypes=(("Text files", "*.txt*"), ("all files", "*.*"))
    )

def generate_control_flow_diagram():
    global filepath
    if filepath:
        with open(filepath, "r") as file:
            use_case_data = file.read()

        control_flow_graph = acfd(use_case_data)
        test_paths = generate_test_paths(control_flow_graph)
        visualize_control_flow_graph(control_flow_graph)

        # Tối ưu hóa các trường hợp thử nghiệm
        optimized_test_cases = optimize_test_cases(test_paths, control_flow_graph)

        # In ra các trường hợp thử nghiệm đã tối ưu
        for test_case in optimized_test_cases:
            print(test_case)

# Triển khai thuật toán ACFD (Algorithm of Control Flow Diagram)
def acfd(use_case_data):
    statements = extract_statements(use_case_data)
    control_flow_graph = {}
    current_node = "Start"

    for statement in statements:
        statement_type = analyze_statement(statement)
        new_node = f"Node_{len(control_flow_graph) + 1}"
        control_flow_graph[new_node] = {"type": statement_type, "content": statement}
        control_flow_graph[current_node]["next"] = new_node

        if statement_type == "condition":
            true_node = f"Node_{len(control_flow_graph) + 1}"
            false_node = f"Node_{len(control_flow_graph) + 1}"
            control_flow_graph[new_node]["true"] = true_node
            control_flow_graph[new_node]["false"] = false_node
            current_node = true_node 

        else:
            current_node = new_node

    control_flow_graph[current_node]["next"] = "End"
    return control_flow_graph

# Hàm phụ trợ để trích xuất các bước từ use_case_data
def extract_statements(use_case_data):
    statements = [stmt.strip() for stmt in use_case_data.strip().split("\n") if stmt.strip()]
    return statements

# Hàm phụ trợ để phân tích cú pháp một bước
def analyze_statement(statement):
    if "IF" in statement or "ELSE" in statement:
        return "condition"
    elif "INPUT" in statement or "ENTER" in statement:
        return "input"
    elif "DISPLAY" in statement or "PRINT" in statement:
        return "output"
    else:
        return "process"

# Hàm tạo ra các đường dẫn thử nghiệm từ biểu đồ luồng điều khiển
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

# Hàm trực quan hóa biểu đồ luồng điều khiển sử dụng graphviz
def visualize_control_flow_graph(control_flow_graph):
    dot = Digraph(comment='Control Flow Diagram')

    for node, data in control_flow_graph.items():
        dot.node(node, label=f"{node}\n({data['type']})\n{data['content']}")
        if "next" in data:
            dot.edge(node, data["next"])
        if "true" in data:
            dot.edge(node, data["true"], label="True")
        if "false" in data:
            dot.edge(node, data["false"], label="False")

    dot.render('control_flow_graph', view=True)

# Hàm đánh giá độ phù hợp của một test case (individual)
# dựa trên tiêu chí bao phủ chuyển tiếp
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

    return len(covered_transitions),  # Trả về số lượng chuyển tiếp được bao phủ

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

    best_individuals = tools.selBest(population, k=5)  # Chọn ra 5 cá thể tốt nhất
    return best_individuals

# Tạo cửa sổ giao diện
window = tk.Tk()
window.title("Use Case to Control Flow Diagram Tool")

# Tạo nút "Browse" để chọn tệp use case
browse_button = ttk.Button(window, text="Browse", command=browse_file)
browse_button.pack()

# Tạo nút "Generate" để tạo biểu đồ luồng điều khiển
generate_button = ttk.Button(window, text="Generate", command=generate_control_flow_diagram)
generate_button.pack()

window.mainloop()
