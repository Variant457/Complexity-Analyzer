import ast

class PythonComplexityAnalyzer:
    """
    Python-only complexity analyzer for iterative code.
    Ignores recursion but flags recursive functions.
    """

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
    def get_complexity_rank(complexity: str):
        if "O(n^" in complexity:
            power = int(complexity.split('^')[-1].replace(")", ""))
            return 3 + power 
        
        if " or " in complexity:
            parts = complexity.split(" or ")
            return max(PythonComplexityAnalyzer.get_complexity_rank(p.strip().split(' ')[0]) for p in parts)
        
        return PythonComplexityAnalyzer.ComplexityRanks.get(complexity, -1)
    
    def analyze(self, code: str):
        try:
            tree = ast.parse(code)
        except Exception as e:
            return {"error": f"Python parse error: {e}"}

        loop_stats = {"count": 0, "max_nesting": 0}
        recursive_funcs = []

        def visit(node, depth=0, current_func=None):
            nonlocal loop_stats, recursive_funcs

            # Loops
            if isinstance(node, (ast.For, ast.While)):
                loop_stats["count"] += 1
                loop_stats["max_nesting"] = max(loop_stats["max_nesting"], depth + 1)
                for child in ast.iter_child_nodes(node):
                    visit(child, depth + 1, current_func)
                return

            # Function definitions
            if isinstance(node, ast.FunctionDef):
                # check if function calls itself
                calls_self = any(
                    isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == node.name
                    for n in ast.walk(node)
                )
                if calls_self:
                    recursive_funcs.append(node.name)
                # visit children without increasing depth
                for child in ast.iter_child_nodes(node):
                    visit(child, 0, node.name)
                return

            for child in ast.iter_child_nodes(node):
                visit(child, depth, current_func)

        visit(tree)

        # Determine iterative Big-O
        max_depth = loop_stats["max_nesting"]
        if loop_stats["count"] == 0:
            big_o = "O(1)"
        elif max_depth == 1:
            big_o = "O(n)"
        else:
            big_o = f"O(n^{max_depth})"

        explanation = f"Detected {loop_stats['count']} loop(s) with maximum nesting {max_depth}."
        if recursive_funcs:
            explanation += f" Recursive function(s) detected: {', '.join(recursive_funcs)}. "
            explanation += "Recursion will be analyzed by the Recursive Analyzer service."

        return {
            "big_o": big_o,
            "loops_count": loop_stats["count"],
            "max_loop_nesting": max_depth,
            "recursive_functions": recursive_funcs,
            "explanation": explanation
        }