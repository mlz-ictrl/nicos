#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""Script analyzer functions."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import operator

try:
    # needs Python 2.5
    import _ast as ast
except ImportError:
    ast = None

from nicos.gui import custom


OP_FUNCS = {
    ast.Add:        operator.add,
    ast.Sub:        operator.sub,
    ast.Mult:       operator.mul,
    ast.Div:        operator.div,
    ast.FloorDiv:   operator.floordiv,
    ast.Mod:        operator.mod,
    ast.Pow:        pow,
    ast.LShift:     operator.lshift,
    ast.RShift:     operator.rshift,
    ast.BitOr:      operator.or_,
    ast.BitAnd:     operator.and_,
    ast.BitXor:     operator.xor,
    ast.Invert:     operator.inv,
    ast.Not:        operator.not_,
    ast.UAdd:       operator.pos,
    ast.USub:       operator.neg,
}

PyCF_ONLY_AST = 0x400
CO_FUTURE_WITH_STATEMENT = 0x8000


class AnalyzerError(Exception):
    pass

class NotConst(Exception):
    pass

notconst = object()

class WrongArgs(Exception):
    pass


class AnalyzerResult(object):
    def __init__(self):
        self.errors = set()
        self.device_ranges = {}
        self.count_time = 0
        self.move_time = 0
        self.other_time = 0
        self.timing_problems = set()

    @property
    def total_time(self):
        return self.count_time + self.move_time + self.other_time


class UserFunction(object):
    def __init__(self, name, arguments, body):
        self.name = name
        self.arguments = arguments
        self.body = body

    def get_args(self, call):
        argnames = [arg.id for arg in self.arguments.args]
        return Analyzer.parse_args(self.name, call,
                                   argnames, self.arguments.defaults,
                                   self.arguments.vararg, self.arguments.kwarg)

    def do_call(self, analyzer, call):
        argdict, (pva, starargs), (kva, starkwds) = self.get_args(call)

        inneranalyzer = analyzer.copy()
        for name, value in argdict.items():
            try:
                argdict[name] = analyzer.const_eval(value)
            except NotConst:
                argdict[name] = notconst
        inneranalyzer.locals.update(argdict)
        if pva:
            newstarargs = []
            for value in starargs:
                try:
                    newstarargs.append(analyzer.const_eval(value))
                except NotConst:
                    newstarargs.append(notconst)
            inneranalyzer.locals[pva] = tuple(newstarargs)
        if kva:
            for name, value in starkwds.items():
                try:
                    starkwds[name] = analyzer.const_eval(value)
                except NotConst:
                    starkwds[name] = notconst
            inneranalyzer.locals[kva] = starkwds
        inneranalyzer.do_suite(self.body)
        analyzer.device_values.update(inneranalyzer.device_values)


