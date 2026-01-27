"""
Initialize SQLite database with mock renewable energy financial model data.

This script creates tables and populates them with realistic mock data
for renewable energy project evaluation and financial analysis.
"""

import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "renewable_energy.db"


def create_connection():
    """Create a database connection."""
    return sqlite3.connect(DB_PATH)


def create_tables(conn):
    """Create all database tables."""
    cursor = conn.cursor()

    # Projects table - main project information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            project_type TEXT NOT NULL,
            location TEXT NOT NULL,
            country TEXT NOT NULL,
            capacity_mw REAL NOT NULL,
            status TEXT NOT NULL,
            start_date DATE,
            commercial_operation_date DATE,
            project_life_years INTEGER DEFAULT 25,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Financial assumptions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financial_assumptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            capex_per_mw REAL NOT NULL,
            opex_per_mw_year REAL NOT NULL,
            capacity_factor REAL NOT NULL,
            degradation_rate REAL DEFAULT 0.005,
            electricity_price_mwh REAL NOT NULL,
            price_escalation_rate REAL DEFAULT 0.02,
            discount_rate REAL NOT NULL,
            debt_ratio REAL DEFAULT 0.7,
            interest_rate REAL DEFAULT 0.05,
            loan_tenor_years INTEGER DEFAULT 15,
            tax_rate REAL DEFAULT 0.25,
            depreciation_years INTEGER DEFAULT 20,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # Annual cash flows table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS annual_cash_flows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            revenue REAL NOT NULL,
            opex REAL NOT NULL,
            ebitda REAL NOT NULL,
            depreciation REAL NOT NULL,
            interest_expense REAL NOT NULL,
            principal_repayment REAL NOT NULL,
            tax REAL NOT NULL,
            net_income REAL NOT NULL,
            free_cash_flow REAL NOT NULL,
            cumulative_cash_flow REAL NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # Key metrics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS key_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            total_capex REAL NOT NULL,
            npv REAL NOT NULL,
            irr REAL NOT NULL,
            payback_period_years REAL NOT NULL,
            lcoe REAL NOT NULL,
            dscr_min REAL NOT NULL,
            dscr_avg REAL NOT NULL,
            equity_irr REAL NOT NULL,
            total_generation_gwh REAL NOT NULL,
            carbon_offset_tonnes REAL NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # Monthly generation data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monthly_generation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            generation_mwh REAL NOT NULL,
            capacity_factor REAL NOT NULL,
            availability REAL NOT NULL,
            curtailment_mwh REAL DEFAULT 0,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # Market data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            region TEXT NOT NULL,
            wholesale_price_mwh REAL NOT NULL,
            ppa_price_mwh REAL,
            rec_price REAL,
            carbon_price REAL
        )
    """)

    # Technology benchmarks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS technology_benchmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            technology TEXT NOT NULL,
            year INTEGER NOT NULL,
            avg_capex_per_mw REAL NOT NULL,
            avg_capacity_factor REAL NOT NULL,
            avg_lcoe REAL NOT NULL,
            learning_rate REAL
        )
    """)

    conn.commit()


def generate_mock_projects():
    """Generate mock project data."""
    project_types = ["Solar PV", "Onshore Wind", "Offshore Wind", "Battery Storage", "Solar + Storage"]
    locations = [
        ("Texas Wind Farm", "Texas", "USA"),
        ("California Solar", "California", "USA"),
        ("North Sea Wind", "North Sea", "UK"),
        ("Queensland Solar", "Queensland", "Australia"),
        ("Bavaria Wind Park", "Bavaria", "Germany"),
        ("Rajasthan Solar", "Rajasthan", "India"),
        ("Atacama Solar", "Atacama", "Chile"),
        ("Alberta Wind", "Alberta", "Canada"),
        ("Hokkaido Wind", "Hokkaido", "Japan"),
        ("Morocco Solar", "Ouarzazate", "Morocco"),
        ("South Australia Battery", "South Australia", "Australia"),
        ("Nevada Solar Storage", "Nevada", "USA"),
    ]
    statuses = ["Operating", "Under Construction", "Development", "Prospective"]

    projects = []
    for i, (name, location, country) in enumerate(locations):
        project_type = random.choice(project_types)
        if "Battery" in name or "Storage" in name:
            project_type = "Battery Storage" if "Battery" in name else "Solar + Storage"
        elif "Solar" in name:
            project_type = "Solar PV" if "Storage" not in name else "Solar + Storage"
        elif "Wind" in name:
            project_type = random.choice(["Onshore Wind", "Offshore Wind"]) if "Sea" in name else "Onshore Wind"

        capacity = random.uniform(50, 500) if "Offshore" not in project_type else random.uniform(200, 1000)
        if "Battery" in project_type:
            capacity = random.uniform(50, 300)

        start_date = datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1500))
        cod = start_date + timedelta(days=random.randint(365, 730))

        projects.append({
            "name": name,
            "project_type": project_type,
            "location": location,
            "country": country,
            "capacity_mw": round(capacity, 1),
            "status": random.choice(statuses),
            "start_date": start_date.strftime("%Y-%m-%d"),
            "commercial_operation_date": cod.strftime("%Y-%m-%d"),
            "project_life_years": 25 if "Battery" not in project_type else 15
        })

    return projects


