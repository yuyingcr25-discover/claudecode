/*
 * Project Setup Tools - Taskpane JavaScript
 */

/* global Office, Excel */

Office.onReady((info) => {
  if (info.host === Office.HostType.Excel) {
    document.getElementById("status-message").textContent = "Workbook loaded successfully";
    
    // Add event listeners for buttons
    document.getElementById("run-setup-btn")?.addEventListener("click", runSetup);
    document.getElementById("validate-btn")?.addEventListener("click", validateData);
    document.getElementById("export-btn")?.addEventListener("click", exportData);
    document.getElementById("refresh-btn")?.addEventListener("click", refreshSheets);
    
    // Load initial data
    refreshSheets();
  }
});

function runSetup() {
  // This will be handled by ribbon button
  console.log("Run Setup clicked");
}

function validateData() {
  // This will be handled by ribbon button  
  console.log("Validate Data clicked");
}

function exportData() {
  console.log("Export Data clicked");
}

function refreshSheets() {
  Excel.run(async (context) => {
    const worksheets = context.workbook.worksheets;
    worksheets.load("items/name");
    await context.sync();
    
    const sheetList = document.getElementById("sheet-list");
    sheetList.innerHTML = "";
    
    worksheets.items.forEach((sheet, index) => {
      const li = document.createElement("li");
      li.className = "sheet-item";
      li.textContent = sheet.name;
      sheetList.appendChild(li);
    });
  }).catch((error) => {
    console.error("Error refreshing sheets:", error);
  });
}