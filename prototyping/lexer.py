"""

This file implements the lexer part of desmoscript's prototype
"""

from typing import List


class Token:
    def __init__(self, token_id, data = None):
        """Inits a new token

        Args:
            token_id (a TOKEN_* enum): Which token this corresponds to
            data : Token-dependent data: For a variable: a string, for a number, its value
        """
        self.id = token_id
        self.data = data

    def __repr__(self):
        ret = ""
        if self.id == TOKEN_NUM_ID or self.id == TOKEN_VARIABLE_ID:
            ret = str(self.data)
        elif self.id == TOKEN_DSM_FUNC_ID:
            ret = dsm_kw_id_to_str[self.data]
        else:
            ret = id_to_str[self.id]
        return ret
    
    def latex(self) -> str:
        if self.id == TOKEN_NUM_ID:
            return str(self.data)
        elif self.id == TOKEN_VARIABLE_ID:
            datastr = str(self.data)
            # if len(datastr) == 1:
            return datastr
            # return datastr[0] + "_{" + datastr[1:] +"}" # We subscript the rest of it
        elif self.id == TOKEN_DSM_FUNC_ID:
            return dsm_kw_id_to_str[self.data]
        else:
            raise Exception(f"The Token.latex() function is only defined on numbers and variables and keyword functions, not on {self}")

class TokenList:
    def __init__(self):
        self.list: List[Token] = []
        self.current_index = -1
        self.count = 0

    def advance(self) -> Token: 
        if self.current_index<self.count-1:
            self.current_index +=1
            return self.list[self.current_index]
        return TOKEN_INVALID

    def peek(self) -> Token:
        if self.current_index<self.count-1:
            return self.list[self.current_index+1]
        return TOKEN_INVALID

    def append(self, token):
        self.list.append(token)
        self.count+=1

    def isFull(self):
        return self.count == self.current_index + 1
    
    def print(self):
        print([token for token in self.list])


# These are the token enums
TOKEN_INVALID_ID = -1
TOKEN_NUM_ID = 0
TOKEN_VARIABLE_ID = 1
TOKEN_PLUS_ID = 2
TOKEN_MINUS_ID = 3
TOKEN_MULT_ID = 4
TOKEN_DIV_ID = 5
TOKEN_EXP_ID = 6
TOKEN_LPAREN_ID = 7
TOKEN_RPAREN_ID = 8
TOKEN_END_ID = 9
TOKEN_EQUAL_ID = 10
TOKEN_LCUR_ID = 11
TOKEN_RCUR_ID = 12
TOKEN_LBRA_ID = 13
TOKEN_RBRA_ID = 14
TOKEN_EOF_ID = 15
TOKEN_COMMA_ID = 16
TOKEN_DOT_ID = 17
TOKEN_DOLLAR_ID = 18
TOKEN_PLACEHOLDER_ID = 19 # Used for putting a placeholder for an empty spot in expressions like $(,,2)

# --- Desmos keywords
TOKEN_DSM_FUNC_ID = 50 # Desmos functions

# TOKEN_COS_ID = 50 # Leaving some space
#
# TOKEN_POLYGON_ID = 75 # Leaving some space
# TOKEN_RGB_ID = 76

# Desmoscript keywords
TOKEN_RAW_ID = 100

# TODO: Keywords
# sin tan acos asin atan sinh cosh tanh atanh acosh asinh
# sum prod int ddx() ncr mod
# raw if while for func routine import <list comprehension>
bin_operators = [TOKEN_PLUS_ID, TOKEN_MINUS_ID, TOKEN_MULT_ID, TOKEN_DIV_ID, TOKEN_EXP_ID, TOKEN_EQUAL_ID]
id_to_str = {TOKEN_INVALID_ID: "invalid",
             TOKEN_NUM_ID: "",
             TOKEN_VARIABLE_ID: "",
             TOKEN_PLUS_ID: "+",
             TOKEN_MINUS_ID: "-",
             TOKEN_MULT_ID: "*",
             TOKEN_DIV_ID: "/",
             TOKEN_EXP_ID: "^",
             TOKEN_LPAREN_ID: "<of>",
             TOKEN_RPAREN_ID: ")",
             TOKEN_END_ID: "\n",
             TOKEN_EOF_ID: "<EOF>",
             TOKEN_EQUAL_ID: "=",
             TOKEN_LCUR_ID: "{",
             TOKEN_RCUR_ID: "}",
             TOKEN_LBRA_ID: "[",
             TOKEN_RBRA_ID: "]",
             TOKEN_COMMA_ID: "<,>",
             TOKEN_DOT_ID: "<.>",
             TOKEN_DOLLAR_ID: "$",
             TOKEN_PLACEHOLDER_ID: "<placeholder>",

             # --- Desmos keywords
             # TOKEN_COS_ID: "\\\\cos",
             # TOKEN_POLYGON_ID: "\\\\operatorname{polygon}",
             # TOKEN_RGB_ID: "\\\\operatorname{rgb}",

             # --- Desmoscript keywords
             TOKEN_RAW_ID: "<raw>",
             }

