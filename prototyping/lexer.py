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
        else:
            ret = id_to_str[self.id]
        return ret
    
    def latex(self) -> str:
        if self.id == TOKEN_NUM_ID:
            return str(self.data)
        elif self.id == TOKEN_VARIABLE_ID:
            datastr = str(self.data)
            if len(datastr) == 1:
                return datastr
            return datastr[0] + "_{" + datastr[1:] +"}" # We subscript the rest of it
        elif self.id == TOKEN_COS_ID:
            return id_to_str[self.id]
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

# --- Desmos keywords
TOKEN_COS_ID = 50 # Leaving some space

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

             # --- Desmos keywords
             TOKEN_COS_ID: "\\cos",

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
TOKEN_EOF = Token(TOKEN_EOF_ID)


# --- Desmos keywords
TOKEN_COS = Token(TOKEN_COS_ID)

# --- Desmoscript keywords
TOKEN_RAW = Token(TOKEN_RAW_ID)

variables = {}
keywords = {
        "cos": TOKEN_COS,
        "raw": TOKEN_RAW
        }

def make_token_from_string(num_or_var:str):
    token = Token(TOKEN_INVALID_ID)

    if num_or_var[0].isalpha():
        if num_or_var in keywords:
            token = keywords[num_or_var]
        elif num_or_var in variables:
            token.id = TOKEN_VARIABLE_ID
            token = variables[num_or_var]
        else:
            token.id = TOKEN_VARIABLE_ID
            token.data = num_or_var
            variables[num_or_var] = token
    elif num_or_var.isdigit():
        token.id = TOKEN_NUM_ID
        token.data = eval(num_or_var)

    if token.id == TOKEN_INVALID_ID:
        print(f"Warning: invalid token generated: {num_or_var}")
    return token


def tokenize_str(content) -> TokenList:
    result = TokenList()
    start_index = 0 # Start index for the current word that's being read
    # current_index = 0 # Start index for the current word that's being read
    comment = 0 # Whether we're reading comments
    content = content + '\n' # We add a newline character to get an end token no matter what
    for current_index in range(len(content)):
        char = content[current_index]
        if char in " ()+-*^/=\n{}[]" and not comment: 
            if current_index > start_index:
                token = make_token_from_string(content[start_index: current_index])
                result.append(token)
                start_index = current_index+1

            match char:
                case " ":
                    start_index = current_index + 1
                case "(":
                    result.append(TOKEN_LPAREN)
                    start_index = current_index + 1
                case ")":
                    result.append(TOKEN_RPAREN)
                    start_index = current_index + 1
                case "{":
                    result.append(TOKEN_LCUR)
                    start_index = current_index + 1
                case "}":
                    result.append(TOKEN_RCUR)
                    start_index = current_index + 1
                case "[":
                    result.append(TOKEN_LBRA)
                    start_index = current_index + 1
                case "]":
                    result.append(TOKEN_RBRA)
                    start_index = current_index + 1
                case "+":
                    result.append(TOKEN_PLUS)
                    start_index = current_index + 1
                case "-":
                    result.append(TOKEN_MINUS)
                    start_index = current_index + 1
                case "*":
                    result.append(TOKEN_MULT)
                    start_index = current_index + 1
                case "^":
                    result.append(TOKEN_EXP)
                    start_index = current_index + 1
                case "=":
                    result.append(TOKEN_EQUAL)
                    start_index = current_index + 1
                case "/":
                    if content[current_index+1] == "/":
                        comment = 1
                        continue
                    result.append(TOKEN_DIV)
                    start_index = current_index + 1
        if char == "\n":
            comment = 0
            start_index = current_index +1
            result.append(TOKEN_END)
    result.append(TOKEN_EOF)
    return result

if __name__ == "__main__":
    # test = "a+b*c^e(/2 btw2 34 e//as \n does this work ? 456*e=4 56e//5"
    test = "ab + ba + 1"
    print(test)
    tokenize_str(test).print()
