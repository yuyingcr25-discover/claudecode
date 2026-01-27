/*
 * Copyright (c) Project Setup Tools. All rights reserved.
 * Licensed under the MIT license.
 */

/* global Excel */

/**
 * Helper functions for Excel operations
 */

/**
 * Get the names of all worksheets in the workbook
 */
export async function getWorksheetNames(): Promise<string[]> {
  return Excel.run(async (context) => {
    const sheets = context.workbook.worksheets;
    sheets.load("items/name");
    await context.sync();
    return sheets.items.map((sheet) => sheet.name);
  });
}

/**
 * Get the active worksheet
 */
export async function getActiveWorksheet(): Promise<Excel.Worksheet> {
  return Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getActiveWorksheet();
    sheet.load("name, id");
    await context.sync();
    return sheet;
  });
}

/**
 * Get data from a specific range
 */
export async function getRangeData(
  sheetName: string,
  rangeAddress: string
): Promise<unknown[][]> {
  return Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getItem(sheetName);
    const range = sheet.getRange(rangeAddress);
    range.load("values");
    await context.sync();
    return range.values;
  });
}

/**
 * Set data to a specific range
 */
export async function setRangeData(
  sheetName: string,
  rangeAddress: string,
  values: unknown[][]
): Promise<void> {
  return Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getItem(sheetName);
    const range = sheet.getRange(rangeAddress);
    range.values = values;
    await context.sync();
  });
}

/**
 * Apply formatting to a range
 */
export async function formatRange(
  sheetName: string,
  rangeAddress: string,
  format: {
    bold?: boolean;
    italic?: boolean;
    fontSize?: number;
    fontColor?: string;
    fillColor?: string;
  }
): Promise<void> {
  return Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getItem(sheetName);
    const range = sheet.getRange(rangeAddress);

    if (format.bold !== undefined) {
      range.format.font.bold = format.bold;
    }
    if (format.italic !== undefined) {
      range.format.font.italic = format.italic;
    }
    if (format.fontSize !== undefined) {
      range.format.font.size = format.fontSize;
    }
    if (format.fontColor !== undefined) {
      range.format.font.color = format.fontColor;
    }
    if (format.fillColor !== undefined) {
      range.format.fill.color = format.fillColor;
    }

    await context.sync();
  });
}

/**
 * Add a new worksheet
 */
export async function addWorksheet(name: string): Promise<void> {
  return Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.add(name);
    sheet.activate();
    await context.sync();
  });
}

/**
 * Delete a worksheet by name
 */
export async function deleteWorksheet(name: string): Promise<void> {
  return Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getItem(name);
    sheet.delete();
    await context.sync();
  });
}

/**
 * Create a table from a range
 */
export async function createTable(
  sheetName: string,
  rangeAddress: string,
  tableName: string,
  hasHeaders: boolean = true
): Promise<void> {
  return Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getItem(sheetName);
    const table = sheet.tables.add(rangeAddress, hasHeaders);
    table.name = tableName;
    await context.sync();
  });
}

/**
 * Get all tables in the workbook
 */
export async function getAllTables(): Promise<{ sheetName: string; tableName: string }[]> {
  return Excel.run(async (context) => {
    const sheets = context.workbook.worksheets;
    sheets.load("items");
    await context.sync();

    const tables: { sheetName: string; tableName: string }[] = [];

    for (const sheet of sheets.items) {
      const sheetTables = sheet.tables;
      sheetTables.load("items/name");
      await context.sync();

      for (const table of sheetTables.items) {
        tables.push({ sheetName: sheet.name, tableName: table.name });
      }
    }

    return tables;
  });
}
