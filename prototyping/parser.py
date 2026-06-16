"""

This file implements the parser(pratt parsing) behind desmoscript's prototype
"""
import lexer as lx
from typing import List


EXPR_ATOM = 0
EXPR_BIN = 1
EXPR_PRE = 2
EXPR_POST = 3

class Expr():
    def __init__(self, token: lx.Token, op_type=EXPR_ATOM):
        """Initializes an expression

        Args:
            token: The token associated to the top part of the expression
            op_type : 0 for an "atom", 1 for binary operator, 2 for prefix and 3 for postfix
        """
        self.is_bin_op = 0
        self.token = token
        self.left: None | Expr = None
        self.right: None | Expr = None
        self.op_type = op_type

    def __repr__(self):
        if self.op_type != EXPR_ATOM:

            if self.op_type == EXPR_BIN:
                if not (isinstance(self.left, Expr) and isinstance(self.right, Expr)):
                    raise Exception(f"This binary operator {self.token} has left {self.left} and right {self.right} with types {type(self.left)} and {type(self.right)} respectively. At least one of them isn't a parse unit")
                return f"({self.left} {self.token} {self.right})"

            if self.op_type == EXPR_PRE: 
                if not isinstance(self.right, Expr):
                    raise Exception(f"This prefix operator {self.token} has right {self.right} with type {type(self.right)}. It isn't a parse unit")
                return f"({self.token} {self.right})"

            if self.op_type == EXPR_POST: 
                if not isinstance(self.left, Expr):
                    raise Exception(f"This postfix operator {self.token} has left {self.left} with type {type(self.right)}. It isn't a parse unit")
                return f"({self.left} {self.token})"
        return f"{self.token}"

    def latex(self):
        match self.token.id:
            case lx.TOKEN_INVALID_ID:
                raise Exception("Cannot generate latex for an invalid token")

            case lx.TOKEN_NUM_ID | lx.TOKEN_VARIABLE_ID:
                return self.token.latex()

            case lx.TOKEN_PLUS_ID:
                return self.left.latex() + "+" + self.right.latex()

            case lx.TOKEN_MINUS_ID:
                if self.op_type == EXPR_BIN:
                    return self.left.latex() + "-" + self.right.latex()
                else:
                    return "-"+self.right.latex()

            case lx.TOKEN_MULT_ID:
                return self.left.latex() + "\\cdot " + self.right.latex()

            case lx.TOKEN_DIV_ID:
                return "\\frac{"+ self.left.latex() + "}{" + self.right.latex()+"}"

            case lx.TOKEN_EXP_ID:
                return self.left.latex() + "^{" + self.right.latex()+"}"

            case lx.TOKEN_LPAREN_ID:
                if self.op_type == EXPR_BIN: # Used as an evaluation operator
                    return self.left.latex() + "\\left(" + self.right.latex() + "\\right)"
                if self.op_type == EXPR_PRE:
                    return "\\right("+self.right.latex() + "\\right)"
                raise Exception("A left parenthesis needs to either be a binary of prefix operator")

            case lx.TOKEN_LCUR_ID:
                raise Exception("A left curly bracket shouldn't appear in latex")

            case lx.TOKEN_LBRA_ID:
                raise Exception("A left bracket shouldn't appear in latex, at least for now")

            case lx.TOKEN_RPAREN_ID:
                raise Exception("A right parenthesis should not appear alone, yet here it is being latexified")

            case lx.TOKEN_RCUR_ID:
                raise Exception("A right curly bracket should not appear alone, yet here it is being latexified")

            case lx.TOKEN_RBRA_ID:
                raise Exception("A right bracket should not appear alone, yet here it is being latexified")
            
            case lx.TOKEN_END_ID:
                return "\n"

            case lx.TOKEN_EQUAL_ID:
                return self.left.latex() + "=" +self.right.latex()

                # --- Desmos keywords
            case lx.TOKEN_COS_ID:
                return self.token.latex()

                # --- Desmoscript keywords
            case lx.TOKEN_RAW_ID:
                return self.token.latex()

            case _:
                raise Exception(f"Attempted latexification on unknown id: {self.token.id}")


