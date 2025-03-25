import json
import psycopg2
from jsonschema import validate, ValidationError
from dotenv import load_dotenv
import os
import networkx as nx
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()

# PostgreSQL Connection Details
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError("\u274c Missing database environment variables. Ensure they are set in .env or system environment.")

# Define JSON Schema
EMPLOYEE_SCHEMA = {
    "type": "object",
    "properties": {
        "employees": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "phone": {"type": "string"},
                    "projects": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"},
                                "budget": {"type": "number"},
                                "status": {"type": "string"}
                            },
                            "required": ["id", "name", "budget", "status"]
                        }
                    }
                },
                "required": ["name", "phone", "projects"]
            }
        }
    },
    "required": ["employees"]
}

def connect_db():
    """
    Establishes a connection to the PostgreSQL database.

    Returns:
    psycopg2.connection: A connection object if successful, None otherwise.
    """
    try:
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def initialize_db():
    """
    Initializes the PostgreSQL database by creating necessary tables if they do not exist.
    """
    conn = connect_db()
    if not conn:
        return

    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                serviceETLTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                employee_phone TEXT REFERENCES employees(phone) ON DELETE CASCADE,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                budget NUMERIC NOT NULL,
                status TEXT NOT NULL,
                valid_from TIMESTAMP NOT NULL,
                valid_to TIMESTAMP,
                is_current BOOLEAN DEFAULT TRUE,
                serviceETLTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(employee_phone, project_id, valid_from)  -- Prevent duplicate projects for the same employee
            );
        """)
        conn.commit()

    conn.close()
    print("✅ Database initialized successfully.")

def update_json(json_file: str, phone, new_projects):
    """
    Update the projects in the JSON file for a given employee.

    Parameters:
    json_file (str): Path to the JSON file.
    phone (str): Phone number of the employee.
    new_projects (list): New projects to add.
    """
    data = load_json(json_file)
    if data:
        for employee in data["employees"]:
            if employee["phone"] == phone:
                # Update status of previous projects to "completed"
                for project in employee["projects"]:
                    if project["id"] != new_projects[-1]["id"]:
                        project["status"] = "completed"

                employee["projects"].extend(new_projects)  # Add new projects to the list
                # Remove duplicate projects
                seen_projects = set()
                unique_projects = []
                for project in employee["projects"]:
                    project_tuple = tuple(project.items())
                    if project_tuple not in seen_projects:
                        seen_projects.add(project_tuple)
                        unique_projects.append(project)
                employee["projects"] = unique_projects
                save_json(json_file, data)
                return  # Exit after updating the employee

def save_to_postgres(employee_name, phone, projects, json_file="task3_employees.json"):
    """
    Merge (insert/update) an employee's projects in PostgreSQL.

    Parameters:
    employee_name (str): Name of the employee.
    phone (str): Phone number of the employee.
    projects (list): List of projects assigned to the employee.
    json_file (str): Path to the JSON file.
    """
    conn = connect_db()
    if not conn:
        return

    with conn.cursor() as cursor:
        try:
            # Insert employee if not exists
            cursor.execute("""
                INSERT INTO employees (name, phone) 
                VALUES (%s, %s) 
                ON CONFLICT (phone) DO NOTHING;
            """, (employee_name, phone))

            # Insert or update projects with serviceETLTimestamp update
            for project in projects:
                # Check if the project already exists for this employee
                cursor.execute("""
                    SELECT 1 FROM projects
                    WHERE employee_phone = %s AND project_id = %s;
                """, (phone, project["id"]))

                if cursor.fetchone():
                    # Project exists, update it
                    cursor.execute("""
                        UPDATE projects
                        SET name = %s, budget = %s, status = %s, is_current = FALSE
                        WHERE employee_phone = %s AND project_id = %s AND is_current = TRUE;
                    """, (project["name"], project["budget"], project["status"], phone, project["id"]))

                    cursor.execute("""
                        INSERT INTO projects (employee_phone, project_id, name, budget, status, valid_from, valid_to, is_current)
                        VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, '9999-12-31 23:59:59.999999', TRUE);
                    """, (phone, project["id"], project["name"], project["budget"], project["status"]))
                else:
                    # Project does not exist, insert it
                    # Update previous project valid_to and status
                    cursor.execute("""
                        UPDATE projects
                        SET valid_to = CURRENT_TIMESTAMP, is_current = FALSE, status = 'completed'
                        WHERE employee_phone = %s AND is_current = TRUE;
                    """, (phone,))

                    cursor.execute("""
                        INSERT INTO projects (employee_phone, project_id, name, budget, status, valid_from, valid_to, is_current)
                        VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, '9999-12-31 23:59:59.999999', TRUE);
                    """, (phone, project["id"], project["name"], project["budget"], project["status"]))

            conn.commit()
            print(f"✅ Data saved/updated for {employee_name}.")

            # Update JSON file after processing all projects
            if projects:
                update_json(json_file, phone, projects)

        except Exception as e:
            print(f"❌ Error inserting/updating data: {e}")
            print(f"   - {e}")
            conn.rollback()

    conn.close()

def validate_json(json_data: str, schema: dict) -> bool:
    """
    Validates JSON data against a predefined schema.

    Parameters:
    json_data (str): JSON data as a string.
    schema (dict): The JSON schema for validation.

    Returns:
    bool: True if validation is successful, False otherwise.
    """
    try:
        parsed_json = json.loads(json_data)  # Convert string to dictionary
        validate(instance=parsed_json, schema=schema)  # Validate against schema
        print("✅ JSON validation successful.")
        return True
    except ValidationError as e:
        print(f"❌ JSON validation failed: {e.message}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
        return False

def load_json(json_file: str) -> dict:
    """
    Loads JSON data from a file.

    Parameters:
    json_file (str): Path to the JSON file.

    Returns:
    dict: Parsed JSON data if successful, None otherwise.
    """
    try:
        with open(json_file, "r") as file:
            data = file.read()

        if validate_json(data, EMPLOYEE_SCHEMA):  # Validate before parsing
            return json.loads(data)
        else:
            print("❌ JSON validation failed. Exiting.")
            return None
    except FileNotFoundError:
        print(f"❌ Error: File '{json_file}' not found.")
        return None
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON format in the file.")
        return None

def save_json(json_file: str, data: dict) -> None:
    """
    Saves JSON data to a file.

    Parameters:
    json_file (str): Path to the JSON file where data should be saved.
    data (dict): The JSON data to be written to the file.

    Returns:
    None
    """
    try:
        with open(json_file, "w") as file:
            json.dump(data, file, indent=4)
        print(f"✅ Successfully saved JSON to {json_file}")
    except Exception as e:
        print(f"❌ Error saving JSON file: {e}")

def add_project(json_file: str, phone_number: str, target_status: str, new_project: dict) -> None:
    """
    Adds a new project to an employee's list and saves it to PostgreSQL.

    Parameters:
    - json_file (str): Path to the JSON file containing employee data.
    - phone_number (str): Phone number of the employee.
    - target_status (str): Status of the last project to insert after.
    - new_project (dict): New project details (id, name, budget, status).
    """
    data = load_json(json_file)
    if data is None:
        return  # Exit if JSON loading fails

    for employee in data["employees"]:
        if employee["phone"] == phone_number:
            employee["projects"].append(new_project)  # Append the new project to the end
            print(f"✅ Project '{new_project['name']}' added for {employee['name']}.")

            save_json(json_file, data)  # Save updated JSON
            save_to_postgres(employee["name"], phone_number, [new_project])  # Save to DB
            return

    print("❌ Employee not found.")

def visualize_employee_projects():
    """
    Visualizes employee-project relationships as a network graph.
    """
    conn = connect_db()
    if not conn:
        return

    G = nx.DiGraph()

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT e.name, p.name AS project_name, p.status
            FROM employees e
            JOIN projects p ON e.phone = p.employee_phone
        """)

        for employee_name, project_name, status in cursor.fetchall():
            G.add_node(employee_name, color='blue')
            G.add_node(project_name, color='green' if status == 'ongoing' else 'red')
            G.add_edge(employee_name, project_name)

    conn.close()

    # Define node colors
    colors = [G.nodes[node]['color'] for node in G.nodes()]

    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color=colors, edge_color='gray', node_size=2000, font_size=10)
    plt.title("Employee-Project Relationships")
    plt.show()

# Initialize the database
initialize_db()

# Example usage
# new_project = {
#     "id": 6,
#     "name": "Project Delta",
#     "budget": 3000,
#     "status": "ongoing"
# }

# add_project("task3_employees.json", "987-654-3210", "ongoing", new_project)

if __name__ == "__main__":
    json_file = "employees.json"  # Initial JSON file path

    # Prompt user for input
    phone_number = input("Enter employee's phone number: ")
    target_status = input("Enter the status of the project to insert after: ")
    new_project_id = int(input("Enter new project ID: "))
    new_project_name = input("Enter new project name: ")
    new_project_budget = int(input("Enter new project budget: "))
    new_project_status = input("Enter new project status: ")

    new_project = {
        "id": new_project_id,
        "name": new_project_name,
        "budget": new_project_budget,
        "status": new_project_status
    }

    add_project(json_file, phone_number, target_status, new_project)

    # Call visualization function
    visualize_employee_projects()