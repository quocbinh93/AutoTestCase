import tkinter as tk
from tkinter import ttk, filedialog
from graphviz import Digraph
from deap import base, creator, tools, algorithms
import random

# --- Giai đoạn 1: Nhập và lưu mô tả use case ---

def save_use_case(use_case_data):
    with open("use_case.txt", "w") as file:
        for key, value in use_case_data.items():
            file.write(f"{key}: {value}\n")

def get_use_case_input():
    use_case_data = {
        "Name": name_entry.get(),
        "Goal": goal_entry.get(),
        "Actors": actors_entry.get(),
        "Preconditions": preconditions_entry.get(),
        "Postconditions": postconditions_entry.get(),
        "Invariants": invariants_entry.get(),
        "Main Success Scenario": main_scenario_text.get("1.0", tk.END),
        "Variations": variations_text.get("1.0", tk.END),
        "Extensions": extensions_text.get("1.0", tk.END),
        "Included Use Cases": included_use_cases_entry.get()
    }
    save_use_case(use_case_data)
    window.destroy()  # Đóng cửa sổ sau khi lưu

# Tạo cửa sổ giao diện
window = tk.Tk()
window.title("Use Case Description Tool")

# Tạo các nhãn và trường nhập liệu
labels = ["Name", "Goal", "Actors", "Preconditions", "Postconditions", "Invariants",
        "Main Success Scenario", "Variations", "Extensions", "Included Use Cases"]
for label_text in labels:
    label = ttk.Label(window, text=label_text)
    label.pack()
    if label_text in ["Main Success Scenario", "Variations", "Extensions"]:
        entry = tk.Text(window)  # Sử dụng Text widget cho các trường nhập liệu dài
    else:
        entry = ttk.Entry(window)
    entry.pack()
    if label_text == "Name":
        name_entry = entry
    elif label_text == "Goal":
        goal_entry = entry
    # ... (tương tự cho các trường khác)

# Tạo nút Lưu
save_button = ttk.Button(window, text="Save", command=get_use_case_input)
save_button.pack()

window.mainloop()

# --- Giai đoạn 2: Tạo biểu đồ luồng điều khiển (CFD) ---

def extract_statements(use_case_data):
    statements = [stmt.strip() for stmt in use_case_data["Main Success Scenario"].strip().split("\n") if stmt.strip()]
    statements += [stmt.strip() for stmt in use_case_data["Extensions"].strip().split("\n") if stmt.strip()]
    return statements

def analyze_statement(statement):
    if "IF" in statement or "ELSE" in statement:
        return "condition"
    elif "INPUT" in statement or "ENTER" in statement:
        return "input"
    elif "DISPLAY" in statement or "PRINT" in statement:
        return "output"
    else:
        return "process"

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

# --- Giai đoạn 3: Tạo test case từ biểu đồ luồng điều khiển ---

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

# --- Giai đoạn 4: Tối ưu hóa test case ---

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

# --- Chương trình chính ---

# Đọc dữ liệu use case từ tệp
with open("use_case.txt", "r") as file:
    use_case_data = {}
    for line in file:
        key, value = line.strip().split(": ", 1)
        use_case_data[key] = value

# Tạo biểu đồ luồng điều khiển
control_flow_graph = acfd(use_case_data)

# Tạo và tối ưu hóa test case
test_paths = generate_test_paths(control_flow_graph)
optimized_test_cases = optimize_test_cases(test_paths, control_flow_graph)

# In kết quả
print("Optimized Test Cases:")
for test_case in optimized_test_cases:
    print(test_case)

# Trực quan hóa biểu đồ luồng điều khiển
visualize_control_flow_graph(control_flow_graph)
