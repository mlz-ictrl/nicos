from __future__ import absolute_import, division, print_function

import ast


class TemplateScriptHandler(ast.NodeVisitor):

    # Store the found keys by block id of the AST
    blocks = {}

    # Store the values for the keys (without key marker)
    values = {}

    kmark = '__'  # key marker

    def __init__(self, code):
        self.ast = ast.parse(code)
        for i, node in enumerate(self.ast.body):
            self.found = []
            self.visit(node)
            if self.found:
                self.blocks[i] = self.found

    def extract_data(self, text):
        self.values = {}
        # print('%s' % text)
        _ast = ast.parse(text)
        for i in self.blocks:
            if i >= len(_ast.body):
                break
            v = self._extract_node(self.ast.body[i], _ast.body[i])
            # print(self.blocks[i], '%r' % v)
            self.values.update(
                {k.strip(self.kmark): v for k, v in zip(self.blocks[i], v)})
        return self.values

    def get(self, key):
        return self.values.get(key, None)

    def _extract_node(self, node1, node2):
        if type(node1) != type(node2):  # pylint: disable=unidiomatic-typecheck
            return []
        if isinstance(node1, ast.Assign):
            return self._extract_assign(node1, node2)
        elif isinstance(node1, ast.Expr):
            return self._extract_expr(node1, node2)
        elif isinstance(node1, ast.For):
            return self._extract_for(node1, node2)

    def _extract_attribute(self, node1, node2):
        ret = []
        if self._is_key(self._value(node1.value)):
            ret.append(self._value(node2.value))
        if self._is_key(node1.attr):
            ret.append(self._value(node2.attr))
        return ret

    def _extract_for(self, node1, node2):
        ret = []
        if self._is_key(self._value(node1.target)):
            ret.append(self._value(node2.target))
        if isinstance(node1.iter, ast.Attribute):
            ret.extend(self._extract_attribute(node1.iter, node2.iter))
        for b1, b2 in zip(node1.body, node2.body):
            if isinstance(b1, ast.Assign):
                ret.extend(self._extract_assign(b1, b2))
        return ret

    def _extract_expr(self, node1, node2):
        # pylint: disable=unidiomatic-typecheck
        if type(node1.value) != type(node2.value):
            return []
        if isinstance(node1.value, ast.Call):
            return self._extract_call(node1.value, node2.value)
        else:
            print('EXPR', node1.value, node2.value)

    def _extract_call(self, node1, node2):
        ret = []
        if isinstance(node1.func, ast.Name):
            if node1.func.id != node2.func.id:
                return ret
            if node1.args or node2.args:
                for a1, a2 in zip(node1.args, node2.args):
                    if isinstance(a1, ast.Str) and self._is_key(a1.s):
                        ret.append(self._value(a2))
                    elif isinstance(a1, ast.Starred) and \
                       self._is_key(a1.value.id):
                        ret.append(self._value(a2.value))
            if node1.keywords or node2.keywords:
                for k1, k2 in zip(node1.keywords, node2.keywords):
                    if self._is_key(k1.arg):
                        ret.append(k2.arg)
                    if self._is_key(self._value(k1.value)):
                        ret.append(self._value(k2.value))
        elif isinstance(node1.func, ast.Attribute):
            # print('Call', node1.func.attr, node2.func.attr)
            if node1.func.attr == node2.func.attr:
                if node1.args or node2.args:
                    for a1, a2 in zip(node1.args, node2.args):
                        if self._is_key(self._value(a1)):
                            ret.append(self._value(a2))
        return ret

    def _extract_assign(self, node1, node2):
        if len(node1.targets) != len(node2.targets):
            return []
        ret = []
        for (n1, n2) in zip(node1.targets, node2.targets):
            if isinstance(n1, (ast.Tuple, ast.List)):
                for name1, name2 in zip(n1.elts, n2.elts):
                    if self._value(name1) != self._value(name2):
                        return []
            elif isinstance(n1, ast.Attribute):
                ret.extend(self._extract_attribute(n1, n2))
        if isinstance(node1.value, (ast.List, ast.Tuple)):
            for n1, n2 in zip(node1.value.elts, node2.value.elts):
                if self._is_key(self._value(n1)):
                    ret.append(self._value(n2))
        else:
            ret.append(self._value(node2.value))
        return ret

    def _value(self, node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.List):
            return self._list(node)
        elif isinstance(node, ast.Tuple):
            return tuple(self._list(node))
        else:
            print('Value', node.value)

    def _list(self, node):
        return [self._value(e) for e in node.elts]

    def _is_key(self, s):
        if isinstance(s, str):
            return s.startswith(self.kmark) and s.endswith(self.kmark)
        return False

    def visit_Name(self, t):
        if self._is_key(t.id):
            self.found.append(t.id)

    def visit_Str(self, t):
        if self._is_key(t.s):
            self.found.append(t.s)

    def visit_keyword(self, t):
        if self._is_key(t.arg):
            self.found.append(t.arg)
        self.generic_visit(t)
