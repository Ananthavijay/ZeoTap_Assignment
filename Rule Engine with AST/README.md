## Rule Engine with AST
This project implements a rule engine using a FastAPI backend and a Flask frontend. Users can create, evaluate, and combine rules based on specific conditions, enabling dynamic rule evaluation against given data.

### Features
- Rule Creation: Users can define rules with logical conditions.
- Rule Evaluation: Evaluate rules against data inputs.
- Rule Combination: Combine multiple rules into a single rule.
- Current Rules Retrieval: Fetch all defined rules from the database.
- Rule Validation: Detect errors such as:
    - Unbalanced parentheses
    - Invalid characters in rule strings
    - Invalid sequences of operators
    - Missing comparison operators

### Tech Stack
- Backend: FastAPI for building the API.
- Database: SQLite for rule storage.
- Frontend: Flask for user interface.
- Testing: Pytest for testing API endpoints and functionality.

### How It Works
The project separates the frontend and backend. The frontend provides a user-friendly interface to interact with the API. Users can create and evaluate rules through the interface, but the API can also be accessed independently for programmatic usage.

### Setup Steps
- Database Initialization: Run `python backend/database_init.py` to create the SQLite database.
- Start the API: Launch the FastAPI server using `python backend/rule_engine_api.py`, which starts at `http://127.0.0.1:8000`.
- Start the Frontend: Run the Flask application using `python frontend/rule_engine_frontend.py`.
- Access the Application: Navigate to `http://127.0.0.1:5000` in your web browser.

### Testing
- Install pytest if not already installed: `pip install pytest`
- Run the tests by executing the following command: `pytest backend/test_rule_engine_api.py`

### Project Structure:
```
rule_engine_project/
│
├── backend/
|   ├── database/
|       └─── rules.db               # SQLite database
│   ├── database_init.py            # SQLite database setup and initialization
│   ├── rule_engine_api.py          # FastAPI application for rule management
│   └── test_rule_engine_api.py     # Automated tests for the FastAPI application
│
├── frontend/
│   ├── rule_engine_frontend.py    # Flask application for the frontend
│   └── templates/
│       └── index.html             # HTML template for the web interface
│
└── requirements.txt                # Python package dependencies
```

## Screen Shots
### 1. UI
![image](https://github.com/user-attachments/assets/a349f490-9d83-40ba-a353-d543faa7c36d)

### 2. Rule Creation
![image](https://github.com/user-attachments/assets/096e27ec-85ae-4cf1-bbf4-a183f3bf0e6b)

### 3. Rule Evaluation
- The data should be provided in JSON format, e.g., `{"age": 35, "department": "Marketing"}`

![image](https://github.com/user-attachments/assets/77ccb99e-6591-478b-b1aa-7569d57698b3)

### 4. Rule Combination
- Select the rules you want to combine, then press Combine to merge the selected rules

![image](https://github.com/user-attachments/assets/e8d2d495-bbb7-4db5-9e3c-d7c6e9f9f8b4)
![image](https://github.com/user-attachments/assets/5f1e6beb-20d4-4d28-a4eb-271ed32cc065)

### 5. Rule Validation
- This is an example of an error that occurs when the condition is invalid, e.g., (age = 30 AND department = 'Sales')

![image](https://github.com/user-attachments/assets/8d830354-bcd1-423b-b545-93a7814e75a4)

