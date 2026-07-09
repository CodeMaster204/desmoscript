"""This file transforms the parse tree from parser.py, and spits out an ast for later analysis.

Say the parser spits out
((f <of> (x <,> y)) = ((2 + y) * (x-a)))
(a = 2)
(f <of> (2,3))
Then the ast would look like
definition:
    f: function -||
                 ||- x: local parameter
                 ||- y: local parameter
        -> ((2+y)*(x-a))

definition:
    a: number 
        -> 2

functioncall(f, (2,3))

And so for instance, type inference would become

typeof(f)   = (typeof(2+y) * typeof(x-a))
            = ((typeof(2) + typeof(y)) * (typeof(x)-typeof(a)))
            = ((number + typeof(y)) * (typeof(x) - number)) # notice we get typeof(a) = number from the ast
This typeof then, is a function taking function parameter types, and spitting out a type.

Then, for the functioncall, we get (evaluate the type function, with parameters)
typeof(functioncall(f,(2,3)))   = ((number + typeof(3)) * (typeof(2) - number))
                                = ((number + number) * (number- number))
                                = (number * number)
                                = number

Then, we know we need to write definitions down in latex, so we do that for both f and a, and
then writing functioncalls becomes easy
"""

import parser as prs
import lexer as lx
TYPE_NONE = 0
TYPE_NUM = 1 # Just anything that resolves to a number
TYPE_POINT = 2 # same for points
TYPE_POINT3D = 3 # same for points(3D)
TYPE_POLYGON = 4 # and same for polygons
TYPE_COLOR = 5 # For stuff like rgb(100,100,100)

def type_add(tp1: int, tp2: int):
    """returns the result of adding two types
    Only possibilities here are:
    num + num -> num
    point + point -> point
    point3d + point3d -> point3d

    Args:
        tp1 (TYPE_... enum): Type of the first argument
        tp2 (TYPE_... enum): Type of the second argument
    """
    if tp1 == TYPE_NUM and tp2 == TYPE_NUM:
        return TYPE_NUM

    if tp1 == TYPE_POINT and tp2 == TYPE_POINT:
        return TYPE_POINT

    if tp1 == TYPE_POINT3D and tp2 == TYPE_POINT3D:
        return TYPE_POINT3D

    raise Exception(f"Types of {tp1} and {tp2} cannot be added together. Description for what these should correspond to is in the start of ast.py")

def type_sub(tp1: int, tp2: int):
    """returns the result of substracting two types
    Only possibilities here are:
    num - num -> num
    point - point -> point
    point3d - point3d -> point3d

    Args:
        tp1 (TYPE_... enum): Type of the first argument
        tp2 (TYPE_... enum): Type of the second argument
    """
    if tp1 == TYPE_NUM and tp2 == TYPE_NUM:
        return TYPE_NUM

    if tp1 == TYPE_POINT and tp2 == TYPE_POINT:
        return TYPE_POINT

    if tp1 == TYPE_POINT3D and tp2 == TYPE_POINT3D:
        return TYPE_POINT3D

    raise Exception(f"Types of {tp1} and {tp2} cannot be substracted together. Description for what these should correspond to is in the start of ast.py")

def type_mult(tp1: int, tp2: int):
    """returns the result of multiplying two types
    Only possibilities here are:
    
    num    *
            num     -> num
            point   -> point
            point3d   -> point3d

    point  *
            num     -> point
            point   -> num  # Dot product TODO: Check that it does work for real

    point3d  *
            num     -> point3d
            point3d   -> num  # Dot product TODO: Check that it does work for real

    Args:
        tp1 (TYPE_... enum): Type of the first argument
        tp2 (TYPE_... enum): Type of the second argument
    """
    if tp1 == TYPE_NUM:
        if tp2 == TYPE_NUM:
            return TYPE_NUM
        if tp2 == TYPE_POINT:
            return TYPE_POINT
        if tp2 == TYPE_POINT3D:
            return TYPE_POINT3D
    if tp1 == TYPE_POINT:
        if tp2 == TYPE_NUM:
            return TYPE_POINT
        if tp2 == TYPE_POINT: # Dot product
            return TYPE_NUM
    if tp1 == TYPE_POINT3D:
        if tp2 == TYPE_NUM:
            return TYPE_POINT3D
        if tp2 == TYPE_POINT3D: # Dot product
            return TYPE_NUM

    raise Exception(f"Types of {tp1} and {tp2} cannot be multiplied together. Description for what these should correspond to is in the start of ast.py")