TOKEN_INVALID = Token(TOKEN_INVALID_ID)
TOKEN_PLUS = Token(TOKEN_PLUS_ID)
TOKEN_MINUS = Token(TOKEN_MINUS_ID)
TOKEN_MULT = Token(TOKEN_MULT_ID)
TOKEN_DIV = Token(TOKEN_DIV_ID)
TOKEN_EXP = Token(TOKEN_EXP_ID)
TOKEN_LPAREN = Token(TOKEN_LPAREN_ID)
TOKEN_RPAREN = Token(TOKEN_RPAREN_ID)
TOKEN_END = Token(TOKEN_END_ID)
TOKEN_EQUAL = Token(TOKEN_EQUAL_ID)
TOKEN_LCUR = Token(TOKEN_LCUR_ID)
TOKEN_RCUR = Token(TOKEN_RCUR_ID)
TOKEN_LBRA = Token(TOKEN_LBRA_ID)
TOKEN_RBRA = Token(TOKEN_RBRA_ID)
TOKEN_COMMA = Token(TOKEN_COMMA_ID)
TOKEN_DOT = Token(TOKEN_DOT_ID)
TOKEN_DOLLAR = Token(TOKEN_DOLLAR_ID)
TOKEN_PLACEHOLDER = Token(TOKEN_PLACEHOLDER_ID)
TOKEN_EOF = Token(TOKEN_EOF_ID)


# --- Desmos keywords
KW_COS_ID = 0
TOKEN_COS = Token(TOKEN_DSM_FUNC_ID, data = KW_COS_ID)
KW_POLYGON_ID = 1
TOKEN_POLYGON = Token(TOKEN_DSM_FUNC_ID, data = KW_POLYGON_ID)
KW_RGB_ID = 2
TOKEN_RGB = Token(TOKEN_DSM_FUNC_ID, data = KW_RGB_ID)

TOKEN_COL_RED = Token(TOKEN_VARIABLE_ID, data = "\\\\operatorname{rgb}(199, 68, 64)")
TOKEN_COL_BLUE = Token(TOKEN_VARIABLE_ID, data = "\\\\operatorname{rgb}(45, 112, 179)")
TOKEN_COL_GREEN = Token(TOKEN_VARIABLE_ID, data = "\\\\operatorname{rgb}(56, 140, 70)")
TOKEN_COL_ORANGE = Token(TOKEN_VARIABLE_ID, data = "\\\\operatorname{rgb}(250, 126, 25)")
TOKEN_COL_PURPLE = Token(TOKEN_VARIABLE_ID, data = "\\\\operatorname{rgb}(96, 66, 166)")
TOKEN_COL_BLACK = Token(TOKEN_VARIABLE_ID, data = "\\\\operatorname{rgb}(0, 0, 0)")

# Point shape variables, which'll be available only in a local context for the point dollar expression
TOKEN_PTSHAPE_DOT = Token(TOKEN_VARIABLE_ID, data = "d_{ot}")
TOKEN_PTSHAPE_CIRCLE = Token(TOKEN_VARIABLE_ID, data = "c_{ircle}")
TOKEN_PTSHAPE_CROSS = Token(TOKEN_VARIABLE_ID, data = "c_{ross}")
TOKEN_PTSHAPE_SQUARE = Token(TOKEN_VARIABLE_ID, data = "s_{quare}")
TOKEN_PTSHAPE_PLUS = Token(TOKEN_VARIABLE_ID, data = "p_{lus}")
TOKEN_PTSHAPE_TRIANGLE = Token(TOKEN_VARIABLE_ID, data = "t_{riangle}")
TOKEN_PTSHAPE_DIAMOND = Token(TOKEN_VARIABLE_ID, data = "d_{iamond}")
TOKEN_PTSHAPE_STAR = Token(TOKEN_VARIABLE_ID, data = "s_{tar}")

