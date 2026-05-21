import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const projectRoot = path.resolve("D:/work/codex/超重力混凝土/hypergravity_concrete_scout");
const outputPath = path.join(projectRoot, "reports", "research_results_file_summary.xlsx");
const previewPath = path.join(os.tmpdir(), "research_results_file_summary_preview.png");
const sheetName = "研究结果文件汇总";

const recommended = new Set([
  "final_research_map.md",
  "papers_master.csv",
  "direction_score.csv",
  "reading_list_by_direction.csv",
  "top_cited_papers.csv",
]);

const categoryOrder = {
  "最终报告": 1,
  "核心数据": 2,
  "原始检索": 3,
  "分析报告": 4,
  "统计表": 5,
  "审计文件": 6,
  "图表": 7,
};

const descriptionMap = {
  "final_research_map.md": ["最终报告", "最终综合报告，汇总研究背景、方法、六方向对比、代表论文、研究空白、实验方案和 30 天行动计划。"],
  "papers_master.csv": ["核心数据", "清洗、合并、去重后的论文主数据表，是后续分析和报告的核心依据。"],
  "works_master.csv": ["核心数据", "与 papers_master.csv 内容相同的兼容副本，用于早期脚本兼容。"],
  "direction_score.csv": ["核心数据", "A-F 六个方向的可行性评分表，包含热度、成熟度、创新空间、实验可行性、设备可获得性、相关性和推荐类别。"],
  "direction_scores.csv": ["统计表", "direction_score.csv 的兼容副本。"],
  "reading_list_by_direction.csv": ["核心数据", "A-F 每个方向约 10 篇推荐阅读论文，含相关性理由和对课题启发。"],
  "reading_list.csv": ["核心数据", "reading_list_by_direction.csv 的兼容副本。"],
  "top_cited_papers.csv": ["核心数据", "每个方向 Top 20 高被引论文。"],
  "top_cited_works.csv": ["统计表", "早期高被引论文兼容输出，记录较少，不建议作为主依据。"],
  "openalex_results.csv": ["原始检索", "OpenAlex 检索得到的原始题录结果。"],
  "semantic_scholar_results.csv": ["原始检索", "Semantic Scholar 检索得到的原始题录结果。"],
  "crossref_results.jsonl": ["原始检索", "Crossref 原始结果文件；当前为空时表示本轮未形成有效 Crossref 原始记录。"],
  "semantic_scholar_results.jsonl": ["原始检索", "Semantic Scholar JSONL 原始结果预留文件；当前为空。"],
  "cleaning_report.md": ["分析报告", "清洗报告，说明原始记录数、去重后记录数、方向分布、数据库贡献、缺失 DOI 和摘要比例。"],
  "landscape_summary.md": ["分析报告", "文献景观总结，包含六个方向的论文数量、2015-2026 趋势、代表期刊、代表作者、高被引论文和活跃度判断。"],
  "landscape_report.md": ["分析报告", "landscape_summary.md 的兼容输出。"],
  "reading_list_by_direction.md": ["分析报告", "分方向推荐阅读清单报告，含年份、引用、作者、来源、DOI/URL、相关性和课题启发。"],
  "reading_list.md": ["分析报告", "reading_list_by_direction.md 的兼容输出。"],
  "direction_score_report.md": ["分析报告", "方向可行性评分报告，解释 A-F 六个方向的分数、主要风险和主攻/备用/暂缓排序。"],
  "direction_scores.md": ["分析报告", "direction_score_report.md 的兼容输出。"],
  "direction_summary.csv": ["统计表", "每个方向的论文数量、近年数量、引用等聚合统计。"],
  "yearly_counts.csv": ["统计表", "A-F 六个方向按年份统计的发文数量。"],
  "author_summary.csv": ["统计表", "各方向代表作者或高频作者统计。"],
  "venue_summary.csv": ["统计表", "各方向代表期刊或会议统计。"],
  "direction_overlap.csv": ["统计表", "A-F 方向之间的题录交叉和重叠关系统计。"],
  "uncertainty_log.csv": ["审计文件", "清洗和字段缺失过程中记录的不确定项，例如缺 DOI、缺摘要等。"],
  "openalex_audit.csv": ["审计文件", "OpenAlex 每个查询的请求审计记录。"],
  "openalex_query_plan.csv": ["审计文件", "OpenAlex 按方向和关键词生成的查询计划。"],
  "semantic_scholar_audit.csv": ["审计文件", "Semantic Scholar 每个查询的请求审计和状态记录。"],
  "semantic_scholar_query_plan.csv": ["审计文件", "Semantic Scholar 按方向和关键词生成的查询计划。"],
  "crossref_audit.csv": ["审计文件", "Crossref 请求审计文件；为空或近空时表示 Crossref 补充数据不足。"],
  "crossref_query_plan.csv": ["审计文件", "Crossref 按方向和关键词生成的查询计划。"],
  "direction_paper_count.png": ["图表", "每个方向论文数量柱状图。"],
  "year_trend_by_direction.png": ["图表", "2015-2026 年各方向发文趋势折线图。"],
  "yearly_trend.png": ["图表", "年度趋势图兼容副本。"],
  "top_venues_by_direction.png": ["图表", "各方向代表期刊或会议图。"],
  "top_venues.png": ["图表", "代表期刊图兼容副本。"],
  "direction_overlap.png": ["图表", "A-F 方向交叉或重叠关系图。"],
};

function defaultDescription(fileName, relativePath) {
  if (relativePath.startsWith("data/raw/")) return ["原始检索", "原始检索结果或预留文件。"];
  if (relativePath.startsWith("data/processed/")) return ["统计表", "处理后的统计或中间结果文件。"];
  if (relativePath.startsWith("reports/")) return ["分析报告", "Markdown 分析报告。"];
  if (relativePath.startsWith("figures/")) return ["图表", "分析图表。"];
  return ["统计表", "研究结果文件。"];
}