def type_div(tp1: int, tp2: int): # WARN: Order matters
    """returns the result of dividing two types, WARN: here ORDER MATTERS
    Only possibilities here are:
    
    num    /
            num     -> num

    point  /
            num     -> point
    point3d  /
            num     -> point3d

    Args:
        tp1 (TYPE_... enum): Type of the first argument
        tp2 (TYPE_... enum): Type of the second argument
    """
    if tp1 == TYPE_NUM and tp2 == TYPE_NUM:
        return TYPE_NUM
    if tp1 == TYPE_POINT and tp2 == TYPE_NUM:
        return TYPE_POINT
    if tp1 == TYPE_POINT3D and tp2 == TYPE_NUM:
        return TYPE_POINT3D

    raise Exception(f"Types of {tp1} and {tp2} cannot be divided in this respective order. Description for what these should correspond to is in the start of ast.py")

def type_exp(tp1: int, tp2: int): # WARN: Order matters
    """returns the result of exponentiating two types, WARN: here ORDER MATTERS
    Only possibilities here are:
    
    num    ^
            num     -> num

    Args:
        tp1 (TYPE_... enum): Type of the first argument
        tp2 (TYPE_... enum): Type of the second argument
    """
    if tp1 == TYPE_NUM and tp2 == TYPE_NUM:
        return TYPE_NUM

    raise Exception(f"Types of {tp1} and {tp2} cannot perform an exponentiation in this respective order. Description for what these should correspond to is in the start of ast.py")

class ASTNode:
    TypeNone:int = 0
    VarAssign:int = 1
    FuncDef:int = 2
    Instance:int = 3 # instance of anything, so just no assignment
    DollarExpr:int = 4
    def __init__(self, expr: prs.Expr, global_context, instancetype: int = TYPE_NONE):
        """Creates an AST node from an expression. Used by the AST class

        Args:
            expr: the expression to ast-ize. It has to be a single desmos equation though, so no context like <raw>
            global_context: A dictionary going from strings (the variables' names) to ASTNodes (their assignment)
        """
        # We need to check for:
        #                   assignments (function definitions among others)
        #                   instances
        #TODO:              comparisons (special case of instances)

        self.nodetype: int = ASTNode.TypeNone
        self.expr: prs.Expr = prs.Expr(lx.TOKEN_INVALID)
        self.global_context: dict[lx.Token, ASTNode] = global_context # Dict for the global scope
        self.local_context: list[lx.Token] = [] # This is a list of the local scope (say we have a function with parameters),
                                                    # which lists all of the parameters, without defining them. That will indeed
                                                    # be the job of the function call, which will make a full dictionary and ast nodes for each
                                                    # variable when it calls
        self.instancetype: int = instancetype # Can be updated once every context has been fully determined (desmos is functional, so stuff can happen later in code), OR at start, if it's an expression whose type is known

        self.dollar_list: list[prs.Expr] = [] # A list of dollar expressions parameters, if applicable

        # For assigments, the highest node *will* be an equal token:
        if expr.token.id == lx.TOKEN_EQUAL_ID:

            # For variables, we will have a single variable token on the left of the equal sign
            # For functions, we will have a <of> (evaluation token on the left)
            if expr.left.token.id == lx.TOKEN_VARIABLE_ID: # variable
                self.nodetype = ASTNode.VarAssign
                self.expr = expr
                self.global_context[expr.left.token] = self

            if expr.left.token.id == lx.TOKEN_LPAREN_ID: # Function definition
                self.nodetype = ASTNode.FuncDef
                self.expr = expr
                # Add the function name to the global context:
                if expr.left.left.token.id != lx.TOKEN_VARIABLE_ID: # This is erroneous syntax
                    raise Exception(f"Wrote a function definition, where the function wasn't a variable: {expr}")
                self.global_context[expr.left.left.token] = self

                # Fetch parameters:
                parameters = get_list_of_params_from_lparen(expr.left)
                if len(parameters) == 0:
                    raise Exception(f"A function definition needs variables")
                self.local_context = [param.token for param in parameters] # We transform this into a list of tokens as wished
                # Check that parameters are variables
                for param in self.local_context:
                    if param.id != lx.TOKEN_VARIABLE_ID: # This is not acceptable in this case
                        raise Exception(f"There is a parameter that isn't a variable {param} in {expr}")

        elif expr.token.id == lx.TOKEN_DOLLAR_ID:
            self.nodetype = ASTNode.DollarExpr
            self.dollar_list = get_list_of_params_from_lparen(expr)
            print("aseas", self.dollar_list)

        else:
            self.nodetype = ASTNode.Instance
            self.expr = expr
    def __str__(self):
        return self.expr.__repr__()

    def getType(self):
        # If it's already been decided, no need to do it again
        if self.instancetype != TYPE_NONE:
            return self.instancetype
        # if not, well here we go:
        match self.nodetype:
            case ASTNode.FuncDef: # Function definitions have no instance type
                return TYPE_NONE
            case ASTNode.Instance:
                self.instancetype = getExprType(self.expr, self.global_context)
                return self.instancetype
            case ASTNode.VarAssign:
                self.instancetype = getExprType(self.expr.right, self.global_context)
                return self.instancetype

