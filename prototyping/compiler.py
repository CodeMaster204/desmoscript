import lexer as lx
import parser as prs
import graph_maker as gmk


def compile(filepath: str, outfilepathname: str):
    with open(filepath, "r") as f_in:
        parse_result = prs.parse(lx.tokenize_str(f_in.read()))
        # TODO: Check for errors in latex code
        # latex = prs.latexify_parse(parse_result)
        
        # We then go through the parse, and extract the expressions in raw, which'll constitute raw latex expressions
        raw_expressions = []
        for expr in parse_result:


        # TODO: The rest
        graph_html = gmk.make_graph(parse_result)
        with open(outfilepathname+".html", "w+") as f_out:
            f_out.write(graph_html)