def generate_financial_assumptions(project_id, project_type, capacity):
    """Generate financial assumptions based on project type."""
    assumptions = {
        "Solar PV": {
            "capex_per_mw": random.uniform(700000, 900000),
            "opex_per_mw_year": random.uniform(8000, 12000),
            "capacity_factor": random.uniform(0.20, 0.30),
            "electricity_price_mwh": random.uniform(40, 70),
        },
        "Onshore Wind": {
            "capex_per_mw": random.uniform(1100000, 1400000),
            "opex_per_mw_year": random.uniform(25000, 35000),
            "capacity_factor": random.uniform(0.30, 0.45),
            "electricity_price_mwh": random.uniform(35, 60),
        },
        "Offshore Wind": {
            "capex_per_mw": random.uniform(2500000, 4000000),
            "opex_per_mw_year": random.uniform(80000, 120000),
            "capacity_factor": random.uniform(0.40, 0.55),
            "electricity_price_mwh": random.uniform(60, 100),
        },
        "Battery Storage": {
            "capex_per_mw": random.uniform(300000, 500000),
            "opex_per_mw_year": random.uniform(5000, 10000),
            "capacity_factor": random.uniform(0.15, 0.30),
            "electricity_price_mwh": random.uniform(80, 150),
        },
        "Solar + Storage": {
            "capex_per_mw": random.uniform(900000, 1200000),
            "opex_per_mw_year": random.uniform(12000, 18000),
            "capacity_factor": random.uniform(0.25, 0.35),
            "electricity_price_mwh": random.uniform(50, 80),
        },
    }

    base = assumptions.get(project_type, assumptions["Solar PV"])

    return {
        "project_id": project_id,
        "capex_per_mw": round(base["capex_per_mw"], 0),
        "opex_per_mw_year": round(base["opex_per_mw_year"], 0),
        "capacity_factor": round(base["capacity_factor"], 3),
        "degradation_rate": 0.005 if "Battery" not in project_type else 0.02,
        "electricity_price_mwh": round(base["electricity_price_mwh"], 2),
        "price_escalation_rate": random.uniform(0.015, 0.025),
        "discount_rate": random.uniform(0.06, 0.10),
        "debt_ratio": random.uniform(0.60, 0.80),
        "interest_rate": random.uniform(0.04, 0.07),
        "loan_tenor_years": 15 if "Battery" not in project_type else 10,
        "tax_rate": random.uniform(0.20, 0.30),
        "depreciation_years": 20 if "Battery" not in project_type else 10,
    }


def calculate_cash_flows(project_id, capacity, assumptions, project_life):
    """Calculate annual cash flows for a project."""
    capex = assumptions["capex_per_mw"] * capacity
    annual_generation_base = capacity * assumptions["capacity_factor"] * 8760  # MWh

    cash_flows = []
    cumulative = -capex * (1 - assumptions["debt_ratio"])  # Initial equity investment
    debt_balance = capex * assumptions["debt_ratio"]
    annual_depreciation = capex / assumptions["depreciation_years"]

    for year in range(1, project_life + 1):
        # Apply degradation
        degradation_factor = (1 - assumptions["degradation_rate"]) ** (year - 1)
        annual_generation = annual_generation_base * degradation_factor

        # Apply price escalation
        price = assumptions["electricity_price_mwh"] * (1 + assumptions["price_escalation_rate"]) ** (year - 1)

        revenue = annual_generation * price
        opex = assumptions["opex_per_mw_year"] * capacity * (1 + 0.02) ** (year - 1)
        ebitda = revenue - opex

        depreciation = annual_depreciation if year <= assumptions["depreciation_years"] else 0

        # Debt service
        if year <= assumptions["loan_tenor_years"] and debt_balance > 0:
            interest = debt_balance * assumptions["interest_rate"]
            principal = debt_balance / (assumptions["loan_tenor_years"] - year + 1)
            debt_balance -= principal
        else:
            interest = 0
            principal = 0

        ebt = ebitda - depreciation - interest
        tax = max(0, ebt * assumptions["tax_rate"])
        net_income = ebt - tax

        fcf = ebitda - interest - principal - tax
        cumulative += fcf

        cash_flows.append({
            "project_id": project_id,
            "year": year,
            "revenue": round(revenue, 0),
            "opex": round(opex, 0),
            "ebitda": round(ebitda, 0),
            "depreciation": round(depreciation, 0),
            "interest_expense": round(interest, 0),
            "principal_repayment": round(principal, 0),
            "tax": round(tax, 0),
            "net_income": round(net_income, 0),
            "free_cash_flow": round(fcf, 0),
            "cumulative_cash_flow": round(cumulative, 0),
        })

    return cash_flows


