#!/bin/bash
# Start the Renewable Energy Analytics Dashboard

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if database exists, if not initialize it
if [ ! -f "$SCRIPT_DIR/renewable_energy.db" ]; then
    echo "Initializing database with mock data..."
    python "$SCRIPT_DIR/init_database.py"
fi

# Start Streamlit
echo "Starting Renewable Energy Analytics Dashboard..."
echo "Dashboard will be available at: http://localhost:8501"
streamlit run "$SCRIPT_DIR/app.py" --server.port 8501
