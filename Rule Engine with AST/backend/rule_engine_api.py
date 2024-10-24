from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import re
import json

app = FastAPI()

DATABASE_PATH = "./database/rules.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH, timeout=5)
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic models for requests
class RuleRequest(BaseModel):
    rule_name: str
    rule_string: str

class EvaluationRequest(BaseModel):
    rule_id: int
    data: dict

class CombineRulesRequest(BaseModel):
    rule_name: str
    rule_strings: list

class Node:
    def __init__(self, node_type, value=None, left=None, right=None):
        self.node_type = node_type
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self):
        return f'Node(type={self.node_type}, value={self.value}, left={self.left}, right={self.right})'

# Helper functions for rule parsing and evaluation
def validate_condition(condition):
    comparison_operators = [r'<=', r'>=', r'!=', r'=', r'>', r'<']
    pattern = r'^\s*\w+\s*(' + '|'.join(comparison_operators) + r')\s+.+$'
    if not re.match(pattern, condition):
        raise HTTPException(status_code=400, detail="Each condition must include a valid comparison operator.")

def parse_condition(condition):
    validate_condition(condition)
    return Node("operand", value=condition)

def create_ast(rule_string):
    tokens = re.split(r'(\(|\)|AND|OR)', rule_string)
    tokens = [token.strip() for token in tokens if token.strip() != '']
    return build_ast(tokens)

def build_ast(tokens):
    stack = []
    operators = []

    for token in tokens:
        if token == '(':
            operators.append(token)
        elif token == ')':
            while operators and operators[-1] != '(':
                right = stack.pop()
                left = stack.pop()
                operator = operators.pop()
                stack.append(Node("operator", value=operator, left=left, right=right))
            operators.pop()
        elif token in ("AND", "OR"):
            operators.append(token)
        else:
            stack.append(parse_condition(token))

    while operators:
        right = stack.pop()
        left = stack.pop()
        operator = operators.pop()
        stack.append(Node("operator", value=operator, left=left, right=right))

    return stack[0] if stack else None

def is_valid_rule(rule_string):
    if rule_string.count('(') != rule_string.count(')'):
        raise HTTPException(status_code=400, detail="Parentheses are not balanced.")
    if not re.match(r'^[\w\s><=()\'\"ANDOR]+$', rule_string):
        raise HTTPException(status_code=400, detail="Invalid characters in rule.")
    if re.search(r'AND\s*AND|OR\s*OR', rule_string):
        raise HTTPException(status_code=400, detail="Invalid sequence of operators.")

def evaluate_ast(node, data):
    if node.node_type == "operand":
        # Extract the operand's condition and evaluate it
        try:
            # The operand should be a condition in the form of "key operator value"
            key, operator, value = node.value.split()
            key = key.strip()
            value = eval(value.strip())  # Evaluate value for numbers
            data_value = data.get(key)
            if data_value is None:
                return False
            # Perform the comparison based on the operator
            if operator == '>':
                return data_value > value
            elif operator == '<':
                return data_value < value
            elif operator == '=':
                return data_value == value
            elif operator == '>=':
                return data_value >= value
            elif operator == '<=':
                return data_value <= value
            elif operator == '!=':
                return data_value != value
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported operator: {operator}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error evaluating condition: {str(e)}")
    elif node.node_type == "operator":
        left_eval = evaluate_ast(node.left, data)
        right_eval = evaluate_ast(node.right, data)
        if node.value == "AND":
            return left_eval and right_eval
        elif node.value == "OR":
            return left_eval or right_eval

# Function to deserialize the AST
def deserialize_ast(ast_dict):
    if isinstance(ast_dict, dict):
        node = Node(ast_dict['node_type'], ast_dict['value'])
        node.left = deserialize_ast(ast_dict['left']) if 'left' in ast_dict else None
        node.right = deserialize_ast(ast_dict['right']) if 'right' in ast_dict else None
        return node
    return None

# API Endpoints
@app.post("/create_rule", status_code=201)
def create_rule(rule_request: RuleRequest):
    rule_string = rule_request.rule_string
    is_valid_rule(rule_string)

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if rule name already exists
    cursor.execute("SELECT * FROM rules WHERE name = ?", (rule_request.rule_name,))
    if cursor.fetchone() is not None:
        raise HTTPException(status_code=400, detail="Rule name already exists.")
    
    ast = create_ast(rule_string)
    cursor.execute("INSERT INTO rules (name, rule_string, ast) VALUES (?, ?, ?)",
                   (rule_request.rule_name, rule_string, json.dumps(ast, default=lambda x: x.__dict__)))
    
    conn.commit()
    conn.close()

    return {"message": "Rule created successfully"}

@app.post("/evaluate_rule")
def evaluate_rule(eval_request: EvaluationRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM rules WHERE id = ?", (eval_request.rule_id,))
    rule = cursor.fetchone()

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    ast = deserialize_ast(json.loads(rule["ast"]))
    data = eval_request.data
    result = evaluate_ast(ast, data)
    
    return {"evaluation_result": result}

@app.post("/combine_rules", status_code=201)
def combine_rules(combine_request: CombineRulesRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if rule name already exists
    cursor.execute("SELECT * FROM rules WHERE name = ?", (combine_request.rule_name,))
    if cursor.fetchone() is not None:
        raise HTTPException(status_code=400, detail="Combined rule name already exists.")

    asts = []
    for rule_string in combine_request.rule_strings:
        is_valid_rule(rule_string)
        ast = create_ast(rule_string)
        asts.append(ast)

    # Combine rules by creating a new AST
    combined_ast = combine_ast(asts)

    cursor.execute("INSERT INTO rules (name, rule_string, ast) VALUES (?, ?, ?)",
                   (combine_request.rule_name, " AND ".join(combine_request.rule_strings), json.dumps(combined_ast, default=lambda x: x.__dict__)))
    
    conn.commit()
    conn.close()

    return {"message": "Rules combined successfully"}

def combine_ast(asts):
    if not asts:
        return None
    root = asts[0]
    for ast in asts[1:]:
        root = Node("operator", value="AND", left=root, right=ast)
    return root

# Debugging function to print AST
def print_ast(node, level=0):
    if node:
        print(' ' * (level * 2) + repr(node))
        print_ast(node.left, level + 1)
        print_ast(node.right, level + 1)

@app.get("/current_rules")
def current_rules():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM rules")
    rules = cursor.fetchall()
    
    conn.close()
    return {"rules": [dict(rule) for rule in rules]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