async function countTextLines(filePath) {
  const text = await fs.readFile(filePath, "utf8");
  if (text.trim() === "") return 0;
  return text.split(/\r\n|\n|\r/).length;
}

async function csvDataRows(filePath) {
  const text = await fs.readFile(filePath, "utf8");
  if (text.trim() === "") return 0;
  const lines = text.split(/\r\n|\n|\r/).filter((line) => line.trim() !== "");
  return Math.max(0, lines.length - 1);
}

async function scaleStatus(filePath, extension) {
  if (extension === ".csv") {
    const rows = await csvDataRows(filePath);
    if (rows === 0) return "空 CSV 或无有效数据行";
    return `${rows} 条`;
  }
  if (extension === ".md") {
    const lines = await countTextLines(filePath);
    return `${lines} 行 Markdown 报告`;
  }
  if (extension === ".jsonl") {
    const lines = await countTextLines(filePath);
    if (lines === 0) return "空文件（0 行）";
    return `${lines} 行 JSONL`;
  }
  if (extension === ".png") return "PNG 图表";
  if (extension === ".xlsx") return "Excel 工作簿";
  return "文件";
}

async function collectRows() {
  const folders = ["data/raw", "data/processed", "reports", "figures"];
  const rows = [];
  for (const folder of folders) {
    const folderPath = path.join(projectRoot, folder);
    const entries = await fs.readdir(folderPath, { withFileTypes: true });
    for (const entry of entries) {
      if (!entry.isFile() || entry.name === ".gitkeep") continue;
      const filePath = path.join(folderPath, entry.name);
      if (path.resolve(filePath) === path.resolve(outputPath)) continue;
      if (entry.name === "research_results_file_summary_preview.png") continue;
      const relativePath = path.relative(projectRoot, filePath).replaceAll("\\", "/");
      const extension = path.extname(entry.name).toLowerCase();
      const [category, description] = descriptionMap[entry.name] ?? defaultDescription(entry.name, relativePath);
      rows.push({
        category,
        fileName: entry.name,
        description,
        status: await scaleStatus(filePath, extension),
        localPath: filePath,
        recommended: recommended.has(entry.name) ? "是" : "否",
      });
    }
  }
  rows.sort((a, b) => {
    const categoryDiff = (categoryOrder[a.category] ?? 99) - (categoryOrder[b.category] ?? 99);
    if (categoryDiff !== 0) return categoryDiff;
    if (a.recommended !== b.recommended) return a.recommended === "是" ? -1 : 1;
    return a.fileName.localeCompare(b.fileName, "zh-Hans-CN");
  });
  return rows;
}

function setColumnWidths(sheet) {
  const widths = [110, 230, 520, 150, 760, 130];
  widths.forEach((width, index) => {
    const range = sheet.getRangeByIndexes(0, index, 200, 1);
    range.format.columnWidthPx = width;
  });
}

async function main() {
  const rows = await collectRows();
  const workbook = Workbook.create();
  const sheet = workbook.worksheets.add(sheetName);
  sheet.showGridLines = false;

  const header = [["类别", "文件名", "内容说明", "规模/状态", "本地地址", "是否主推荐查看"]];
  const body = rows.map((row) => [row.category, row.fileName, row.description, row.status, row.localPath, row.recommended]);
  const data = [...header, ...body];
  sheet.getRangeByIndexes(0, 0, data.length, header[0].length).values = data;

  const usedRange = sheet.getRangeByIndexes(0, 0, data.length, header[0].length);
  usedRange.format = {
    font: { name: "Microsoft YaHei", size: 10, color: "#111827" },
    wrapText: true,
    verticalAlignment: "top",
  };
  sheet.getRange("A1:F1").format = {
    fill: "#1F4E79",
    font: { name: "Microsoft YaHei", bold: true, color: "#FFFFFF", size: 11 },
    horizontalAlignment: "center",
    verticalAlignment: "middle",
    wrapText: true,
  };
  sheet.getRange("A1:F1").format.rowHeightPx = 32;
  sheet.getRangeByIndexes(1, 0, Math.max(1, data.length - 1), 6).format.rowHeightPx = 54;
  setColumnWidths(sheet);
  sheet.freezePanes.freezeRows(1);

  const tableRange = `A1:F${data.length}`;
  const table = sheet.tables.add(tableRange, true, "ResearchResultsFileSummary");
  table.style = "TableStyleMedium2";
  table.showFilterButton = true;
  table.showBandedRows = true;

  sheet.getRange(`F2:F${data.length}`).conditionalFormats.add("containsText", {
    text: "是",
    format: {
      fill: "#D9EAD3",
      font: { bold: true, color: "#14532D" },
    },
  });
  sheet.getRange(`D2:D${data.length}`).conditionalFormats.add("containsText", {
    text: "空",
    format: {
      fill: "#FCE4D6",
      font: { color: "#9A3412" },
    },
  });

  await workbook.inspect({
    kind: "table",
    range: `${sheetName}!A1:F8`,
    include: "values",
    tableMaxRows: 8,
    tableMaxCols: 6,
    maxChars: 4000,
  });
  await workbook.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
    options: { useRegex: true, maxResults: 50 },
    summary: "final formula error scan",
  });
  const preview = await workbook.render({
    sheetName,
    range: "A1:F18",
    scale: 1,
    format: "png",
  });
  await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));

  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  const xlsx = await SpreadsheetFile.exportXlsx(workbook);
  await xlsx.save(outputPath);
  console.log(JSON.stringify({ outputPath, previewPath, rows: rows.length }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
