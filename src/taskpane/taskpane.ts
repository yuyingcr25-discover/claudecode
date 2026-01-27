/*
 * Copyright (c) Project Setup Tools. All rights reserved.
 * Licensed under the MIT license.
 */

/* global Excel, Office */

Office.onReady((info) => {
  if (info.host === Office.HostType.Excel) {
    initializeTaskpane();
  }
});

/**
 * Initialize the taskpane UI and event handlers
 */
function initializeTaskpane(): void {
  // Set up button click handlers
  const runSetupBtn = document.getElementById("run-setup-btn");
  const validateBtn = document.getElementById("validate-btn");
  const exportBtn = document.getElementById("export-btn");
  const refreshBtn = document.getElementById("refresh-btn");

  if (runSetupBtn) {
    runSetupBtn.addEventListener("click", handleRunSetup);
  }

  if (validateBtn) {
    validateBtn.addEventListener("click", handleValidateData);
  }

  if (exportBtn) {
    exportBtn.addEventListener("click", handleExport);
  }

  if (refreshBtn) {
    refreshBtn.addEventListener("click", handleRefresh);
  }

  // Load initial workbook info
  loadWorkbookInfo();

  console.log("Project Setup Tools taskpane initialized");
}

/**
 * Load and display workbook information
 */
async function loadWorkbookInfo(): Promise<void> {
  try {
    await Excel.run(async (context) => {
      const workbook = context.workbook;
      const sheets = workbook.worksheets;
      sheets.load("items/name");

      await context.sync();

      const sheetList = document.getElementById("sheet-list");
      if (sheetList) {
        sheetList.innerHTML = "";
        sheets.items.forEach((sheet) => {
          const li = document.createElement("li");
          li.textContent = sheet.name;
          li.className = "sheet-item";
          sheetList.appendChild(li);
        });
      }

      updateStatus("Workbook loaded successfully", "success");
    });
  } catch (error) {
    updateStatus(`Error loading workbook: ${error}`, "error");
  }
}

/**
 * Handle the Run Setup button click
 */
async function handleRunSetup(): Promise<void> {
  updateStatus("Running setup...", "info");

  try {
    await Excel.run(async (context) => {
      const workbook = context.workbook;
      const activeSheet = workbook.worksheets.getActiveWorksheet();
      activeSheet.load("name");

      await context.sync();

      // Example: Add a timestamp to indicate setup was run
      const range = activeSheet.getRange("A1");
      range.values = [[`Setup run at: ${new Date().toISOString()}`]];
      range.format.autofitColumns();

      await context.sync();

      updateStatus("Setup completed successfully!", "success");
    });
  } catch (error) {
    updateStatus(`Setup failed: ${error}`, "error");
  }
}

/**
 * Handle the Validate Data button click
 */
async function handleValidateData(): Promise<void> {
  updateStatus("Validating data...", "info");

  try {
    await Excel.run(async (context) => {
      const workbook = context.workbook;
      const activeSheet = workbook.worksheets.getActiveWorksheet();
      const usedRange = activeSheet.getUsedRange();

      usedRange.load("values, rowCount, columnCount");
      await context.sync();

      const issues: string[] = [];

      // Example validation: check for empty cells in used range
      const values = usedRange.values;
      for (let row = 0; row < values.length; row++) {
        for (let col = 0; col < values[row].length; col++) {
          if (values[row][col] === "" || values[row][col] === null) {
            issues.push(`Empty cell at row ${row + 1}, column ${col + 1}`);
          }
        }
      }

      if (issues.length === 0) {
        updateStatus("Validation passed! No issues found.", "success");
      } else {
        updateStatus(`Validation found ${issues.length} issue(s)`, "warning");
        displayValidationResults(issues);
      }
    });
  } catch (error) {
    updateStatus(`Validation failed: ${error}`, "error");
  }
}

/**
 * Handle the Export button click
 */
async function handleExport(): Promise<void> {
  updateStatus("Exporting data...", "info");

  try {
    await Excel.run(async (context) => {
      const workbook = context.workbook;
      const activeSheet = workbook.worksheets.getActiveWorksheet();
      const usedRange = activeSheet.getUsedRange();

      usedRange.load("values");
      await context.sync();

      const data = usedRange.values;

      // Convert to JSON format
      const jsonData = JSON.stringify(data, null, 2);

      // Display in results area (in a real app, you might download this)
      const resultsDiv = document.getElementById("results");
      if (resultsDiv) {
        resultsDiv.innerHTML = `<pre>${jsonData}</pre>`;
      }

      updateStatus("Export completed!", "success");
    });
  } catch (error) {
    updateStatus(`Export failed: ${error}`, "error");
  }
}

/**
 * Handle the Refresh button click
 */
async function handleRefresh(): Promise<void> {
  updateStatus("Refreshing...", "info");
  await loadWorkbookInfo();
}

/**
 * Update the status message in the UI
 */
function updateStatus(message: string, type: "info" | "success" | "warning" | "error"): void {
  const statusEl = document.getElementById("status-message");
  if (statusEl) {
    statusEl.textContent = message;
    statusEl.className = `status-message status-${type}`;
  }
}

/**
 * Display validation results in the UI
 */
function displayValidationResults(issues: string[]): void {
  const resultsDiv = document.getElementById("results");
  if (resultsDiv) {
    resultsDiv.innerHTML = `
      <h4>Validation Issues:</h4>
      <ul class="validation-issues">
        ${issues.slice(0, 10).map((issue) => `<li>${issue}</li>`).join("")}
        ${issues.length > 10 ? `<li>...and ${issues.length - 10} more</li>` : ""}
      </ul>
    `;
  }
}