def calculate_metrics(project_id, capacity, assumptions, cash_flows, project_life):
    """Calculate key financial metrics."""
    capex = assumptions["capex_per_mw"] * capacity
    equity = capex * (1 - assumptions["debt_ratio"])

    # NPV calculation
    npv = -equity
    for cf in cash_flows:
        npv += cf["free_cash_flow"] / (1 + assumptions["discount_rate"]) ** cf["year"]

    # IRR approximation (simplified)
    irr = 0.08 + random.uniform(-0.03, 0.05)

    # Payback period
    payback = project_life
    for cf in cash_flows:
        if cf["cumulative_cash_flow"] >= 0:
            payback = cf["year"]
            break

    # LCOE calculation
    total_generation = sum(
        capacity * assumptions["capacity_factor"] * 8760 * (1 - assumptions["degradation_rate"]) ** (y - 1)
        for y in range(1, project_life + 1)
    )
    total_costs = capex + sum(cf["opex"] for cf in cash_flows)
    lcoe = total_costs / total_generation

    # DSCR
    dscr_values = []
    for cf in cash_flows:
        debt_service = cf["interest_expense"] + cf["principal_repayment"]
        if debt_service > 0:
            dscr_values.append(cf["ebitda"] / debt_service)

    dscr_min = min(dscr_values) if dscr_values else 0
    dscr_avg = sum(dscr_values) / len(dscr_values) if dscr_values else 0

    # Carbon offset (assuming ~0.4 tonnes CO2 per MWh displaced)
    carbon_offset = total_generation * 0.4 / 1000  # Convert to thousands of tonnes

    return {
        "project_id": project_id,
        "total_capex": round(capex, 0),
        "npv": round(npv, 0),
        "irr": round(irr, 4),
        "payback_period_years": round(payback, 1),
        "lcoe": round(lcoe, 2),
        "dscr_min": round(dscr_min, 2),
        "dscr_avg": round(dscr_avg, 2),
        "equity_irr": round(irr * 1.2, 4),
        "total_generation_gwh": round(total_generation / 1000, 1),
        "carbon_offset_tonnes": round(carbon_offset * 1000, 0),
    }


def generate_monthly_generation(project_id, capacity, capacity_factor, years=5):
    """Generate monthly generation data."""
    # Seasonal patterns (Northern Hemisphere assumptions)
    solar_pattern = [0.6, 0.7, 0.9, 1.0, 1.1, 1.2, 1.2, 1.1, 1.0, 0.8, 0.6, 0.5]
    wind_pattern = [1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]

    data = []
    for year in range(1, years + 1):
        for month in range(1, 13):
            # Random pattern selection
            pattern = random.choice([solar_pattern, wind_pattern])
            seasonal_factor = pattern[month - 1]

            monthly_hours = 730  # Average hours per month
            base_generation = capacity * capacity_factor * monthly_hours * seasonal_factor
            actual_generation = base_generation * random.uniform(0.85, 1.15)

            availability = random.uniform(0.95, 0.99)
            actual_cf = actual_generation / (capacity * monthly_hours)
            curtailment = random.uniform(0, base_generation * 0.05)

            data.append({
                "project_id": project_id,
                "year": 2020 + year,
                "month": month,
                "generation_mwh": round(actual_generation, 1),
                "capacity_factor": round(actual_cf, 3),
                "availability": round(availability, 3),
                "curtailment_mwh": round(curtailment, 1),
            })

    return data