TOKEN_PTDRAG_NO = Token(TOKEN_VARIABLE_ID, data = "n_{o}")
TOKEN_PTDRAG_XY = Token(TOKEN_VARIABLE_ID, data = "x_{y}")
# The horizontal and vertical ones are handled with the normal x and y tokens


TOKEN_LINESTYLE_LINE = Token(TOKEN_VARIABLE_ID, data = "l_{ine}")
TOKEN_LINESTYLE_DASHES = Token(TOKEN_VARIABLE_ID, data = "d_{ashes}")
TOKEN_LINESTYLE_DOTS = Token(TOKEN_VARIABLE_ID, data = "d_{ots}")

# Desmos variables defined by default:
TOKEN_X_VAR = Token(TOKEN_VARIABLE_ID, "x")
TOKEN_Y_VAR = Token(TOKEN_VARIABLE_ID, "y")
# --- Desmoscript keywords
TOKEN_RAW = Token(TOKEN_RAW_ID)

variables = {
        "x": TOKEN_X_VAR,
        "y": TOKEN_Y_VAR,
        "red": TOKEN_COL_RED,
        "blue": TOKEN_COL_BLUE,
        "green": TOKEN_COL_GREEN,
        "orange": TOKEN_COL_ORANGE,
        "purple": TOKEN_COL_PURPLE,
        "black": TOKEN_COL_BLACK,

        "dot": TOKEN_PTSHAPE_DOT,
        "circle": TOKEN_PTSHAPE_CIRCLE,
        "cross": TOKEN_PTSHAPE_CROSS,
        "square": TOKEN_PTSHAPE_SQUARE,
        "plus": TOKEN_PTSHAPE_PLUS,
        "triangle": TOKEN_PTSHAPE_TRIANGLE,
        "diamond": TOKEN_PTSHAPE_DIAMOND,
        "star": TOKEN_PTSHAPE_STAR,

        "no": TOKEN_PTDRAG_NO,
        "xy": TOKEN_PTDRAG_XY,
        "line": TOKEN_LINESTYLE_LINE,
        "dots": TOKEN_LINESTYLE_DOTS,
        "dashes": TOKEN_LINESTYLE_DASHES,
        }
keywords = {
        "raw": TOKEN_RAW,

        "cos": TOKEN_COS,
        "polygon": TOKEN_POLYGON,
        "rgb": TOKEN_RGB,
        }
# lists for easier modulation and modification in the future
default_variable_tokens = [
        TOKEN_X_VAR,
        TOKEN_Y_VAR
        ]
default_color_tokens = [
        TOKEN_COL_RED,
        TOKEN_COL_BLUE,
        TOKEN_COL_GREEN,
        TOKEN_COL_ORANGE,
        TOKEN_COL_PURPLE,
        TOKEN_COL_BLACK,
        ]
default_ptshape_tokens = [
        TOKEN_PTSHAPE_DOT,
        TOKEN_PTSHAPE_CIRCLE,
        TOKEN_PTSHAPE_CROSS,
        TOKEN_PTSHAPE_SQUARE,
        TOKEN_PTSHAPE_PLUS,
        TOKEN_PTSHAPE_TRIANGLE,
        TOKEN_PTSHAPE_DIAMOND,
        TOKEN_PTSHAPE_STAR,
        ]
