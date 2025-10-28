import ast

class RecursiveAnalyzer():
    ComplexityRanks = {
        "O(1)": 0,
        "O(log n)": 1,
        "O(n)": 2,
        "O(n log n)": 3,
        "O(2^n)": 8,
        "O(n!)": 9,
        "O(inf)": 10
    }

    @staticmethod
    def get_complexity_rank(big_o: str):
        if " or " in big_o:
            complexities = big_o.split(" or ")
            return max(RecursiveAnalyzer.get_complexity_rank(p.strip().split(" ")[0]) for p in complexities)
        
        if "O(n^" in big_o:
            power = int(big_o.split('^')[-1].replace(')', ''))
            return 3 + power
        
        return RecursiveAnalyzer.ComplexityRanks.get(big_o, -1)
    
    def analyze(self, code: str):
        tree = ast.parse(code)
        
        visitor = RecursiveCallVisitor()
        visitor.visit(tree)
        
        results = {}
        for func_name, func_node in visitor.recursive_calls.items():
            if self.is_recursive(func_node, func_name):
                results[func_name] = self.analyze_function(func_node)
        
        return {
            "recursive_functions_analyzed": results,
            "explanation": "Analysis of recursive functions complete."
        }
    
    def is_recursive(self, func_node: ast.FunctionDef, func_name: str):
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == func_name:
                return True
        return False
    
    def analyze_function(self, func_node: ast.FunctionDef):
        def count_calls_in_node(node):
            """Counts recursive calls within a given node."""
            count = 0
            for n in ast.walk(node):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == func_node.name:
                    count += 1
            return count

        def find_max_calls_in_branch(node_list):
            """Finds the max calls in any single branch (e.g., if/else)."""
            max_calls = 0
            
            non_branch_nodes = [n for n in node_list if not isinstance(n, ast.If)]
            for node in non_branch_nodes:
                max_calls += count_calls_in_node(node)

            if_nodes = [n for n in node_list if isinstance(n, ast.If)]
            if not if_nodes:
                return max_calls

            max_branch_calls = 0
            for if_node in if_nodes:
                body_calls = find_max_calls_in_branch(if_node.body)
                orelse_calls = find_max_calls_in_branch(if_node.orelse)
                max_branch_calls = max(max_branch_calls, body_calls, orelse_calls)
            
            return max_calls + max_branch_calls
        
        recursive_calls = find_max_calls_in_branch(func_node.body)
        work_per_call, work_rank = self.find_work_per_call(func_node.body)
        has_base_case = self.find_base_case(func_node)
        big_o, explanation = self.estimate_complexity(recursive_calls, work_per_call, work_rank, has_base_case)

        return {
            "recursive_call_count": recursive_calls,
            "work_per_call": work_per_call,
            "base_cases_found": has_base_case,
            "estimated_big_o": big_o,
            "explanation": explanation
        }
    
    def find_work_per_call(self, node_list):
        loop_stats = {"count": 0, "max_nesting": 0}

        def find_loops(node, depth= 0):
            nonlocal loop_stats
            if isinstance(node, (ast.For, ast.While)):
                loop_stats["count"] += 1
                loop_stats["max_nesting"] = max(loop_stats["max_nesting"], depth + 1)
                for child in ast.iter_child_nodes(node):
                    find_loops(child, depth + 1)
                return
            if isinstance(node, (ast.FunctionDef, ast.Call)):
                return
            
            for child in ast.iter_child_nodes(node):
                find_loops(child, depth)

        for node in node_list:
            find_loops(node)

        max_depth = loop_stats["max_nesting"]
        if loop_stats["count"] == 0:
            big_o = "O(1)"
        elif max_depth == 1:
            big_o = "O(n)"
        else:
            big_o = f"O(n^{max_depth})"

        return big_o, self.get_complexity_rank(big_o)
    
    def find_base_case(self, func_node: ast.FunctionDef):
        for node in ast.walk(func_node):
            if isinstance(node, ast.If):
                for body_item in node.body + node.orelse:
                    if isinstance(body_item, ast.Return):
                        is_recurive_return = False

                        for call in ast.walk(body_item):
                            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == func_node.name:
                                is_recurive_return = True
                                break
                        if not is_recurive_return:
                            return True

        all_calls_guarded = True
        has_recursive_calls = False

        def check_guards(node, is_guarded):
            nonlocal all_calls_guarded, has_recursive_calls
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == func_node.name:
                has_recursive_calls = True
                if not is_guarded:
                    all_calls_guarded = False
                return

            new_guard_status = is_guarded
            if isinstance(node, (ast.If, ast.While, ast.For)):
                new_guard_status = True

            for child in ast.iter_child_nodes(node):
                check_guards(child, new_guard_status)

        for body_item in func_node.body:
            check_guards(body_item, is_guarded=False)

        if has_recursive_calls and all_calls_guarded:
            return True

        return False
    
    def estimate_complexity(self, calls, work_big_o, work_rank, has_base):
        if not has_base:
            return "O(inf)", "No base case found; function may not terminate."
        
        work_o1 = self.get_complexity_rank("O(1)")
        
        if calls == 1:
            if work_rank <= work_o1:
                return "O(n) or O(log n)", "Single recursive call with constant or logarithmic work per call."
            else:
                return f"O(n^2) or O(n log n)", f"1 call, {work_big_o} work (if work dominates) or n log n (ex: Merge Sort analysis)."
        if calls > 1:
            if work_rank <= work_o1:
                return f"O({calls}^n) or O(n^{calls})", f"{calls} recursive calls with constant work per call."
            else:
                return f"O(n log n) or O(n^{calls})", f"{calls} recursive calls with {work_big_o} work per call."
            
        return "O(inf)", "Unknown Complexity."

class RecursiveCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.recursive_calls = {}

    def visit_FunctionDef(self, node):
        self.recursive_calls[node.name] = node
        return