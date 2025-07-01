from mcp.server.fastmcp import FastMCP
from typing import List

# In-memory mock database with 20 leave days to start
employee_leaves = {
    "E001": {"name": "Shreyas", "balance": 25, "history": ["2025-03-25", "2025-03-26", "2025-03-27", "2025-03-28", "2025-03-29"]},
    "E002": {"name": "Sharath", "balance": 30, "history": []}
}

# Create MCP server
mcp = FastMCP("LeaveManager")

# Tool: Check Leave Balance
@mcp.tool()
def get_leave_balance(employee_id: str) -> str:
    """Check how many leave days are left for the employee"""
    data = employee_leaves.get(employee_id)
    if data:
        return f"{data['name']} ({employee_id}) has {data['balance']} leave days remaining."
    return "Employee ID not found."

# Tool: Apply for Leave with specific dates
@mcp.tool()
def apply_leave(employee_id: str, name: str, leave_dates: List[str]) -> str:
    """
    Apply leave for specific dates (e.g., ["2025-04-17", "2025-05-01"])
    """
    data = employee_leaves.get(employee_id)
    if not data:
        return "Employee ID not found."
    if data["name"] != name:
        return f"Name does not match for employee ID {employee_id}."

    requested_days = len(leave_dates)
    available_balance = data["balance"]

    if available_balance < requested_days:
        return f"Insufficient leave balance. You requested {requested_days} day(s) but have only {available_balance}."

    # Deduct balance and add to history
    data["balance"] -= requested_days
    data["history"].extend(leave_dates)

    return f"Leave applied for {requested_days} day(s) for {name} ({employee_id}). Remaining balance: {data['balance']}."

# Resource: Leave history
@mcp.tool()
def get_leave_history(employee_id: str = None, name: str = None) -> str:
    """Get leave history for the employee by ID or name (at least one required)"""
    if not employee_id and not name:
        return "Please provide either employee ID or name."

    # If employee_id is provided, use it
    if employee_id:
        data = employee_leaves.get(employee_id)
        if not data:
            return f"Employee ID {employee_id} not found."
        if name and data["name"] != name:
            return f"Name does not match for employee ID {employee_id}."
        history = ', '.join(data['history']) if data['history'] else "No leaves taken."
        return f"Leave history for {data['name']} ({employee_id}): {history}"

    # If only name is provided, search for it
    matches = [(eid, d) for eid, d in employee_leaves.items() if d["name"].lower() == name.lower()]
    if not matches:
        return f"No employee found with the name '{name}'."
    if len(matches) > 1:
        ids = ', '.join(eid for eid, _ in matches)
        return f"Multiple employees found with the name '{name}'. Please specify the employee ID. IDs: {ids}"
    eid, data = matches[0]
    history = ', '.join(data['history']) if data['history'] else "No leaves taken."
    return f"Leave history for {name} ({eid}): {history}"

# Resource: Greeting
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}! How can I assist you with leave management today?"

# Tool: Add a new employee
@mcp.tool()
def add_employee(employee_id: str, name: str, initial_balance: int = 20) -> str:
    """Add a new employee with a name and an optional initial leave balance (default 20)"""
    if employee_id in employee_leaves:
        return f"Employee {employee_id} already exists."
    employee_leaves[employee_id] = {"name": name, "balance": initial_balance, "history": []}
    return f"Employee {name} ({employee_id}) added with {initial_balance} leave days."

# Tool: Count employees
@mcp.tool()
def count_employees() -> str:
    """Return the total number of employees in the system."""
    count = len(employee_leaves)
    return f"There are {count} employees in the system."

if __name__ == "__main__":
    mcp.run()