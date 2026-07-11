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

    def latex(self, previous=lx.TOKEN_INVALID_ID):
        """Generates the latex expression for something, by calling recursively

        Args:
            previous (lx.token_id): the token id of the previous caller. Put lx.TOKEN_INVALID_ID if you don't care (say, are calling this one from nowhere)

        Returns:
            the latex expression
        """
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
                if self.left.token.id == lx.TOKEN_NUM_ID and self.right.token.id == lx.TOKEN_VARIABLE_ID:
                    return self.left.latex() + self.right.latex() 
                return self.left.latex() + "\\\\cdot " + self.right.latex()

            case lx.TOKEN_DIV_ID:
                return "\\\\frac{"+ self.left.latex() + "}{" + self.right.latex()+"}"

            case lx.TOKEN_EXP_ID:
                return self.left.latex() + "^{" + self.right.latex()+"}"

            case lx.TOKEN_LPAREN_ID:
                if self.op_type == EXPR_BIN: # Used as an evaluation operator
                    return self.left.latex(lx.TOKEN_LPAREN_ID) + "\\\\left(" + self.right.latex(lx.TOKEN_LPAREN_ID) + "\\\\right)"
                if self.op_type == EXPR_PRE:
                    return "\\\\right("+self.right.latex(lx.TOKEN_LPAREN_ID) + "\\\\right)"
                raise Exception("A left parenthesis needs to either be a binary of prefix operator")
            
            case lx.TOKEN_COMMA_ID: # This is very easy, but the main problem is the parentheses that circle around something
                if previous != lx.TOKEN_COMMA_ID and previous != lx.TOKEN_LPAREN_ID: 
                                                        # That is, we are the first comma called (hierarichally) E.g.:
                                                        # Input:            1,2,3,4
                                                        # Parse:            (1,(2,(3,4)))
                                                        #                     ^
                                                        # The ^ is the one we are, if this if passes. In this case, we need to add parentheses, but 
                                                        # only if the above isn't a parenthesis either...
                    return "(" + self.left.latex(lx.TOKEN_COMMA_ID) + "," + self.right.latex(lx.TOKEN_COMMA_ID) + ")"

                return self.left.latex(lx.TOKEN_COMMA_ID) + "," + self.right.latex(lx.TOKEN_COMMA_ID)

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
            case lx.TOKEN_DSM_FUNC_ID:
                return self.token.latex()

                # --- Desmoscript keywords
            case lx.TOKEN_RAW_ID:
                return self.token.latex()

            case lx.TOKEN_DOLLAR_ID:
                return "$" +self.right.latex()

            case _:
                raise Exception(f"Attempted latexification on unknown id: {self.token.id}")


class ExprList:
    def __init__(self, token: lx.Token):
        self.token = token
        self.data: List[Expr] = []




def nud_num(token, token_list):
    return Expr(token)

def nud_var(token, token_list):
    return Expr(token)

def nud_dsm_func(token: lx.Token, token_list):
    """Function for desmos default keywords, like cos, int or prod
    """
    match token.id:
        case lx.TOKEN_DSM_FUNC_ID:
            # Those are functions of some arguments, and act as function calls, meaning the led_lparen will handle everything for us
            return Expr(token)
        case _:
            return Expr(lx.TOKEN_INVALID_ID)

def nud_dsmsp_kw(token, token_list):
    """Function for desmoscript default keywords, like raw
    """
    match token.id:
        case lx.TOKEN_RAW_ID:
            # Those are "environment delimiters", meaning that after them should come a pair of {} in which a special environment will be defined. These keywords act as prefix operators
            return [Expr(token), parse_line(token_list, 0)]


    return Expr(lx.TOKEN_INVALID_ID)

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
    to_return = parse_line(token_list, rbp_table[token.id]) 
    return to_return
    # to_return = parse(token_list, lx.TOKEN_RPAREN_ID)
    # if token_list.peek().id == lx.TOKEN_RPAREN_ID:
    #     token_list.advance()
    # return to_return

def nud_lcur(token, token_list: lx.TokenList): 
    block: list[Expr] = []

    block = parse(token_list, lx.TOKEN_RCUR_ID)
    if(token_list.peek().id != lx.TOKEN_RCUR_ID):
        raise Exception("Right curly wasn't matched")
    token_list.advance()
    return block

