import lexer as lx
import parser as prs
import graph_maker as gmk
import ast_

def compile(filepath: str, outfilepathname: str):
    with open(filepath, "r") as f_in:
        # parse_result = prs.parse(lx.tokenize_str(f_in.read()))
        t = lx.tokenize_str(f_in.read())
        t.print()
        parse_result = prs.parse(t)
        # TODO: Check for errors in latex code
        # latex = prs.latexify_parse(parse_result)
        
        # We then go through the parse, and extract the expressions in raw, which'll constitute raw latex expressions
        raw_expressions = []
        for expr in parse_result:
            if isinstance(expr, list):
                if isinstance(expr[0], prs.Expr):
                    if expr[0].token.id == lx.TOKEN_RAW_ID:
                        raw_expressions += get_expr_list_from_nest(expr[1])

        ast = ast_.AST(raw_expressions)
        # for a in ast.ast:
        #     print("ast-print", a)
        print("context", ast.context)
        types = [node.getType() for node in ast.ast]
        for i in range(len(types)):
            print("ast-print", types[i], ast.ast[i])
        
        # TODO: The rest
        graph_html = gmk.make_graph(ast)
        with open(outfilepathname+".html", "w+") as f_out:
            f_out.write(graph_html)

def get_expr_list_from_nest(nest) -> list[prs.Expr]:
    """This creates a list of expressions, from a nest of expressions in lists and sublists and whatnot
    """
    output: list[prs.Expr] = []
    if isinstance(nest, prs.Expr):
        output = [nest]
    elif isinstance(nest, list):
        for expr in nest:
            output+=get_expr_list_from_nest(expr)
    return output



