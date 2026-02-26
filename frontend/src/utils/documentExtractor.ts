import { extractTextFromPdf } from "./pdfExtractor";

export interface ExtractionResult {
  text: string;
  supported: boolean;
  formatName: string;
}

const PLAIN_TEXT_TYPES = new Set([
  "text/plain",
  "text/markdown",
  "text/csv",
  "text/x-markdown",
]);

const SCAFFOLDED_FORMATS: Record<string, string> = {
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "XLSX",
  "application/vnd.openxmlformats-officedocument.presentationml.presentation": "PPTX",
  "application/rtf": "RTF",
  "application/epub+zip": "EPUB",
  "text/vtt": "VTT",
  "application/x-subrip": "SRT",
};

function getFormatFromExtension(filename: string): string {
  const ext = filename.split(".").pop()?.toLowerCase() ?? "";
  const map: Record<string, string> = {
    pdf: "PDF",
    txt: "TXT",
    md: "Markdown",
    csv: "CSV",
    html: "HTML",
    htm: "HTML",
    docx: "DOCX",
    xlsx: "XLSX",
    pptx: "PPTX",
    rtf: "RTF",
    epub: "EPUB",
    srt: "SRT",
    vtt: "VTT",
  };
  return map[ext] ?? ext.toUpperCase();
}

async function extractPlainText(file: File): Promise<string> {
  return file.text();
}

async function extractHtml(file: File): Promise<string> {
  const html = await file.text();
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, "text/html");
  return doc.body.textContent?.trim() ?? "";
}

export async function extractDocument(file: File): Promise<ExtractionResult> {
  const formatName = getFormatFromExtension(file.name);

  // PDF
  if (file.type === "application/pdf" || file.name.endsWith(".pdf")) {
    const text = await extractTextFromPdf(file);
    return { text, supported: true, formatName };
  }

  // Plain text variants (TXT, MD, CSV)
  if (PLAIN_TEXT_TYPES.has(file.type) || /\.(txt|md|csv)$/i.test(file.name)) {
    const text = await extractPlainText(file);
    return { text, supported: true, formatName };
  }

  // HTML
  if (file.type === "text/html" || /\.html?$/i.test(file.name)) {
    const text = await extractHtml(file);
    return { text, supported: true, formatName };
  }

  // Scaffolded formats (not yet implemented)
  const scaffoldedName = SCAFFOLDED_FORMATS[file.type];
  if (scaffoldedName) {
    return { text: "", supported: false, formatName: scaffoldedName };
  }

  // Check by extension for scaffolded formats
  const ext = file.name.split(".").pop()?.toLowerCase() ?? "";
  if (["docx", "xlsx", "pptx", "rtf", "epub", "srt", "vtt"].includes(ext)) {
    return { text: "", supported: false, formatName };
  }

  return { text: "", supported: false, formatName: formatName ?? "Unknown" };
}

export const SUPPORTED_EXTENSIONS = [".pdf", ".txt", ".md", ".csv", ".html", ".htm"];
export const SCAFFOLDED_EXTENSIONS = [".docx", ".xlsx", ".pptx", ".rtf", ".epub", ".srt", ".vtt"];
export const ALL_EXTENSIONS = [...SUPPORTED_EXTENSIONS, ...SCAFFOLDED_EXTENSIONS];