ptshape_token_to_latex = {
        TOKEN_PTSHAPE_DOT: "",
        TOKEN_PTSHAPE_CIRCLE: ',"pointStyle": "OPEN"',
        TOKEN_PTSHAPE_CROSS: ',"pointStyle":"CROSS"',
        TOKEN_PTSHAPE_SQUARE: ',"__stashed_V12PointStyle": "SQUARE"',
        TOKEN_PTSHAPE_PLUS: ',"__stashed_V12PointStyle": "PLUS"',
        TOKEN_PTSHAPE_TRIANGLE: ',"__stashed_V12PointStyle": "TRIANGLE"',
        TOKEN_PTSHAPE_DIAMOND: ',"__stashed_V12PointStyle": "DIAMOND"',
        TOKEN_PTSHAPE_STAR: ',"__stashed_V12PointStyle": "STAR"',
        }
default_ptdrag_tokens = [
        TOKEN_PTDRAG_NO,
        TOKEN_PTDRAG_XY,
        TOKEN_X_VAR,
        TOKEN_Y_VAR,
        ]
ptdrag_token_to_latex = {
        TOKEN_PTDRAG_NO: ',"dragMode":"NONE"',
        TOKEN_PTDRAG_XY: ',"dragMode":"XY"',
        TOKEN_X_VAR: ',"dragMode":"X"',
        TOKEN_Y_VAR: ',"dragMode":"Y"',
        }
default_linestyle_tokens = [
        TOKEN_LINESTYLE_LINE,
        TOKEN_LINESTYLE_DASHES,
        TOKEN_LINESTYLE_DOTS,
        ]
linestyle_token_to_latex = {
        TOKEN_LINESTYLE_LINE: ',"lines":true',
        TOKEN_LINESTYLE_DASHES: ',"lineStyle": "DASHED"',
        TOKEN_LINESTYLE_DOTS: ',"lineStyle": "DOTTED"',
        }



dsm_kw_id_to_str = {
        KW_COS_ID: "\\\\cos",
        KW_POLYGON_ID: "\\\\operatorname{polygon}",
        KW_RGB_ID: "\\\\operatorname{rgb}",
        }

def make_token_from_string(num_or_var:str):
    
    """This is meant to parse stuff like 234xyz45 and spit out [234, xyz_{45}], and raise an error if the format is wrong. LATER, we will also parse 56hi_th3re into 56*hi_{th3re} and similar stuff
    """
    num_or_var = num_or_var.replace("_","") # These are the same in this language, so just use them for fun, or don"t
    if set(num_or_var) in set("abcdefghijmnopqrstuvwxyz0123456789.") != set():
        print(f"Invalid token generated, tried interpreting <{num_or_var}>")
        return [TOKEN_INVALID]

    number = num_or_var[0] in set("0123456789.") # Whether we have a number in front of the word
    word = 0 # whether we have a word
    subscript = 0 # Whether we have a subscript
    first_letter = 0
    while first_letter < len(num_or_var):
        if(num_or_var[first_letter].isalpha()):
            word = 1
            break
        first_letter += 1

    first_subscript_char = first_letter+1
    # if word:
    #     while first_subscript_char < len(num_or_var):
    #         if(num_or_var[first_subscript_char].isdigit()):
    #             subscript = 1
    #             break;
    #         first_subscript_char += 1
    #
    # if subscript:
    #     compound_word = num_or_var[first_letter: first_subscript_char] +num_or_var[first_subscript_char:]
    # else:
    compound_word = num_or_var[first_letter:]

    if word:
        if compound_word in keywords:
            word_token = keywords[compound_word]
        elif compound_word in variables:
            word_token = variables[compound_word]
        else:
            word_data = compound_word
            if len(compound_word) >1: # We need to split it into desmos standards
                word_data = compound_word[0] + r"_{" + compound_word[1:] + r"}"
            word_token = Token(TOKEN_VARIABLE_ID, data=word_data)
            variables[compound_word] = word_token

        if number:
            number_token = Token(TOKEN_NUM_ID, data = eval(num_or_var[:first_letter]))
            return [number_token, TOKEN_MULT, word_token]
        return [word_token]

    if number:
        number_token = Token(TOKEN_NUM_ID, data = eval(num_or_var[:first_letter]))
        return [number_token]