class ExprList:
    def __init__(self, token: lx.Token, op_type):
        self.token = token
        self.data: List[Expr] = []
        self.op_type = op_type
        self.left = None
        self.right = None




def nud_num(token, token_list):
    return Expr(token)

def nud_var(token, token_list):
    return Expr(token)

def nud_dsm_func(token: lx.Token, token_list):
    """Function for desmos default keywords, like cos, int or prod
    """
    match token.id:
        case lx.TOKEN_COS_ID:
            # Those are functions of some arguments, and act as function calls, meaning the led_lparen will handle everything for us
            return Expr(token)

def nud_dsmsp_kw(token, token_list):
    """Function for desmoscript default keywords, like raw
    """
    match token.id:
        case lx.TOKEN_RAW_ID:
            # Those are "environment delimiters", meaning that after them should come a pair of {} in which a special environment will be defined. These keywords act as prefix operators
            to_return = ExprList(token, EXPR_PRE)
            to_return.right = parse_lines(token_list, 0)
    return Expr(token)

def nud_plus(token, token_list):
    return Expr(token)

def nud_minus(token, token_list):
    to_return = Expr(token, 2)
    to_return.right = parse_line(token_list, rbp_table[lx.TOKEN_MINUS_ID])
    return to_return

def nud_lparen(token, token_list): # We don't need a nud for rparen. This function is used when () is used as a grouping tool, like (a+b)*c
    # We parse the rest as normal. Since the right parenthesis will have the place of an operator, and
    # has a lbp of -1, the following will return as soon as a right parenthesis is detected.
    # TODO: Check that pairs of parentheses get detected, and reported
    return parse_line(token_list, rbp_table[token.id]) 

def nud_lcur(token, token_list): # This one works as nud_lparen does, except it causes another full multiline-parse, instead
    # of a simple "rest of expression" parse like the ( does
    # TODO: Check that pairs of parentheses get detected, and reported
    return parse_lines(token_list, rbp_table[token.id]) 

nud_lbra = nud_lparen # Same mechanics as for the left parenthesis

def nud_none(token, token_list):
    raise Exception(f"Tried generating a nud for something ({token}) which doesn't have one: id: {token.id}")


def led_bin_op(left, token, token_list):
    to_return = Expr(token, EXPR_BIN)
    to_return.left = left
    to_return.right = parse_line(token_list, rbp_table[token.id])
    return to_return

def led_equal(left, token, token_list): # TODO: Check whether = is used correctly. I believe doing this once we actually have the whole parse is better. As in a general rules/syntax checker
    to_return = Expr(token, EXPR_BIN)
    to_return.left = left
    to_return.right = parse_line(token_list, rbp_table[token.id])
    return to_return


def led_rparen(left, token, token_list):
    # The right parenthesis should return whatever the expression was before, that is, the left, and get itself out of the way
    return left

led_rcur = led_rparen # Same mechanics as the right parenthesis
led_rbra = led_rparen 

def led_none(left, token, token_list):
    raise Exception(f"Tried generating a led for a token which doesn't have one. Token id: {token.id}")


lbp_table = {
             lx.TOKEN_INVALID_ID: None,
             lx.TOKEN_NUM_ID: None,
             lx.TOKEN_VARIABLE_ID: None,
             lx.TOKEN_PLUS_ID: 20,
             lx.TOKEN_MINUS_ID: 20,
             lx.TOKEN_MULT_ID: 30,
             lx.TOKEN_DIV_ID: 30,
             lx.TOKEN_EXP_ID: 41,
             lx.TOKEN_EQUAL_ID: 10,
             lx.TOKEN_END_ID: 4,
             lx.TOKEN_EOF_ID: 0,
             lx.TOKEN_LPAREN_ID: 100,
             lx.TOKEN_RPAREN_ID: 5, # We want to return as soon as we see this
             lx.TOKEN_LCUR_ID: 100,
             lx.TOKEN_RCUR_ID: -10,
             lx.TOKEN_LBRA_ID: 100,
             lx.TOKEN_RBRA_ID: 2,

             # --- Desmos keywords
             lx.TOKEN_COS_ID: None,
             
             # --- Desmoscript keywords
             lx.TOKEN_RAW_ID: None,
             }

