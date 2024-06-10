from graphviz import Digraph

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
    # Khởi tạo nút "Start" ngay từ đầu
    control_flow_graph = {"Start": {"type": "start", "content": "Start Node", "next": None}} 
    current_node = "Start"  

    for statement in statements:
        statement_type = analyze_statement(statement)
        # Đơn giản hóa việc đánh số nút
        new_node = f"Node_{len(control_flow_graph)}" 
        control_flow_graph[new_node] = {"type": statement_type, "content": statement}
        control_flow_graph[current_node]["next"] = new_node

        # Xử lý nút điều kiện và cập nhật nút hiện tại
        if statement_type == "condition":
            true_node = f"Node_{len(control_flow_graph) + 1}"
            false_node = f"Node_{len(control_flow_graph) + 1}"
            control_flow_graph[new_node]["true"] = true_node
            control_flow_graph[new_node]["false"] = false_node
            current_node = true_node  
        else:
            current_node = new_node

    # Kết thúc đồ thị bằng nút "End"
    control_flow_graph[current_node]["next"] = "End"
    control_flow_graph["End"] = {"type": "end", "content": "End Node"} 
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
