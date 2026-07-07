import parser as prs
import lexer as lx
import ast_ as ast_
api_key = "3811e14e71e14f2b83d5fea5e2e13075"
graph_template = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Generated Desmos Graph</title>
  <script src="https://www.desmos.com/api/v1.11/calculator.js?apiKey={api_key}"></script>
  <style>
    html, body {{ margin: 0; height: 100%; }}
    #calculator {{ width: 100%; height: 100%; }}
  </style>
</head>
<body>
  <div id="calculator"></div>

  <script>
    var elt = document.getElementById('calculator');
    var calculator = Desmos.GraphingCalculator(elt);

    const expressions = [EXPRESSIONS];

    expressions.forEach(expr => calculator.setExpression(expr));
  </script>
</body>
</html>
"""

html_template = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Generated Desmos Graph</title>
  <script src="https://www.desmos.com/api/v1.11/calculator.js?apiKey={api_key}"></script>
  <style>
    html, body {{ margin: 0; height: 100%; }}
    #calculator {{ width: 100%; height: 100%; }}
  </style>
</head>
<body>
  <div id="calculator"></div>

  <script>
    var elt = document.getElementById('calculator');
    var calculator = Desmos.GraphingCalculator(elt);

    const graphdata = GRAPHDATA

    calculator.setState(graphdata);
  </script>
</body>
</html>
"""
API_VERSION = 11
XMIN = -10
XMAX = 10
YMIN = -10
YMAX = 10
json_template = f"""
{{
  "version": {API_VERSION},
  "graph": {{
    "viewport": {{
      "xmin": {XMIN},
      "xmax": {XMAX},
      "ymin": {YMIN},
      "ymax": {YMAX}
    }}
  }},
  "expressions": {{
    "list": [EXPRESSIONS]
  }}
}}
"""
"""
      {{
        "type": "expression",
        "id": "1",
        "latex": "y=x^2",
        "color": "#c74440"
      }},
      {{
        "type": "expression",
        "id": "2",
        "latex": "y=\\sin(x)"
      }},
      {{
        "type": "expression",
        "id": "a",
        "latex": "a=2",
        "sliderBounds": {{
          "min": 0,
          "max": 10
        }}
      }}
"""
calc_template = f"""{{
    version: {API_VERSION},
    graph: {{
        viewport: {{xmin: {XMIN}, xmax: {XMAX}, ymin: {YMIN}, ymax: {YMAX}}}
    }},
    expressions : {{
        list : [EXPRESSIONS]
    }}
}}
"""

def make_graph(ast: ast_.AST) -> str:
    to_return = html_template
    calc_state = calc_template
    latex_expressions = ""
    for i, node in enumerate(ast.ast):
        if node.nodetype == ast_.ASTNode.DollarExpr: # This is a dollar expression, it's already been handled
            continue

        if i < len(ast.ast)-1: # There's still an element left
            next_node = ast.ast[i+1]
            if next_node.nodetype == ast_.ASTNode.DollarExpr: # Next is a dollar expression

                # What if current expression is a slider (assignment of a variable to a number)
                if node.nodetype == ast_.ASTNode.VarAssign and node.getType() == ast_.TYPE_NUM:
                    # The argument structure is ($ <of> ((start <,> stop)<,> step))
                    # And if it's defaults, we just let it be as is, without modifying the parameter
                    for expr in next_node.dollar_list:
                        if expr.token.id != lx.TOKEN_PLACEHOLDER_ID and ast.getExprTypeFromGlobalContext(expr) != ast_.TYPE_NUM:
                            raise Exception(f"The type in dollar expressions should be a number, the expression was {expr} instead")

                    min_str = ""
                    max_str = ""
                    step_str = ""
                    l = len(next_node.dollar_list)
                    # Going through the parameters, and checking for placeholders
                    if l > 0:
                        slider_min_expr = next_node.dollar_list[0]
                        if slider_min_expr.token.id != lx.TOKEN_PLACEHOLDER_ID:
                            min_str = f""" "min": "{slider_min_expr.latex()}", "hardMin": true """
                    if l>1:
                        slider_max_expr = next_node.dollar_list[1]
                        if slider_max_expr.token.id != lx.TOKEN_PLACEHOLDER_ID:
                            max_str = f""" "max": "{slider_max_expr.latex()}", "hardMax": true """
                    if l>2:
                        slider_step_expr = next_node.dollar_list[2]
                        if slider_step_expr.token.id != lx.TOKEN_PLACEHOLDER_ID:
                            step_str = f""" "step": "{slider_step_expr.latex()}" """

                    latex_expressions += f"""{{"type": "expression", "id":"{i}", "latex": "{node.expr.latex()}" """


                    if min_str == "" and max_str == "" and step_str == "": # We have no changes from the default, add a parenthesis (and maybe a comma) and we're done
                        latex_expressions += f"}}{",\n"if i != len(ast.ast)-1 else ""}"
                        continue
                    latex_expressions += """, "slider": {"""
                    if min_str != "":
                        latex_expressions += min_str
                    if max_str != "":
                        if min_str != "":
                            latex_expressions += ","
                        latex_expressions += max_str
                    if step_str != "":
                        if min_str != "" or max_str != "":
                            latex_expressions += ","
                        latex_expressions += step_str
                    latex_expressions += f"}}}}{",\n"if i != len(ast.ast)-1 else ""}"
                    continue

        latex_expressions += f"""{{"type": "expression", "id":"{i}", "latex": "{node.expr.latex()}"}}{","if i != len(ast.ast)-1 else ""}\n"""
    return to_return.replace("GRAPHDATA", calc_state.replace("EXPRESSIONS", latex_expressions))

