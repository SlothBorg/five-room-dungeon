const statusEl = document.getElementById("status");
const generateBtn = document.getElementById("generate-btn");
const countInput = document.getElementById("count-input");
const imageEl = document.getElementById("dungeon-image");
const tableEl = document.getElementById("rooms-table");
const downloadPngBtn = document.getElementById("download-png");
const downloadMdBtn = document.getElementById("download-md");

let lastResult = null;

function setStatus(text) {
  statusEl.textContent = text;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function roomsMarkdownToTable(markdown) {
  const rows = markdown
    .trim()
    .split("\n")
    .filter((line) => line.startsWith("|"))
    .slice(2); // drop header + separator row, we render our own <thead>

  const body = rows
    .map((row) => {
      const cells = row
        .split("|")
        .slice(1, -1)
        .map((cell) => `<td>${escapeHtml(cell.trim())}</td>`)
        .join("");
      return `<tr>${cells}</tr>`;
    })
    .join("");

  return `<table><thead><tr><th>Room</th><th>Role</th><th>Connects To</th></tr></thead><tbody>${body}</tbody></table>`;
}

async function initPyodide() {
  setStatus("Loading Python runtime (this can take a few seconds)…");
  const pyodide = await loadPyodide();

  setStatus("Installing networkx and matplotlib…");
  await pyodide.loadPackage(["networkx", "matplotlib"]);

  setStatus("Loading dungeon generator…");
  const [mainSrc, appSrc] = await Promise.all([
    fetch("main.py").then((r) => r.text()),
    fetch("pyodide_app.py").then((r) => r.text()),
  ]);
  pyodide.FS.writeFile("main.py", mainSrc);
  pyodide.FS.writeFile("pyodide_app.py", appSrc);
  pyodide.runPython(appSrc);

  setStatus("Ready.");
  generateBtn.disabled = false;
  return pyodide;
}

const pyodideReadyPromise = initPyodide().catch((err) => {
  console.error(err);
  setStatus("Failed to load the Python runtime. See console for details.");
  throw err;
});

async function generate() {
  const n = parseInt(countInput.value, 10);
  if (!Number.isInteger(n) || n < 1) {
    setStatus("Please enter a positive integer.");
    return;
  }

  generateBtn.disabled = true;
  setStatus("Generating…");

  try {
    const pyodide = await pyodideReadyPromise;
    const resultJson = await pyodide.runPythonAsync(`generate_dungeon(${n})`);
    const result = JSON.parse(resultJson);
    lastResult = result;

    imageEl.src = `data:image/png;base64,${result.png_base64}`;
    imageEl.hidden = false;
    tableEl.innerHTML = roomsMarkdownToTable(result.markdown);

    setStatus(
      `Generated ${result.module_count} module(s), ${result.room_count} rooms, ` +
        `${result.edge_count} connections.`
    );
    downloadPngBtn.disabled = false;
    downloadMdBtn.disabled = false;
  } catch (err) {
    console.error(err);
    setStatus("Something went wrong generating the dungeon. See console for details.");
  } finally {
    generateBtn.disabled = false;
  }
}

function downloadPng() {
  if (!lastResult) return;
  const a = document.createElement("a");
  a.href = `data:image/png;base64,${lastResult.png_base64}`;
  a.download = "dungeon_graph.png";
  a.click();
}

function downloadMd() {
  if (!lastResult) return;
  const blob = new Blob([lastResult.markdown], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "dungeon_rooms.md";
  a.click();
  URL.revokeObjectURL(url);
}

generateBtn.addEventListener("click", generate);
downloadPngBtn.addEventListener("click", downloadPng);
downloadMdBtn.addEventListener("click", downloadMd);