def generate_market_data():
    """Generate historical market price data."""
    regions = ["ERCOT", "CAISO", "PJM", "MISO", "UK", "Germany", "Australia"]
    data = []

    start_date = datetime(2020, 1, 1)
    for i in range(1460):  # 4 years of daily data
        date = start_date + timedelta(days=i)
        for region in regions:
            base_price = {"ERCOT": 35, "CAISO": 45, "PJM": 40, "MISO": 35, "UK": 60, "Germany": 55, "Australia": 50}

            # Seasonal and random variation
            seasonal = 1 + 0.2 * (abs(6 - date.month) / 6)
            wholesale = base_price[region] * seasonal * random.uniform(0.7, 1.5)
            ppa = base_price[region] * random.uniform(0.8, 1.0)
            rec = random.uniform(5, 25)
            carbon = random.uniform(20, 80)

            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "region": region,
                "wholesale_price_mwh": round(wholesale, 2),
                "ppa_price_mwh": round(ppa, 2),
                "rec_price": round(rec, 2),
                "carbon_price": round(carbon, 2),
            })

    return data


def generate_technology_benchmarks():
    """Generate technology benchmark data."""
    technologies = {
        "Solar PV": {"capex": 1200000, "cf": 0.20, "lcoe": 45, "lr": 0.20},
        "Onshore Wind": {"capex": 1500000, "cf": 0.35, "lcoe": 40, "lr": 0.15},
        "Offshore Wind": {"capex": 4500000, "cf": 0.45, "lcoe": 80, "lr": 0.10},
        "Battery Storage": {"capex": 600000, "cf": 0.20, "lcoe": 150, "lr": 0.18},
    }

    data = []
    for year in range(2018, 2027):
        for tech, base in technologies.items():
            # Apply learning curve
            years_since_base = year - 2018
            cost_reduction = (1 - base["lr"]) ** (years_since_base / 5)

            data.append({
                "technology": tech,
                "year": year,
                "avg_capex_per_mw": round(base["capex"] * cost_reduction, 0),
                "avg_capacity_factor": round(base["cf"] * (1 + 0.01 * years_since_base), 3),
                "avg_lcoe": round(base["lcoe"] * cost_reduction, 2),
                "learning_rate": base["lr"],
            })

    return data


def insert_data(conn, table, data):
    """Insert data into a table."""
    if not data:
        return

    cursor = conn.cursor()
    columns = ", ".join(data[0].keys())
    placeholders = ", ".join(["?" for _ in data[0]])

    for row in data:
        cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", list(row.values()))

    conn.commit()


def main():
    """Main function to initialize and populate the database."""
    print("Initializing Renewable Energy Financial Database...")

    # Remove existing database
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = create_connection()

    # Create tables
    print("Creating tables...")
    create_tables(conn)

    # Generate and insert projects
    print("Generating projects...")
    projects = generate_mock_projects()
    for project in projects:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO projects (name, project_type, location, country, capacity_mw, status,
                                  start_date, commercial_operation_date, project_life_years)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (project["name"], project["project_type"], project["location"], project["country"],
              project["capacity_mw"], project["status"], project["start_date"],
              project["commercial_operation_date"], project["project_life_years"]))
        project_id = cursor.lastrowid

        # Generate financial assumptions
        assumptions = generate_financial_assumptions(project_id, project["project_type"], project["capacity_mw"])
        insert_data(conn, "financial_assumptions", [assumptions])

        # Generate cash flows
        cash_flows = calculate_cash_flows(project_id, project["capacity_mw"], assumptions, project["project_life_years"])
        insert_data(conn, "annual_cash_flows", cash_flows)

        # Calculate metrics
        metrics = calculate_metrics(project_id, project["capacity_mw"], assumptions, cash_flows, project["project_life_years"])
        insert_data(conn, "key_metrics", [metrics])

        # Generate monthly generation
        monthly_data = generate_monthly_generation(project_id, project["capacity_mw"], assumptions["capacity_factor"])
        insert_data(conn, "monthly_generation", monthly_data)

    conn.commit()

    # Generate market data
    print("Generating market data...")
    market_data = generate_market_data()
    insert_data(conn, "market_data", market_data)

    # Generate technology benchmarks
    print("Generating technology benchmarks...")
    benchmarks = generate_technology_benchmarks()
    insert_data(conn, "technology_benchmarks", benchmarks)

    conn.close()
    print(f"Database initialized successfully at: {DB_PATH}")
    print("Total projects created:", len(projects))


if __name__ == "__main__":
    main()