# def make_graph(ast: ast_.AST) -> str:
#     to_return = html_template
#     calc_state = calc_template
#     latex_expressions = ""
#     for i, node in enumerate(ast.ast):
#         if expr.token.id == lx.TOKEN_DOLLAR_ID: # This is a dollar expression, it's already been handled
#             continue
#
#         if i < len(expr_list)-1: # There's still an element left
#             next_expr = expr_list[i+1]
#             if next_expr.token.id == lx.TOKEN_DOLLAR_ID: # Next is a dollar expression
#
#                 # What if current expression is a slider
#                 if expr.token.id == lx.TOKEN_EQUAL_ID:
#                     if expr.left.token.id == lx.TOKEN_VARIABLE_ID: # These ifs tell us current expression is an assignment of a constant
#                         if expr.right.token.id == lx.TOKEN_NUM_ID: # Then we are certain it's a slider
#                             # The argument structure is ($ <of> ((start <,> stop)<,> step))
#                             # And if it's defaults, we just let it be as is, without modifying the parameter
#                             slider_min_expr = next_expr.right.left # This will exist if syntax is ok
#                             slider_max_expr = next_expr.right.right.left 
#                             slider_step_expr = next_expr.right.right.right
#                             latex_expressions += f"""{{"type": "expression", "id":"{i}", "latex": "{expr.latex()}" """
#                             min_str = ""
#                             max_str = ""
#                             step_str = ""
#                             if slider_min_expr.token.id != lx.TOKEN_PLACEHOLDER_ID:
#                                 min_str = f""" "min": "{slider_min_expr.latex()}", "hardMin": true """
#                             if slider_max_expr.token.id != lx.TOKEN_PLACEHOLDER_ID:
#                                 max_str = f""" "max": "{slider_max_expr.latex()}", "hardMax": true """
#                             if slider_step_expr.token.id != lx.TOKEN_PLACEHOLDER_ID:
#                                 step_str = f""" "step": "{slider_step_expr.latex()}" """
#
#                             if min_str == "" and max_str == "" and step_str == "": # We have no changes from the default, add a parenthesis (and maybe a comma) and we're done
#                                 latex_expressions += f"}}{",\n"if i != len(expr_list)-1 else ""}"
#                                 continue
#                             latex_expressions += """, "slider": {"""
#                             if min_str != "":
#                                 latex_expressions += min_str
#                             if max_str != "":
#                                 if min_str != "":
#                                     latex_expressions += ","
#                                 latex_expressions += max_str
#                             if step_str != "":
#                                 if min_str != "" or max_str != "":
#                                     latex_expressions += ","
#                                 latex_expressions += step_str
#                             print(step_str, slider_step_expr)
#                             latex_expressions += f"}}}}{",\n"if i != len(expr_list)-1 else ""}"
#                             # latex_expressions
#                             # ""","slider":{{"min": {slider_min_expr.latex()}, "max": {slider_max_expr.latex()}, "step": {slider_step_expr.latex()}, "hardMin": true, "hardMax":true}}}}{","if i != len(expr_list)-1 else ""}\n"""
#                             continue
#
#         latex_expressions += f"""{{"type": "expression", "id":"{i}", "latex": "{expr.latex()}"}}{","if i != len(expr_list)-1 else ""}\n"""
#     return to_return.replace("GRAPHDATA", calc_state.replace("EXPRESSIONS", latex_expressions))