def nud_dollar(token, token_list):
    to_return = Expr(token, EXPR_PRE)
    to_return.right = parse_line(token_list, rbp_table[token.id])
    return to_return

nud_lbra = nud_lparen # Same mechanics as for the left parenthesis

def nud_comma(token, token_list: lx.TokenList): # This happens in say, following situation: $(1,,3)
    # to_return = Expr(token, EXPR_BIN)
    # to_return.left = Expr(lx.TOKEN_PLACEHOLDER, EXPR_ATOM)
    # to_return.right = parse_line(token_list, rbp_table[lx.TOKEN_COMMA_ID])
    to_return = Expr(lx.TOKEN_PLACEHOLDER)
    token_list.current_index-=1 # This is weird, ik, but it does work
    return to_return

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

def led_atom(left, token, token_list: lx.TokenList):
    # An atom (num or variable) is not meant to be used as an operator. However, if that's the case, we insert a multiplication before and treat it as such
    to_return = Expr(lx.TOKEN_MULT, EXPR_BIN)
    to_return.left = left
    token_list.current_index-=1
    to_return.right = parse_line(token_list, rbp_table[lx.TOKEN_MULT_ID])
    return to_return

def led_comma(left, token, token_list: lx.TokenList): 
    to_return = Expr(token, EXPR_BIN)
    to_return.left = left
    if nud_table[token_list.peek().id] == nud_none: # Arrives in situations like $(1,2,) where a std parse asks for a nud for )
        to_return.right = Expr(lx.TOKEN_PLACEHOLDER)
    else:
        to_return.right = parse_line(token_list, rbp_table[token.id])
    return to_return

def led_rparen(left, token, token_list):
    # The right parenthesis should return whatever the expression was before, that is, the left, and get itself out of the way
    return left

led_rbra = led_rparen 

def led_none(left, token, token_list):
    raise Exception(f"Tried generating a led for a token which doesn't have one. Token id: {token.id}")


lbp_table = {
             lx.TOKEN_INVALID_ID: None,
             lx.TOKEN_NUM_ID: 30, #None, # We put the same lbp as multiplication in order to consider stuff like a 2 b as  a*2*b
             lx.TOKEN_VARIABLE_ID: 30, # None,
             lx.TOKEN_DOLLAR_ID: None, # the dollar sign acts as a prefix operator
             lx.TOKEN_PLUS_ID: 20,
             lx.TOKEN_MINUS_ID: 20,
             lx.TOKEN_MULT_ID: 30,
             lx.TOKEN_DIV_ID: 30,
             lx.TOKEN_EXP_ID: 41,
             lx.TOKEN_EQUAL_ID: 10,
             lx.TOKEN_END_ID: 0,
             lx.TOKEN_EOF_ID: 0,
             lx.TOKEN_LPAREN_ID: 100,
             lx.TOKEN_RPAREN_ID: 5, # We want to return as soon as we see this
             lx.TOKEN_LCUR_ID: None,
             lx.TOKEN_RCUR_ID: 0,
             lx.TOKEN_LBRA_ID: None,
             lx.TOKEN_RBRA_ID: None,
             lx.TOKEN_COMMA_ID: 15, # Higher than =, but lower than +
             lx.TOKEN_DOT_ID: None, #as of now

             # --- Desmos keywords
             lx.TOKEN_DSM_FUNC_ID: None,
             
             # --- Desmoscript keywords
             lx.TOKEN_RAW_ID: None,
             }

rbp_table = {
             lx.TOKEN_INVALID_ID: None,
             lx.TOKEN_NUM_ID: 31, # None,
             lx.TOKEN_VARIABLE_ID: 31, # None,
             lx.TOKEN_DOLLAR_ID: 0, # We want everything except for an end/eof to kill it
             lx.TOKEN_PLUS_ID: 21,
             lx.TOKEN_MINUS_ID: 21,
             lx.TOKEN_MULT_ID: 31,
             lx.TOKEN_DIV_ID: 31,
             lx.TOKEN_EXP_ID: 40,
             lx.TOKEN_EQUAL_ID: 3,
             lx.TOKEN_END_ID: 0,
             lx.TOKEN_EOF_ID: 0,
             lx.TOKEN_LPAREN_ID: 6, # We want this to sniff out a right parenthesis, but not a newline
             lx.TOKEN_RPAREN_ID: None,
             lx.TOKEN_LCUR_ID: None,
             lx.TOKEN_RCUR_ID: None,
             lx.TOKEN_LBRA_ID: None, 
             lx.TOKEN_RBRA_ID: None,
             lx.TOKEN_COMMA_ID: 14,
             lx.TOKEN_DOT_ID: None, #  as of now

             # --- Desmos keywords
             lx.TOKEN_DSM_FUNC_ID: None,
             
             # --- Desmoscript keywords
             lx.TOKEN_RAW_ID: None,
             }

