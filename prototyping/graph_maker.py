import parser as prs
import lexer as lx
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

def make_graph(expr_list: list[prs.Expr]) -> str:
    to_return = html_template
    calc_state = calc_template
    latex_expressions = ""
    for i, expr in enumerate(expr_list):
        if expr.token.id == lx.TOKEN_DOLLAR_ID: # This is a dollar expression, it's already been handled
            continue

        if i < len(expr_list)-1: # There's still an element left
            next_expr = expr_list[i+1]
            if next_expr.token.id == lx.TOKEN_DOLLAR_ID: # Next is a dollar expression

                # What if current expression is a slider
                if expr.token.id == lx.TOKEN_EQUAL_ID:
                    if expr.left.token.id == lx.TOKEN_VARIABLE_ID: # These ifs tell us current expression is a slider
                        # The argument structure is ($ <of> ((start <,> stop)<,> step))
                        slider_min_expr = next_expr.right.left.left # This will exist if syntax is ok
                        slider_max_expr = next_expr.right.left.right 
                        slider_step_expr = next_expr.right.right
                        latex_expressions += f"""{{"type": "expression", "id":"{i}", "latex": "{expr.latex().replace("\\","\\\\")}","slider":{{"min": {slider_min_expr.latex()}, "max": {slider_max_expr.latex()}, "step": {slider_step_expr.latex()}, "hardMin": true, "hardMax":true}}}}{","if i != len(expr_list)-1 else ""}\n"""
                        continue

        latex_expressions += f"""{{"type": "expression", "id":"{i}", "latex": "{expr.latex().replace("\\","\\\\")}"}}{","if i != len(expr_list)-1 else ""}\n"""
    return to_return.replace("GRAPHDATA", calc_state.replace("EXPRESSIONS", latex_expressions))