rbp_table = {
             lx.TOKEN_INVALID_ID: None,
             lx.TOKEN_NUM_ID: None,
             lx.TOKEN_VARIABLE_ID: None,
             lx.TOKEN_PLUS_ID: 21,
             lx.TOKEN_MINUS_ID: 21,
             lx.TOKEN_MULT_ID: 31,
             lx.TOKEN_DIV_ID: 31,
             lx.TOKEN_EXP_ID: 40,
             lx.TOKEN_EQUAL_ID: 11,
             lx.TOKEN_END_ID: 4,
             lx.TOKEN_EOF_ID: 0,
             lx.TOKEN_LPAREN_ID: 7, # Just enough to sniff out a right parenthesis
             lx.TOKEN_RPAREN_ID: None,
             lx.TOKEN_LCUR_ID: -10,
             lx.TOKEN_RCUR_ID: None,
             lx.TOKEN_LBRA_ID: 3, # Just enough to sniff out a right bracket
             lx.TOKEN_RBRA_ID: None,

             # --- Desmos keywords
             lx.TOKEN_COS_ID: None,
             
             # --- Desmoscript keywords
             lx.TOKEN_RAW_ID: None,
             }

nud_table = {
             lx.TOKEN_INVALID_ID: nud_none,
             lx.TOKEN_NUM_ID: nud_num,
             lx.TOKEN_VARIABLE_ID: nud_var,
             lx.TOKEN_PLUS_ID: nud_plus,
             lx.TOKEN_MINUS_ID: nud_minus,
             lx.TOKEN_MULT_ID: nud_none,
             lx.TOKEN_DIV_ID: nud_none,
             lx.TOKEN_EXP_ID: nud_none,
             lx.TOKEN_EQUAL_ID: nud_none,
             lx.TOKEN_END_ID: nud_none,
             lx.TOKEN_EOF_ID: nud_none,
             lx.TOKEN_LPAREN_ID: nud_lparen,
             lx.TOKEN_RPAREN_ID: nud_none,
             lx.TOKEN_LCUR_ID: nud_lcur,
             lx.TOKEN_RCUR_ID: nud_none,
             lx.TOKEN_LBRA_ID: nud_lbra,
             lx.TOKEN_RBRA_ID: nud_none,

             # --- Desmos keywords
             lx.TOKEN_COS_ID: nud_dsm_func,
             
             # --- Desmoscript keywords
             lx.TOKEN_RAW_ID: nud_dsmsp_kw,
             }

led_table = {
             lx.TOKEN_INVALID_ID: led_none,
             lx.TOKEN_NUM_ID: led_none,
             lx.TOKEN_VARIABLE_ID: led_none,
             lx.TOKEN_PLUS_ID: led_bin_op,
             lx.TOKEN_MINUS_ID: led_bin_op,
             lx.TOKEN_MULT_ID: led_bin_op,
             lx.TOKEN_DIV_ID: led_bin_op,
             lx.TOKEN_EXP_ID: led_bin_op,
             lx.TOKEN_EQUAL_ID: led_equal, 
             lx.TOKEN_END_ID: led_none,
             lx.TOKEN_EOF_ID: led_none,
             lx.TOKEN_LPAREN_ID: led_bin_op, #led_lparen,
             lx.TOKEN_RPAREN_ID: led_rparen,
             lx.TOKEN_LCUR_ID: led_bin_op,
             lx.TOKEN_RCUR_ID: led_rcur,
             lx.TOKEN_LBRA_ID: led_bin_op,
             lx.TOKEN_RBRA_ID: led_rbra,

             # --- Desmos keywords
             lx.TOKEN_COS_ID: led_none,
             
             # --- Desmoscript keywords
             lx.TOKEN_RAW_ID: led_none,
             }


