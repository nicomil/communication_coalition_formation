import fs from "node:fs/promises";
import path from "node:path";
import { Workbook } from "@oai/artifact-tool";

const [csvPath, previewDir] = process.argv.slice(2);
if (!csvPath || !previewDir) {
  throw new Error("Usage: node verify_directional_csv_artifact.mjs CSV_PATH PREVIEW_DIR");
}

const csvText = await fs.readFile(csvPath, "utf8");
const workbook = await Workbook.fromCSV(csvText, { sheetName: "Data" });
const overview = await workbook.inspect({
  kind: "workbook,sheet,region",
  sheetId: "Data",
  range: "A1:L8",
  maxChars: 5000,
  tableMaxRows: 8,
  tableMaxCols: 12,
  tableMaxCellChars: 80,
});
const directional = await workbook.inspect({
  kind: "region",
  sheetId: "Data",
  range: "CX114:DF127",
  maxChars: 10000,
  tableMaxRows: 20,
  tableMaxCols: 10,
  tableMaxCellChars: 220,
});

await fs.mkdir(previewDir, { recursive: true });
for (const [name, range] of [
  ["identity_preview.png", "A114:L127"],
  ["directional_chat_preview.png", "CX114:DF127"],
]) {
  const preview = await workbook.render({
    sheetName: "Data",
    range,
    scale: 1,
    format: "png",
  });
  await fs.writeFile(
    path.join(previewDir, name),
    new Uint8Array(await preview.arrayBuffer()),
  );
}

console.log(JSON.stringify({
  overview: overview.ndjson,
  directional: directional.ndjson,
  rendered_previews: 2,
}, null, 2));
