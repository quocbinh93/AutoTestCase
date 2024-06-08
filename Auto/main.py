import use_case_input
import cfd_generation
import test_case_generation

def main():
    # Run the Tkinter event loop to show the GUI and allow user input
    use_case_input.window.mainloop()
    # Now that the window is closed, retrieve the data from the global variable:
    use_case_data = use_case_input.use_case_data

    if use_case_data:  # Kiểm tra xem dữ liệu có được thu thập thành công không
        # Create control flow graph
        control_flow_graph = cfd_generation.acfd(use_case_data)

        # Generate and optimize test cases
        test_paths = test_case_generation.generate_test_paths(control_flow_graph)
        optimized_test_cases = test_case_generation.optimize_test_cases(test_paths, control_flow_graph)

        # Print results
        print("Optimized Test Cases:")
        for test_case in optimized_test_cases:
            print(test_case)

        # Visualize control flow graph
        cfd_generation.visualize_control_flow_graph(control_flow_graph)
    else:
        print("Không có dữ liệu use case được nhập.")

if __name__ == "__main__":
    main()
