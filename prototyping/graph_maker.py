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


                # Dollar expressions for points
                # Format is
                # color opacity thickness   shape   draggable   label
                # outline   anchor for label
                if (node.nodetype == ast_.ASTNode.VarAssign and node.getType() == ast_.TYPE_POINT) or \
                    (node.nodetype == ast_.ASTNode.Instance and node.getType() == ast_.TYPE_POINT):

                    config_strs = ["" for i in range(8)] # TODO: Check the range is good

                    expected_types_with_context = [
                            (ast_.TYPE_COLOR, None),                    # Color
                            (ast_.TYPE_NUM, None),                       # opacity
                            (ast_.TYPE_NUM, None),                       # Thickness
                            (ast_.TYPE_PTSHAPE, ast_.CONTEXT_PTSHAPE),   # Shape
                            (ast_.TYPE_PTDRAG, ast_.CONTEXT_PTDRAG),    # Draggable
                            #(ast_.TYPE_str,)                            # Label
                            (ast_.TYPE_NUM, None),                            # Outline
                            (ast_.TYPE_NUM, None),                             # Anchor
                    ]

                    latex_expressions += f"""{{"type": "expression", "id":"{i}", "latex": "{node.expr.latex()}" """
                    print("dollar_list:", next_node.dollar_list)

                    for i in range(min(len(next_node.dollar_list), 5)): # TODO: Take 5 up to the whole 8 argument
                        if next_node.dollar_list[i].token.id != lx.TOKEN_PLACEHOLDER_ID:
                            if ast.getExprTypeFromExtendedContext(next_node.dollar_list[i], expected_types_with_context[i][1]) != expected_types_with_context[i][0]:
                                raise Exception(f"Expected type {expected_types_with_context[i][0]} for {i}-th argument (here {next_node.dollar_list[i]}) for point dollar expression, got {ast.getExprTypeFromGlobalContext(next_node.dollar_list[i])}")
                            match i:
                                case 0: # Color
                                    config_strs[i] = f', "colorLatex": "{next_node.dollar_list[i].latex()}"'
                                case 1: # Opacity
                                    config_strs[i] = f', "pointOpacity": "{next_node.dollar_list[i].latex()}"'
                                case 2: # Thickness
                                    latex = next_node.dollar_list[i].latex()
                                    config_strs[i] = f', "pointSize": "{latex}", "movablePointSize": "{latex}"'
                                case 3: # Shape
                                    config_strs[i] = lx.ptshape_token_to_latex[next_node.dollar_list[i].token] # It is embedded inside of the data of the token itself
                                case 4: # Draggable
                                    config_strs[i] = lx.ptdrag_token_to_latex[next_node.dollar_list[i].token]
                            latex_expressions += config_strs[i]

                    # And we finish off
                    latex_expressions += f"}}{",\n"if i != len(ast.ast)-1 else ""}"
                    continue



                # Dollar expressions for functions (instances and function definitions, which are of type number if they are even visible)
                # Format is
                # color opacity thickness   style
                if (node.nodetype == ast_.ASTNode.FuncDef ) or \
                    (node.nodetype == ast_.ASTNode.Instance and node.getType() == ast_.TYPE_NUM):

                    config_strs = ["" for i in range(4)] # TODO: Check the range is good

                    expected_types_with_context = [
                            (ast_.TYPE_COLOR, None),                    # Color
                            (ast_.TYPE_NUM, None),                       # opacity
                            (ast_.TYPE_NUM, None),                       # Thickness
                            (ast_.TYPE_LINESTYLE, ast_.CONTEXT_LINESTYLE),   # Style
                    ]

                    latex_expressions += f"""{{"type": "expression", "id":"{i}", "latex": "{node.expr.latex()}" """
                    print("dollar_list:", next_node.dollar_list)

                    for i in range(min(len(next_node.dollar_list), 4)): 
                        if next_node.dollar_list[i].token.id != lx.TOKEN_PLACEHOLDER_ID:
                            if ast.getExprTypeFromExtendedContext(next_node.dollar_list[i], expected_types_with_context[i][1]) != expected_types_with_context[i][0]:
                                raise Exception(f"Expected type {expected_types_with_context[i][0]} for {i}-th argument (here {next_node.dollar_list[i]}) for point dollar expression, got {ast.getExprTypeFromGlobalContext(next_node.dollar_list[i])}")
                            match i:
                                case 0: # Color
                                    config_strs[i] = f', "colorLatex": "{next_node.dollar_list[i].latex()}"'
                                case 1: # Opacity
                                    config_strs[i] = f', "lineOpacity": "{next_node.dollar_list[i].latex()}"'
                                case 2: # Thickness
                                    config_strs[i] = f', "lineWidth": "{next_node.dollar_list[i].latex()}"'
                                case 3: # Shape
                                    config_strs[i] = lx.linestyle_token_to_latex[next_node.dollar_list[i].token] # It is embedded inside of this dict 
                            latex_expressions += config_strs[i]

                    # And we finish off
                    latex_expressions += f"}}{",\n"if i != len(ast.ast)-1 else ""}"
                    continue

                # Dollar expressions for polygons
                # Format is
                # color opacity thickness linestyle fill_opacity
                if (node.nodetype == ast_.ASTNode.Instance and node.getType() == ast_.TYPE_POLYGON):

                    config_strs = ["" for i in range(5)] # TODO: Check the range is good

                    expected_types_with_context = [
                            (ast_.TYPE_COLOR, None),                    # Color
                            (ast_.TYPE_NUM, None),                      # Fill opacity
                            (ast_.TYPE_NUM, None),                       # opacity
                            (ast_.TYPE_NUM, None),                       # Thickness
                            (ast_.TYPE_LINESTYLE, ast_.CONTEXT_LINESTYLE),   # Style
                    ]

                    latex_expressions += f"""{{"type": "expression", "id":"{i}", "latex": "{node.expr.latex()}" """
                    print("dollar_list:", next_node.dollar_list)

                    for i in range(min(len(next_node.dollar_list), 5)): 
                        if next_node.dollar_list[i].token.id != lx.TOKEN_PLACEHOLDER_ID:
                            if ast.getExprTypeFromExtendedContext(next_node.dollar_list[i], expected_types_with_context[i][1]) != expected_types_with_context[i][0]:
                                raise Exception(f"Expected type {expected_types_with_context[i][0]} for {i}-th argument (here {next_node.dollar_list[i]}) for point dollar expression, got {ast.getExprTypeFromGlobalContext(next_node.dollar_list[i])}")
                            match i:
                                case 0: # Color
                                    config_strs[i] = f', "colorLatex": "{next_node.dollar_list[i].latex()}"'
                                case 1: # Fill opacity
                                    config_strs[i] = f', "fillOpacity": "{next_node.dollar_list[i].latex()}"'
                                case 2: # Opacity
                                    config_strs[i] = f', "lineOpacity": "{next_node.dollar_list[i].latex()}"'
                                case 3: # Thickness
                                    config_strs[i] = f', "lineWidth": "{next_node.dollar_list[i].latex()}"'
                                case 4: # Shape
                                    config_strs[i] = lx.linestyle_token_to_latex[next_node.dollar_list[i].token] # It is embedded inside of this dict 
                            latex_expressions += config_strs[i]

                    # And we finish off
                    latex_expressions += f"}}{",\n"if i != len(ast.ast)-1 else ""}"
                    continue








                    

                    latex_expressions += f"""{{"type": "expression", "id":"{i}", "latex": "{node.expr.latex()}" """

        latex_expressions += f"""{{"type": "expression", "id":"{i}", "latex": "{node.expr.latex()}"}}{","if i != len(ast.ast)-1 else ""}\n"""
    return to_return.replace("GRAPHDATA", calc_state.replace("EXPRESSIONS", latex_expressions))

