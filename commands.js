/*
 * Copyright (c) Project Setup Tools. All rights reserved.
 * Licensed under the MIT license.
 */

/* global Excel, Office */

// Import config from relative path (will be bundled)
const config = {
  ANALYTICS_URL: "https://claudecode-yuyingcrexcelribbon.streamlit.app"
};

Office.onReady(() => {
  // Office is ready
});

/**
 * Run the project setup automation
 * This function is called directly from the ribbon button
 */
async function runSetup(event) {
  try {
    await Excel.run(async (context) => {
      const workbook = context.workbook;
      const activeSheet = workbook.worksheets.getActiveWorksheet();
      activeSheet.load("name");

      await context.sync();

      // Perform setup operations
      const range = activeSheet.getRange("A1");
      range.values = [[`Setup run at: ${new Date().toISOString()}`]];
      range.format.autofitColumns();

      await context.sync();

      showNotification("Setup Complete", "Project setup has been run successfully.");
    });
  } catch (error) {
    showNotification("Error", `Setup failed: ${error}`);
  }

  // Signal that the function is complete
  event.completed();
}

/**
 * Validate data in the workbook
 * This function is called directly from the ribbon button
 */
async function validateData(event) {
  try {
    await Excel.run(async (context) => {
      const workbook = context.workbook;
      const activeSheet = workbook.worksheets.getActiveWorksheet();
      const usedRange = activeSheet.getUsedRange();

      usedRange.load("values, rowCount, columnCount, address");
      await context.sync();

      let emptyCount = 0;
      const values = usedRange.values;

      for (let row = 0; row < values.length; row++) {
        for (let col = 0; col < values[row].length; col++) {
          if (values[row][col] === "" || values[row][col] === null) {
            emptyCount++;
          }
        }
      }

      if (emptyCount === 0) {
        showNotification("Validation Passed", "No empty cells found in the used range.");
      } else {
        showNotification(
          "Validation Warning",
          `Found ${emptyCount} empty cell(s) in range ${usedRange.address}`
        );
      }
    });
  } catch (error) {
    showNotification("Error", `Validation failed: ${error}`);
  }

  // Signal that the function is complete
  event.completed();
}

/**
 * Open the Analytics Dashboard
 * This function opens the Streamlit analytics dashboard in a new browser window
 */
async function openAnalytics(event) {
  try {
    // Open the analytics dashboard in a new browser window
    window.open(config.ANALYTICS_URL, "_blank", "noopener,noreferrer");

    showNotification("Analytics", "Opening Renewable Energy Analytics Dashboard...");
  } catch (error) {
    showNotification("Error", `Failed to open analytics: ${error}`);
  }

  // Signal that the function is complete
  event.completed();
}

/**
 * Show a notification to the user
 */
function showNotification(title, message) {
  // Use Office notification API if available
  if (Office.context.ui && typeof Office.context.ui.displayDialogAsync === "function") {
    // For more complex notifications, you could open a dialog
    console.log(`${title}: ${message}`);
  }

  // Also log to console
  console.log(`Notification - ${title}: ${message}`);
}

// Register functions with Office
Office.actions.associate("runSetup", runSetup);
Office.actions.associate("validateData", validateData);
Office.actions.associate("openAnalytics", openAnalytics);