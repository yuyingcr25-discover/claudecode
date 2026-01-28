# Excel Ribbon Add-in Setup Instructions

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Node.js** (version 16 or higher) - Download from https://nodejs.org/
2. **Python 3** (version 3.8 or higher) - Download from https://python.org/
3. **Microsoft Excel** (Desktop version - Windows or Mac)

## Setup Steps

### 1. Extract the ZIP file
Extract all files to a folder on your computer (e.g., `C:\Projects\excel-addon`)

### 2. Install Node.js Dependencies

Open Command Prompt or Terminal and navigate to the project folder:

```bash
cd path\to\excel-addon
npm install
```

This will install all required Node.js packages (may take a few minutes).

### 3. Install Python Dependencies

Navigate to the analytics folder:

```bash
cd analytics
pip install -r requirements.txt
```

### 4. Initialize the Database

Still in the analytics folder, run:

```bash
python init_database.py
```

This creates a SQLite database with sample renewable energy project data.

## Running the Application

You need to run TWO servers simultaneously:

### Terminal 1: Excel Add-in Development Server

```bash
cd path\to\excel-addon
npm run dev-server
```

You should see: `webpack compiled successfully`
The add-in will be available at: https://localhost:3000

### Terminal 2: Analytics Dashboard

```bash
cd path\to\excel-addon\analytics
streamlit run app.py --server.port 8501 --server.headless true --browser.gatherUsageStats false
```

You should see: `You can now view your Streamlit app in your browser`
The dashboard will be available at: http://localhost:8501

## Loading the Add-in in Excel

### Option 1: Automatic (Easiest)

Open a third terminal:

```bash
cd path\to\excel-addon
npm start
```

This will automatically open Excel with the add-in loaded.

### Option 2: Manual Sideloading

1. Open Excel
2. Go to **Insert** tab → **Add-ins** → **Get Add-ins**
3. Click **Upload My Add-in** (bottom right corner)
4. Browse and select: `path\to\excel-addon\manifest.xml`
5. Click **Upload**

### Option 3: Shared Folder (Enterprise/Network)

If your IT allows, you can place the manifest.xml in a network shared folder:

1. Copy `manifest.xml` to a shared network folder
2. In Excel: **File** → **Options** → **Trust Center** → **Trust Center Settings**
3. **Trusted Add-in Catalogs** → Add the network folder path
4. Restart Excel and go to **Insert** → **My Add-ins** → **Shared Folder**

## Using the Add-in

Once loaded, you'll see a **"Project Setup"** tab in the Excel ribbon with 4 buttons:

1. **Open Panel** - Opens the taskpane sidebar with interactive tools
2. **Run Setup** - Writes a timestamp to cell A1 (demo automation)
3. **Validate Data** - Scans the active sheet for empty cells
4. **Analytics** - Opens the Streamlit dashboard at http://localhost:8501

### Taskpane Features

The taskpane includes:
- **Run Setup** button
- **Validate Data** button
- **Export Data** button - Exports sheet data as JSON
- **Refresh** button - Reloads worksheet list
- **Worksheet Browser** - Shows all sheets in the workbook
- **Results Display** - Shows validation issues and exported data

## Troubleshooting

### "Add-in won't load" or "Manifest error"
- Ensure both servers are running (npm run dev-server and streamlit)
- Check that ports 3000 and 8501 are not blocked by firewall
- Clear Office cache: Delete folder `%LOCALAPPDATA%\Microsoft\Office\16.0\Wef\`

### "SSL Certificate Error"
- The dev server creates a self-signed certificate
- You may need to accept the security warning in your browser
- Navigate to https://localhost:3000 and accept the certificate

### "Analytics button does nothing"
- Ensure the Streamlit dashboard is running on port 8501
- Check if http://localhost:8501 opens in your browser manually

### Node/npm errors
- Make sure Node.js version is 16 or higher: `node --version`
- Try deleting `node_modules` folder and running `npm install` again

### Python errors
- Make sure Python 3 is installed: `python --version`
- Try using `pip3` instead of `pip` if on Mac/Linux
- On Windows, ensure Python was added to PATH during installation

## Development Notes

- The add-in runs on **https://localhost:3000** (HTTPS required by Office)
- The analytics dashboard runs on **http://localhost:8501**
- Hot reload is enabled - changes to code will auto-refresh
- All data in the analytics dashboard is mock/sample data

## Stopping the Servers

Press `Ctrl+C` in each terminal window to stop the servers.

To unload the add-in from Excel: **Insert** → **My Add-ins** → Click the three dots next to "Project Setup Tools" → **Remove**

## Support

For issues or questions, refer to:
- Office Add-ins documentation: https://learn.microsoft.com/en-us/office/dev/add-ins/
- Streamlit documentation: https://docs.streamlit.io/