def parse_line(token_list: lx.TokenList, min_bp) -> Expr:
    token: lx.Token = token_list.advance()

    if token == lx.TOKEN_INVALID:
        raise Exception("Token was invalid, in nud parsing")
    if token.id == lx.TOKEN_END_ID:
        raise Exception("There was a newline token in the nud part of parse_line")
    if token.id == lx.TOKEN_EOF_ID:
        raise Exception("There was an eof token in the nud part of parse_line")

    left = nud_table[token.id](token, token_list)
    while lbp_table[token_list.peek().id] > min_bp:

        token: lx.Token = token_list.advance()

        if token == lx.TOKEN_INVALID:
            raise Exception("Token was invalid, in led parsing")
        if token == lx.TOKEN_END_ID:
            raise Exception("There was a newline token in the parse_line function's loop. Min_bp should be 4 or greater, if not this may happen.")
        if token == lx.TOKEN_EOF_ID:
            raise Exception("There was an eof token in the parse_line function's loop. Min_bp should be 0 or greater, if not this may happen.")

        left = led_table[token.id](left, token, token_list)

    print(token_list.peek())
    match token_list.peek().id:
        case lx.TOKEN_RPAREN_ID:
            token_list.advance()
    return left

def parse_lines(token_list: lx.TokenList, min_bp):
    result: List[Expr] = []

    while not token_list.isFull():
        peekaboo = token_list.peek()
        match peekaboo.id:
            case lx.TOKEN_END_ID | lx.TOKEN_EOF_ID:
                token_list.advance()
                continue
        if not lbp_table[peekaboo.id] is None:
            print(peekaboo, min_bp, lbp_table[peekaboo.id])
            if lbp_table[peekaboo.id] <= min_bp:
                break
        parse_result = parse_line(token_list, lbp_table[lx.TOKEN_END_ID]) # This will parse by line
        print("parse_result", parse_result)
        result.append(parse_result)
        # peekaboo = token_list.peek()
        # if not lbp_table[peekaboo.id] is None:
        #     if lbp_table[peekaboo.id] <= min_bp:
        #         print("trying!!")
        #         print(parse_line(token_list, 0))
        #         break
    return result

def parse(token_list: lx.TokenList) -> List[Expr]:
    result: List[Expr] = []

    while not token_list.isFull():
        peekaboo = token_list.peek()
        match peekaboo.id:
            case lx.TOKEN_END_ID:
                token_list.advance()
                continue
            case lx.TOKEN_RCUR_ID:
                token_list.advance()
                continue
            case lx.TOKEN_EOF_ID:
                break
        parse_result = parse_line(token_list, 4) 
        print("AA", parse_result)

        if not(parse_result is None):
            result.append(parse_result)
    return result

def print_parse(expr_list: List[Expr]):
    for expr in expr_list:
        print(f"{expr}")

def latexify_parse(expr_list: List[Expr]):
    result = ""
    for i in range(len(expr_list)):
        result += expr_list[i].latex()
        if i != len(expr_list):
            result += "\n"
    return result

if __name__ == "__main__":
    # toparse = "-a* b ^ c * (d + b) + f(a*b) \n a+ 2 * 4 \n a=3+5"
    # toparse = "a + b* c+d^e"
    # toparse = "-a ^ b"
    # toparse = "a^(b+c)+d"
    toparse = """
    {{2+3=5}
    cos(2*3) + cosh = 6^x
    4*x + ((56*g)/4)
    }
    a + b = 3
    """
    # toparse = "2+((56*g)/4)"
    
    token_list = lx.tokenize_str(toparse)
    print(toparse)
    token_list.print()

    # print(token_list.advance())
    # parsed = parse_lines(token_list, -20)
    # print_parse(parsed)

    parsed = parse(token_list)
    print(parsed)
    print_parse(parsed)
    
    # parsed = parse(token_list)
    # print_parse(parsed)
    # print(latexify_parse(parsed))
    # print_parse(parsed)  