def get_list_of_params_from_lparen(expr: prs.Expr)->list[prs.Expr]:
    """Returns a list of expressions, unpacked out of the comma bs

    Args:
        expr: the expression (the first element above and left of the first comma if existing. Essentially the function of an lparen)
    """
    to_return: list[prs.Expr] = []
    # First, if there's only one variable:
    if expr.right.token.id != lx.TOKEN_COMMA_ID:
        to_return.append(expr.right)
        return to_return
    #Now, if there's multiple variables, there's at least *one* comma:
    current_comma = expr.right
    while current_comma.right.token.id == lx.TOKEN_COMMA_ID: # As long as parameters remain
        to_return.append(current_comma.left)
        current_comma = current_comma.right

    # We have to run it again here, since the last comma won't have a comma to its right. In this case though,
    # we not only need to add the left parameter, but also the right one
    to_return.append(current_comma.left)
    to_return.append(current_comma.right)
    
    return to_return

def getExprType(expr: prs.Expr, context: dict[lx.Token, ASTNode] = {})->int:
    """Gives the type of an expression (of the instance type)

    Args:
        expr: An expression (without = signs) for us to compute the type of
        context: the current context we work with (global with local extensions)

    Returns:
        The type of the expression
    """
    match expr.token.id:

        case lx.TOKEN_NUM_ID:
            return TYPE_NUM
        case lx.TOKEN_PLUS_ID: # All main standard binary operators
            return type_add(getExprType(expr.left, context), getExprType(expr.right, context))
        case lx.TOKEN_MINUS_ID: # All main standard binary operators
            return type_sub(getExprType(expr.left, context), getExprType(expr.right, context))
        case lx.TOKEN_MULT_ID: # All main standard binary operators
            return type_mult(getExprType(expr.left, context), getExprType(expr.right, context))
        case lx.TOKEN_DIV_ID: # All main standard binary operators
            return type_div(getExprType(expr.left, context), getExprType(expr.right, context))
        case lx.TOKEN_EXP_ID: # All main standard binary operators
            return type_exp(getExprType(expr.left, context), getExprType(expr.right, context))

        case lx.TOKEN_VARIABLE_ID:
            # We need to check in the context for its type, which just means polling it
            if not expr.token in context:
                raise Exception(f"Unresolved dependency: {expr}, context: {context}")
            ast_node = context[expr.token]
            return ast_node.getType()

        case lx.TOKEN_COMMA_ID:
            # We have the 2D and 3D case:
            param1_type = getExprType(expr.left, context)
            param2_type = getExprType(expr.right, context)
            # Now since points are right associative, we'll have either something like:
            # (1 <,> 3)
            # or something like
            # (1 <,> (4 <,> 5))
            #in which case param2_type == TYPE_POINT2D, so we get TYPE_POINT2D
            if param1_type != TYPE_NUM:
                raise Exception(f"Points must have numbers as coordinates: {expr}")
            if param2_type == TYPE_NUM: # We have a 2D point
                return TYPE_POINT
            elif param2_type == TYPE_POINT:
                return TYPE_POINT3D
            raise Exception(f"Points must have numbers as coordinates: {expr}")




        case lx.TOKEN_LPAREN_ID: # Function evaluation
            # Either it is a standard function (polygon), or a custom one. Either way, we need to look at the parameters
            params = get_list_of_params_from_lparen(expr)
            if len(params) == 0:
                raise Exception(f"A function call needs arguments:{expr}, context: {context}")
            # We first poll the type of each parameter, then evaluate the type of the function definition with an extended context
            types = [getExprType(param, context) for param in params]
            
            match expr.left.token.id: # We check which function it is:
                case lx.TOKEN_COS_ID: # Takes *one* num, and returns a num
                    if types[0] != TYPE_NUM:
                        raise Exception("Cos only takes one argument, and it has to be a number")
                    return TYPE_NUM
                case lx.TOKEN_POLYGON_ID:
                    # TODO check stuff
                    return TYPE_POLYGON
                case lx.TOKEN_RGB_ID:
                    if len(params) != 3:
                        raise Exception(f"Expected 3 arguments for the rbg function, got {len(params)}: {params}")
                    if types[0] != TYPE_NUM or types[1] != TYPE_NUM or types[2] != TYPE_NUM:
                        raise Exception("Expected numbers for arguments in rgb function")
                    return TYPE_COLOR

                case _: # An arbitrary function call from a nice function (doesn't do type magic), typically custom-defined
                    if not expr.left.token in context: # Unresolved dependency
                        raise Exception(f"Unresolved dependency: {expr.left}, context: {context}")
                    f_node = context[expr.left.token] # We get the function's node
                    # paramnodes = [ASTNode(prs.Expr(lx.), {}, type_) for type_ in types] # Create ASTnodes for the argument calls
                    extended_context = context.copy()
                    for i in range(len(f_node.local_context)): # Iterating through the arguments
                        ast_node = ASTNode(prs.Expr(f_node.local_context[i]), {}, types[i]) # Create ASTnodes for the argument calls
                        extended_context[f_node.local_context[i]] = ast_node
                    # And then, we just evaluate that expressions, with this context:
                    return getExprType(f_node.expr.right, extended_context) # We call the right, to hop over the equal sign

    return TYPE_NONE


class AST():
    def __init__(self, exprs: list[prs.Expr]):
        """Generates an AST from a list of desmos expressions, being the (slightly modified) result of a parse (extract the raw expressions)
        To use it, first unpack all the expressions to get a list of pure expressions
        Args:
            exprs: a list of expressions
        """
        self.context: dict[lx.Token, ASTNode] = {
                lx.TOKEN_X_VAR: ASTNode(prs.Expr(lx.TOKEN_X_VAR), {}, TYPE_NUM),
                lx.TOKEN_Y_VAR: ASTNode(prs.Expr(lx.TOKEN_Y_VAR), {}, TYPE_NUM),
                }
        # We start out by adding defaults like x,y, (maybe t, r and theta?), if they exist
        self.ast: list[ASTNode] = [ASTNode(expr, self.context) for expr in exprs]
        # The context oughta be done now

    def getExprTypeFromGlobalContext(self, expr: prs.Expr):
        return getExprType(expr, self.context)

