#!/usr/bin/python
import math
import operator as op


Symbol = str
List = list
Number = (int, float)


class Env(dict):
    """
    An environment: a dict of 'var': val pairs with an outer Env
    """
    def __init__(self, params=(), args=(), outer=None):
        self.update(zip(params, args))
        self.outer = outer

    def find(self, var):
        return self if (var in self) else self.outer.find(var)


class Procedure(object):
    """ A user defined Lisp Procedure """
    def __init__(self, params, body, env):
        self.params, self.body, self.env = params, body, env

    def __call__(self, *args):
        return eval(self.body, Env(self.params, args, self.env))
        


def standard_env():
    # An environment with some Scheme standard procedures
    env = Env()
    env.update(vars(math))
    env.update({
        '+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv, 
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 
        'abs':     abs,
        'append':  op.add,  
        'apply':   lambda proc, args: proc(*args),
        'begin':   lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:], 
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_, 
        'equal?':  op.eq, 
        'length':  len, 
        'list':    lambda *x: list(x), 
        'list?':   lambda x: isinstance(x,list), 
        'map':     lambda *args: list(map(*args)),
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [], 
        'number?': lambda x: isinstance(x, Number),   
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
    })

    return env

global_env = standard_env()

def tokenize(chars):
    # Convert a string into a list of tokens
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()

def parse(program):
    # Read expressions from a string
    return read_tokens(tokenize(program))

def read_tokens(tokens):
    # Read an expression from a sequence of tokens
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF')
    
    token = tokens.pop(0)
    if token == '(':
        L = []
        while tokens[0] != ')':
            L.append(read_tokens(tokens))
        tokens.pop(0) # pop off ')'
        return L
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token):
    # Number becomes numbers else a symbol
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)


def eval(x, env=global_env):
    # Evaluate an expression in an environment
    if isinstance(x, Symbol):# variable reference
        return env.find(x)[x]
        # return env[x]  
    elif not isinstance(x, List):  # constant literal
        return x

    op, *args = x 
    if op == 'quote':  # (quote exp)
        return args[0]
    elif op == 'if':
        (test, conseq, alt) = args
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif op == 'define':
        (symbol, exp) = args
        env[symbol] = eval(exp, env)
    elif op == 'set!':
        (symbol, exp) = args
        env.find(symbol)[symbol] = eval(exp, env)
    elif op == 'lambda':
        (params, body) = args
        return Procedure(params, body, env)
    else:  # procedure call
        proc = eval(op, env)
        vals = [eval(arg, env) for arg in args]
        return proc(*vals)


def repl(prompt='lisp>>= '):
    # A prompt-read-eval-print loop
    while True:
        val = eval(parse(input(prompt)))
        if val is not None:
            print(schemstr(val))


def schemstr(exp):
    # Convert a python object back into scheme readable string
    if isinstance(exp, List):
        return '(' + ''.join(map(schemstr, exp)) + ')'
    else:
        return str(exp)


print(tokenize('(hello(55))'))
program = "(begin (define r 10) (* pi (* r r)))"
print(parse(program))

print(eval(parse(program)))

repl()