nud_table = {
             lx.TOKEN_INVALID_ID: nud_none,
             lx.TOKEN_NUM_ID: nud_num,
             lx.TOKEN_VARIABLE_ID: nud_var,
             lx.TOKEN_DOLLAR_ID: nud_dollar,
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
             lx.TOKEN_COMMA_ID: nud_comma,
             lx.TOKEN_DOT_ID: nud_none,

             # --- Desmos keywords
             lx.TOKEN_DSM_FUNC_ID: nud_dsm_func,
             
             # --- Desmoscript keywords
             lx.TOKEN_RAW_ID: nud_dsmsp_kw,
             }

led_table = {
             lx.TOKEN_INVALID_ID: led_none,
             lx.TOKEN_NUM_ID: led_atom,
             lx.TOKEN_VARIABLE_ID: led_atom,
             lx.TOKEN_DOLLAR_ID: led_none,
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
             lx.TOKEN_RCUR_ID: led_none,
             lx.TOKEN_LBRA_ID: led_bin_op,
             lx.TOKEN_RBRA_ID: led_rbra,
             lx.TOKEN_COMMA_ID: led_comma,
             lx.TOKEN_DOT_ID: led_none,

             # --- Desmos keywords
             lx.TOKEN_DSM_FUNC_ID: led_none,
             
             # --- Desmoscript keywords
             lx.TOKEN_RAW_ID: led_none,
             }


def parse_line(token_list: lx.TokenList, min_bp) -> Expr:
    token: lx.Token = token_list.advance()

    if token == lx.TOKEN_INVALID:
        raise Exception("Token was invalid, in nud parsing")

    left = nud_table[token.id](token, token_list)
    while lbp_table[token_list.peek().id] > min_bp:

        token: lx.Token = token_list.advance()

        if token == lx.TOKEN_INVALID:
            raise Exception("Token was invalid, in led parsing")

        left = led_table[token.id](left, token, token_list)

    return left

def parse(token_list: lx.TokenList, custom_end_token_id = lx.TOKEN_EOF_ID) -> list[Expr]:
    result: list[Expr] = []

    while token_list.peek().id == lx.TOKEN_END_ID:
        token_list.advance() # We skip the newlines at the start (do block in C)

    while token_list.peek().id not in {custom_end_token_id, lx.TOKEN_EOF_ID}:


        parse_result = parse_line(token_list, 4) 
        print("intermediary parse result: ", parse_result)

        if not(parse_result is None):
            result.append(parse_result)

        while token_list.peek().id == lx.TOKEN_END_ID:
            token_list.advance() # We skip the newlines

    return result

def print_parse(expr_list: list[Expr]):
    print("Printing parse result: ")
    for expr in expr_list:
        print(f"{expr}")

def latexify_parse(expr_list: list[Expr]):
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
    # toparse = "a^(b+c)+d/cos(2*a)\n\n a+b"
    toparse = """
    raw {{2+3=5}
    cos(2*3) + cosh = 6^x
    4*x + ((56*g)/4)
    }
    a + b = 3
    raw cos(3*a) = 0
    raw { wait (2)=0}
    """
    # toparse = "{2+2}"
    # toparse = "2+((56*g)/4)"
    
    token_list = lx.tokenize_str(toparse)
    print(toparse)
    token_list.print()

    # print(token_list.advance())
    # parsed = parse_lines(token_list, -20)
    # print_parse(parsed)

    # parsed = parse(token_list)
    # print(parsed)
    # print_parse(parsed)
    parsed = parse(token_list)
    print("Result: ", parsed)
    print_parse(parsed)
    
    # parsed = parse(token_list)
    # print_parse(parsed)
    # print(latexify_parse(parsed))
    # print_parse(parsed)  