class Analyzer(object):

    def __init__(self, result):
        self.result = result
        # customization data
        self.function_analyzers = custom.ANALYZERS
        self.move_analyzers = custom.MOVE_ANALYZERS
        # dictionary of tracked local variables
        self.locals = {}
        # dictionary of local overrides
        self.local_overrides = {}
        # dictionary of device values
        self.device_values = {}

    def copy(self):
        res = self.__class__(self.result)
        res.locals.update(self.locals)
        res.local_overrides.update(self.local_overrides)
        res.device_values.update(self.device_values)
        return res

    def tick(self, count_time, move_time=0, other_time=0):
        self.result.count_time += count_time
        self.result.move_time  += move_time
        self.result.other_time += other_time

    def timing_problem(self, msg, node=None):
        entry = (node and node.lineno or -1, msg)
        self.result.timing_problems.add(entry)

    def error(self, msg, node=None):
        entry = (node and node.lineno or -1, msg)
        self.result.errors.add(entry)

    def set_local_override(self, name, value):
        self.local_overrides[name] = value

    def assign(self, name, value):
        self.locals[name] = self.local_overrides.get(name, value)

    def const__range(self, args, kwds):
        return range(*args, **kwds)

    def const__reversed(self, args, kwds):
        return reversed(*args, **kwds)

    def const__zip(self, args, kwds):
        return zip(*args, **kwds)

    def const__str(self, args, kwds):
        return str(*args, **kwds)

    def const_eval(self, expr):
        if not isinstance(expr, ast.AST):
            # assume already evaluated
            return expr
        # partly copied from Python 2.6 ast.literal_eval(), but does
        # a little more like evaluating binops of constants
        _safe_names = {'None': None, 'True': True, 'False': False}
        def _convert(node):
            if isinstance(node, ast.Str):
                return node.s
            elif isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.Tuple):
                return tuple(map(_convert, node.elts))
            elif isinstance(node, ast.List):
                return list(map(_convert, node.elts))
            elif isinstance(node, ast.Dict):
                return dict((_convert(k), _convert(v)) for k, v
                            in zip(node.keys, node.values))
            elif isinstance(node, ast.Name):
                if node.id in _safe_names:
                    return _safe_names[node.id]
                elif node.id in self.locals:
                    if self.locals[node.id] is notconst:
                        raise NotConst
                    return self.locals[node.id]
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and \
                       hasattr(self, 'const__' + node.func.id):
                    args = map(_convert, node.args)
                    kwds = dict((arg, _convert(val))
                                for (arg, val) in node.keywords)
                    func = getattr(self, 'const__' + node.func.id)
                    try:
                        return func(args, kwds)
                    except Exception:
                        raise NotConst
            elif isinstance(node, ast.BinOp):
                return OP_FUNCS[type(node.op)](_convert(node.left),
                                               _convert(node.right))
            elif isinstance(node, ast.UnaryOp):
                return OP_FUNCS[type(node.op)](_convert(node.operand))
            raise NotConst
        return _convert(expr)

    def do_move(self, devarg, pos):
        if isinstance(devarg, ast.Name):
            try:
                # may be assigned or a function param
                devname = self.const_eval(devarg.id)
            except NotConst:
                devname = devarg.id
        elif isinstance(devarg, ast.Str):
            devname = devarg.s
        else:
            # device is not a constant
            self.timing_problem('device is not a constant', devarg)
            return
        if devname not in self.device_values:
            # previous value not known yet, just set it (but only if number)
            if isinstance(pos, (int, long, float)):
                self.device_values[devname] = pos
                self.result.device_ranges[devname] = pos, pos
        else:
            prevpos = self.device_values[devname]
            try:
                diff = pos - prevpos
            except Exception:
                pass
            else:
                if devname in self.move_analyzers:
                    self.move_analyzers[devname](self, diff)
                self.device_values[devname] = pos
                pmin, pmax = self.result.device_ranges[devname]
                self.result.device_ranges[devname] = min(pos, pmin), max(pos, pmax)

    def do_expr(self, expr):
        if isinstance(expr, ast.Call):
            # look for constant function/method names ("funcid")
            funcid = None
            if isinstance(expr.func, ast.Name):
                funcid = expr.func.id
            elif isinstance(expr.func, ast.Attribute) and \
                 isinstance(expr.func.value, ast.Name):
                funcid = expr.func.value.id + '.' + expr.func.attr
            # if the funcid is known, calculate the time
            analyzer = None
            if funcid in self.function_analyzers:
                func = self.function_analyzers[funcid]
                analyzer = lambda self, call: func(self, call.args, call)
            elif funcid in self.locals and isinstance(self.locals[funcid],
                                                      UserFunction):
                analyzer = self.locals[funcid].do_call
            if analyzer is not None:
                try:
                    analyzer(self, expr)
                # catch usually occurring exceptions
                except NotConst:
                    self.timing_problem('arguments of %s not constant' %
                                        funcid, expr)
                except (WrongArgs, IndexError):
                    self.error('arguments of %s invalid' % funcid, expr)
            else:
                self.error('unknown function: %s' % funcid, expr)
        elif isinstance(expr, ast.BoolOp):
            for val in expr.values:
                self.do_expr(val)
        elif isinstance(expr, ast.BinOp):
            self.do_expr(expr.left)
            self.do_expr(expr.right)
        elif isinstance(expr, ast.UnaryOp):
            self.do_expr(expr.operand)
        elif isinstance(expr, ast.Compare):
            self.do_expr(expr.left)
            for cmp in expr.comparators:
                self.do_expr(cmp)
        elif isinstance(expr, (ast.List, ast.Tuple)):
            for elt in expr.elts:
                self.do_expr(elt)

    def do_stmt(self, stmt):
        if isinstance(stmt, ast.Return):
            self.do_expr(stmt.value)
        elif isinstance(stmt, ast.Assign):
            try:
                val = self.const_eval(stmt.value)
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        self.assign(target.id, val)
            except NotConst:
                # for non-constant values, assigning in our namespace
                # makes no sense
                self.do_expr(stmt.value)
        elif isinstance(stmt, ast.AugAssign):
            try:
                val = self.const_eval(stmt.value)
                if isinstance(stmt.target, ast.Name):
                    self.assign(stmt.target.id, OP_FUNCS[type(stmt.op)](
                        self.locals[stmt.target.id], val))
            except KeyError:
                # raised for non-constant names
                pass
            except NotConst:
                self.do_expr(stmt.value)
        elif isinstance(stmt, ast.Print):
            for val in stmt.values:
                self.do_expr(val)
        elif isinstance(stmt, ast.For):
            # if possible, assign the values to the targets, so that something
            # like this is measurable:
            #   for tmess in [60, 30]:
            if isinstance(stmt.target, (ast.Name, ast.Tuple)):
                if isinstance(stmt.target, ast.Name):
                    target = stmt.target.id
                else:
                    target = []
                    for elt in stmt.target.elts:
                        if isinstance(elt, ast.Name):
                            target.append(elt.id)
                        else:
                            target.append(None)
                try:
                    seq = self.const_eval(stmt.iter)
                except (NotConst, TypeError):
                    self.timing_problem('loop iterator not constant', stmt)
                    self.do_suite(stmt.body)
                else:
                    for item in seq:
                        if not isinstance(target, list):
                            self.assign(target, item)
                        else:
                            try:  # this can go wrong!
                                for name, elt in zip(target, item):
                                    self.assign(name, elt)
                            except (ValueError, TypeError):
                                pass
                        self.do_suite(stmt.body)
            else:
                # primitive, without assignment
                try:
                    times = len(self.const_eval(stmt.iter))
                except (NotConst, TypeError):
                    # let's assume the loop is run once
                    times = 1
                    self.timing_problem('loop iterator not constant', stmt)
                for i in range(times):
                    self.do_suite(stmt.body)
            self.do_suite(stmt.orelse)
        elif isinstance(stmt, ast.While):
            # while is hard... let's assume the loop is at least run once
            self.timing_problem('while statement used', stmt)
            self.do_suite(stmt.body)
            self.do_suite(stmt.orelse)
        elif isinstance(stmt, ast.If):
            self.timing_problem('if statement used', stmt)
            self.do_expr(stmt.test)
            # do both
            self.do_suite(stmt.body)
            self.do_suite(stmt.orelse)
        elif isinstance(stmt, ast.With):
            self.do_expr(stmt.context_expr)
            self.do_suite(stmt.body)
        elif isinstance(stmt, ast.TryExcept):
            # let's assume the body is run without an exception
            self.do_suite(stmt.body)
            self.do_suite(stmt.orelse)
        elif isinstance(stmt, ast.TryFinally):
            self.do_suite(stmt.body)
            self.do_suite(stmt.finalbody)
        elif isinstance(stmt, ast.Expr):
            self.do_expr(stmt.value)
        elif isinstance(stmt, ast.FunctionDef):
            self.locals[stmt.name] = UserFunction(stmt.name,
                                                  stmt.args, stmt.body)
        elif isinstance(stmt, ast.Delete):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    self.locals.pop(target.id, None)
        # ignoring: ClassDef, Raise, Assert,
        # Import, ImportFrom, Exec, Global, Pass, Break, Continue

    def do_suite(self, suite):
        for stmt in suite:
            self.do_stmt(stmt)

    def do_script(self, script):
        # compile source of the script to an AST
        try:
            mod = compile_ast(script)
        except SyntaxError, err:
            self.result.errors.add((err.lineno, err.msg))
            return
        self.do_suite(mod.body)

    @staticmethod
    def parse_args(funcname, call, argnames, argdefaults,
                   varargname=None, kwargname=None):
        # call.starargs and call.kwargs are ignored for now
        n = len(argnames) - len(argdefaults)
        defaults = dict(zip(argnames[n:], argdefaults))
        pva = varargname
        kva = kwargname

        argdict, starargs, starkwds = {}, [], {}
        # assign positional arguments
        for argname, arg in map(None, argnames, call.args):
            if argname is None:
                if pva:
                    starargs.append(arg)
                else:
                    raise WrongArgs('%s: too many positional args' % funcname)
            elif arg is not None:
                argdict[argname] = arg
        # assign keyword arguments
        for kwd in call.keywords:
            if kwd.arg not in argnames:
                if kva:
                    starkwds[kwd.arg] = kwd.value
                else:
                    raise WrongArgs('%s: invalid keyword args' % funcname)
            else:
                argdict[kwd.arg] = kwd.value
        # assign defaults to args not given
        for argname in argnames:
            if argname not in argdict:
                if argname in defaults:
                    argdict[argname] = defaults[argname]
                else:
                    raise WrongArgs('%s: not enough args' % funcname)
        return argdict, (pva, starargs), (kva, starkwds)


def compile_ast(script):
    return compile(script + '\n', '?', 'exec',
                   PyCF_ONLY_AST | CO_FUTURE_WITH_STATEMENT)


def analyze(script):
    # initialize customization to instrument
    custom.load_customization()
    # no AST module -> no estimation possible
    if not ast:
        raise AnalyzerError('cannot analyze script; Python version is too old')
    result = AnalyzerResult()
    analyzer = Analyzer(result)
    analyzer.do_script(script)
    return result


def get_global_names(script):
    # return simple global assignments
    mod = compile_ast(script)
    names = []
    for stmt in mod.body:
        if not isinstance(stmt, ast.Assign):
            continue
        for target in stmt.targets:
            if isinstance(target, ast.Name):
                names.append(target.id)
    return names
