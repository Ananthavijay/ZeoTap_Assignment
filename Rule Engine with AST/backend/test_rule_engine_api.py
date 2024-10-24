import pytest
from httpx import AsyncClient, ASGITransport
from rule_engine_api import app  # Ensure you import your FastAPI app

@pytest.mark.asyncio
async def test_create_rule_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1:8000") as client:
        response = await client.post("/create_rule", json={
            "rule_name": "Test Rule 1",
            "rule_string": "((age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')) AND (salary > 50000 OR experience > 5)"
        })
        assert response.status_code == 201
        assert response.json() == {"message": "Rule created successfully"}

@pytest.mark.asyncio
async def test_create_rule_duplicate_name():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1:8000") as client:
        response = await client.post("/create_rule", json={
            "rule_name": "Test Rule 1",  # This name already exists
            "rule_string": "age < 30 AND department = 'Support'"
        })
        assert response.status_code == 400
        assert response.json().get("detail") == "Rule name already exists."

@pytest.mark.asyncio
async def test_evaluate_rule_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1:8000") as client:
        response = await client.post("/evaluate_rule", json={
            "rule_id": 1,  # Assuming this rule ID exists
            "data": {
                "age": 35,
                "department": "Sales",
                "salary": 60000,
                "experience": 6
            }
        })
        assert response.status_code == 200
        assert response.json().get("evaluation_result") is True

@pytest.mark.asyncio
async def test_evaluate_rule_non_existent():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1:8000") as client:
        response = await client.post("/evaluate_rule", json={
            "rule_id": 9999,  # Non-existent rule ID
            "data": {
                "age": 35,
                "department": "Sales",
                "salary": 60000,
                "experience": 6
            }
        })
        assert response.status_code == 404
        assert response.json().get("detail") == "Rule not found"

@pytest.mark.asyncio
async def test_evaluate_rule_missing_data():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1:8000") as client:
        response = await client.post("/evaluate_rule", json={
            "rule_id": 1,
            "data": {
                "age": 35,
                # Missing department, salary, experience
            }
        })
        assert response.status_code == 200
        assert response.json().get("evaluation_result") is False

@pytest.mark.asyncio
async def test_combine_rules_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1:8000") as client:
        response = await client.post("/combine_rules", json={
            "rule_name": "Combined Test Rule",
            "rule_strings": [
                "age > 30 AND department = 'Sales'",
                "age < 25 AND department = 'Marketing'"
            ]
        })
        assert response.status_code == 201
        assert response.json() == {"message": "Rules combined successfully"}

@pytest.mark.asyncio
async def test_combine_rules_duplicate_name():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1:8000") as client:
        response = await client.post("/combine_rules", json={
            "rule_name": "Combined Test Rule",  # This name already exists
            "rule_strings": [
                "age > 30",
                "salary > 50000"
            ]
        })
        assert response.status_code == 400
        assert response.json().get("detail") == "Combined rule name already exists."

@pytest.mark.asyncio
async def test_create_rule_invalid_syntax():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1:8000") as client:
        response = await client.post("/create_rule", json={
            "rule_name": "Invalid Rule",
            "rule_string": "age > 30 AND AND department = 'Sales'"  # Invalid syntax
        })
        assert response.status_code == 400
        assert response.json().get("detail") == "Invalid sequence of operators."

@pytest.mark.asyncio
async def test_current_rules():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1:8000") as client:
        response = await client.get("/current_rules")
        assert response.status_code == 200
        assert isinstance(response.json().get("rules"), list)

if __name__ == "__main__":
    pytest.main()