def tokenize_str(content) -> TokenList:
    result = TokenList()
    start_index = 0 # Start index for the current word that's being read
    # current_index = 0 # Start index for the current word that's being read
    comment = 0 # Whether we're reading comments
    depth = 0 # The current depth (parentheses for now, later {} and [] will be added)
    dollar_depth = 0 # The depth at which we saw the dollar sign
    dollar_mode = 0 # This is set to 0 when seeing a $, set to 2 when seeing a (, set to 3 when meeting the matching ), and reset to 0 after the following end of line/file token
    dollar_buffer = TokenList() # The buffer inside which resides dollar info
    appending_buffer = result # The buffer we are apppending now
    content = content + '\n' # We add a newline character to get an end token no matter what
    for current_index in range(len(content)):
        char = content[current_index]
        if char in " $()+-*^/=\n{}[];#," and not comment: 
            if current_index > start_index:
                token = make_token_from_string(content[start_index: current_index])
                appending_buffer.list += token
                appending_buffer.count+=len(token)
                start_index = current_index+1

            match char:
                case " ":
                    start_index = current_index + 1
                    continue
                case "(":
                    if dollar_mode == 1: # We had a $ previously, so we change the mode, and the appending buffer
                        dollar_mode = 2
                        appending_buffer = dollar_buffer
                        appending_buffer.append(TOKEN_DOLLAR) # We want the buffer to look like $arg1,arg2,arg4; (in tokens) afterwards
                    else:
                        appending_buffer.append(TOKEN_LPAREN)
                    start_index = current_index + 1
                    depth+=1
                    continue
                case ")":
                    start_index = current_index + 1
                    depth-=1
                    if dollar_mode == 2 and dollar_depth == depth: # We are getting out of the $ environment, so we need to
                        dollar_mode = 3 # signal that we went outside of it
                        appending_buffer.append(TOKEN_END) # Append an end of line
                        appending_buffer = result # Change the appending buffer once again
                    else:
                        appending_buffer.append(TOKEN_RPAREN)
                    continue
                case "{":
                    appending_buffer.append(TOKEN_LCUR)
                    start_index = current_index + 1
                    continue
                case "}":
                    appending_buffer.append(TOKEN_RCUR)
                    start_index = current_index + 1
                    continue
                case "[":
                    appending_buffer.append(TOKEN_LBRA)
                    start_index = current_index + 1
                    continue
                case "]":
                    appending_buffer.append(TOKEN_RBRA)
                    start_index = current_index + 1
                    continue
                case "+":
                    appending_buffer.append(TOKEN_PLUS)
                    start_index = current_index + 1
                    continue
                case "-":
                    appending_buffer.append(TOKEN_MINUS)
                    start_index = current_index + 1
                    continue
                case "*":
                    appending_buffer.append(TOKEN_MULT)
                    start_index = current_index + 1
                    continue
                case "^":
                    appending_buffer.append(TOKEN_EXP)
                    start_index = current_index + 1
                    continue
                case "=":
                    appending_buffer.append(TOKEN_EQUAL)
                    start_index = current_index + 1
                    continue
                case "/":
                    appending_buffer.append(TOKEN_DIV)
                    start_index = current_index + 1
                    continue
                case ",":
                    appending_buffer.append(TOKEN_COMMA)
                    start_index = current_index + 1
                    continue
                case "$":
                    # We don't append a token, as it'll be appended later
                    start_index = current_index + 1
                    dollar_mode = 1
                    dollar_depth = depth
                    continue
                case "#":
                    comment = 1
                    start_index = current_index + 1
                    continue
        if char == "\n":
            comment = 0
            start_index = current_index +1
        if char == ";":
            if depth != 0: # Something is unclosed
                raise Exception(f"Some parenthesis pair was either unopened or unclosed")
            result.append(TOKEN_END)
            if dollar_mode == 3: # We had some dollar information in this section
                result.list += dollar_buffer.list
                result.count += dollar_buffer.count
                dollar_buffer = TokenList() # We reset the dollar buffer
            start_index = current_index +1

    if dollar_mode == 3: # We had some dollar information in this section, which got terminated by an eof, and not a ;
        result.list += dollar_buffer.list
        result.count += dollar_buffer.count
        dollar_buffer = TokenList() # We reset the dollar buffer

    result.append(TOKEN_EOF)
    return result

if __name__ == "__main__":
    # test = "a+b*c^e(/2 btw2 34 e//as \n does this work ? 456*e=4 56e//5"
    test = "ab + ba + 1"
    print(test)
    tokenize_str(test).print()
