from mcp.server.fastmcp import FastMCP
from typing import List
from db import get_employees_collection

# Remove in-memory mock database
# employee_leaves = {...}

# Create MCP server
mcp = FastMCP("LeaveManager")
employees = get_employees_collection()
 
# Tool: Check Leave Balance
@mcp.tool()
def get_leave_balance(employee_id: str) -> str:
    """Check how many leave days are left for the employee"""
    data = employees.find_one({"employee_id": employee_id})
    if data:
        return f"{data['name']} ({employee_id}) has {data['balance']} leave days remaining."
    return "Employee ID not found."

# Tool: Apply for Leave with specific dates
@mcp.tool()
def apply_leave(employee_id: str, name: str, leave_dates: List[str]) -> str:
    """
    Apply leave for specific dates (e.g., ["2025-04-17", "2025-05-01"])
    """
    data = employees.find_one({"employee_id": employee_id})
    if not data:
        return "Employee ID not found."
    if data["name"] != name:
        return f"Name does not match for employee ID {employee_id}."
    requested_days = len(leave_dates)
    available_balance = data["balance"]
    if available_balance < requested_days:
        return f"Insufficient leave balance. You requested {requested_days} day(s) but have only {available_balance}."
    # Update balance and history in MongoDB
    employees.update_one(
        {"employee_id": employee_id},
        {"$inc": {"balance": -requested_days}, "$push": {"history": {"$each": leave_dates}}}
    )
    updated = employees.find_one({"employee_id": employee_id})
    return f"Leave applied for {requested_days} day(s) for {name} ({employee_id}). Remaining balance: {updated['balance']}."

# Resource: Leave history
@mcp.tool()
def get_leave_history(employee_id: str = None, name: str = None) -> str:
    """Get leave history for the employee by ID or name (at least one required)"""
    if not employee_id and not name:
        return "Please provide either employee ID or name."
    if employee_id:
        data = employees.find_one({"employee_id": employee_id})
        if not data:
            return f"Employee ID {employee_id} not found."
        if name and data["name"] != name:
            return f"Name does not match for employee ID {employee_id}."
        history = ', '.join(data['history']) if data['history'] else "No leaves taken."
        return f"Leave history for {data['name']} ({employee_id}): {history}"
    matches = list(employees.find({"name": {"$regex": f"^{name}$", "$options": "i"}}))
    if not matches:
        return f"No employee found with the name '{name}'."
    if len(matches) > 1:
        ids = ', '.join(emp['employee_id'] for emp in matches)
        return f"Multiple employees found with the name '{name}'. Please specify the employee ID. IDs: {ids}"
    data = matches[0]
    history = ', '.join(data['history']) if data['history'] else "No leaves taken."
    return f"Leave history for {data['name']} ({data['employee_id']}): {history}"

# Tool: Add a new employee
@mcp.tool()
def add_employee(employee_id: str, name: str, initial_balance: int = 30) -> str:
    """Add a new employee with a name and an optional initial leave balance (default 20)"""
    if employees.find_one({"employee_id": employee_id}):
        return f"Employee {employee_id} already exists."
    employees.insert_one({
        "employee_id": employee_id,
        "name": name,
        "balance": initial_balance,
        "history": []
    })
    return f"Employee {name} ({employee_id}) added with {initial_balance} leave days."

# Tool: Count employees
@mcp.tool()
def count_employees() -> str:
    """Return the total number of employees in the system."""
    count = employees.count_documents({})
    return f"There are {count} employees in the system."

# Tool: Add a reason for leave for specific dates
@mcp.tool()
def add_leave_reason(employee_id: str, name: str, leave_dates: List[str], reason: str) -> str:
    """Add a reason for leave for specific dates. Appends to the 'leaves_reason' list in the employee document."""
    data = employees.find_one({"employee_id": employee_id})
    if not data:
        return "Employee ID not found."
    if data["name"] != name:
        return f"Name does not match for employee ID {employee_id}."
    # Add the reason and dates to the leaves_reason list
    employees.update_one(
        {"employee_id": employee_id},
        {"$push": {"leaves_reason": {"dates": leave_dates, "reason": reason}}}
    )
    return f"Leave reason added for {name} ({employee_id}) for dates {', '.join(leave_dates)}: {reason}"

# Tool: Delete an employee
@mcp.tool()
def delete_employee(employee_id: str, name: str) -> str:
    """Delete an employee from the system by employee_id and name."""
    data = employees.find_one({"employee_id": employee_id})
    if not data:
        return "Employee ID not found."
    if data["name"] != name:
        return f"Name does not match for employee ID {employee_id}."
    employees.delete_one({"employee_id": employee_id})
    return f"Employee {name} ({employee_id}) has been deleted from the system."

# Resource: Greeting
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}! How can I assist you with leave management today?"

if __name__ == "__main__":
    mcp.run()