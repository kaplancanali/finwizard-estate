import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";
import type { InventoryAnalysisReport } from "@/lib/types/analysis";

function safe(text: string, max = 900): string {
  return text
    .replace(/\u011f/g, "g")
    .replace(/\u011e/g, "G")
    .replace(/\u00fc/g, "u")
    .replace(/\u00dc/g, "U")
    .replace(/\u015f/g, "s")
    .replace(/\u015e/g, "S")
    .replace(/\u0131/g, "i")
    .replace(/\u0130/g, "I")
    .replace(/\u00f6/g, "o")
    .replace(/\u00d6/g, "O")
    .replace(/\u00e7/g, "c")
    .replace(/\u00c7/g, "C")
    .slice(0, max);
}

export function downloadAnalysisPdf(
  report: InventoryAnalysisReport,
  propertyTitle: string
) {
  const doc = new jsPDF({ unit: "pt", format: "a4" });
  const margin = 40;
  let y = margin;

  const addTitle = (text: string, size = 14) => {
    if (y > 760) {
      doc.addPage();
      y = margin;
    }
    doc.setFont("helvetica", "bold");
    doc.setFontSize(size);
    doc.text(safe(text, 120), margin, y);
    y += size + 8;
  };

  const addPara = (text: string, size = 10) => {
    doc.setFont("helvetica", "normal");
    doc.setFontSize(size);
    const lines = doc.splitTextToSize(safe(text, 4000), 515);
    for (const line of lines) {
      if (y > 780) {
        doc.addPage();
        y = margin;
      }
      doc.text(line, margin, y);
      y += size + 3;
    }
    y += 6;
  };

  addTitle("Torkam — AI Envanter Analiz Raporu", 16);
  addPara(`Ilan: ${propertyTitle}`);
  addPara(
    `Skor: ${report.overall_score}/100 | Guven: ${report.confidence_score}/100 | Madde: ${report.inventory_items_covered}/${report.inventory_items_total}`
  );
  addPara(`Model: ${report.model} | Tarih: ${new Date(report.generated_at).toLocaleString("tr-TR")}`);

  addTitle("Yonetici Ozeti");
  addPara(report.executive_summary);

  addTitle("Metodoloji");
  addPara(report.methodology);

  addTitle("Tavsiye");
  addPara(report.recommendation);

  addTitle("Riskler");
  addPara((report.risks.length ? report.risks : ["-"]).map((r) => `• ${r}`).join("\n"));

  addTitle("Firsatlar");
  addPara(
    (report.opportunities.length ? report.opportunities : ["-"]).map((r) => `• ${r}`).join("\n")
  );

  addTitle("Veri Bosluklari");
  addPara((report.data_gaps.length ? report.data_gaps : ["-"]).map((r) => `• ${r}`).join("\n"));

  addTitle("Due Diligence Checklist");
  addPara(
    (report.due_diligence.length ? report.due_diligence : ["-"]).map((r) => `• ${r}`).join("\n")
  );

  for (const cat of report.categories) {
    addTitle(`${cat.title} (${cat.score ?? "—"}/100)`);
    addPara(cat.summary);
    addPara(
      `Kapsam: ${cat.coverage.evaluated}/${cat.coverage.total} degerlendirildi | unknown=${cat.coverage.unknown} risk=${cat.coverage.risk} olumlu=${cat.coverage.positive}`
    );

    const rows = cat.findings.map((f) => [
      safe(f.label || f.item_id, 40),
      f.status,
      String(f.confidence ?? "—"),
      f.evidence_strength,
      safe(f.evidence, 60),
      safe(f.required_proof, 60),
      safe(f.note, 60),
    ]);

    autoTable(doc, {
      startY: y,
      head: [["Madde", "Durum", "Conf", "Kanit", "Evidence", "Required proof", "Not"]],
      body: rows,
      styles: { fontSize: 7, cellPadding: 2 },
      headStyles: { fillColor: [11, 76, 132] },
      margin: { left: margin, right: margin },
    });

    const finalY =
      (doc as unknown as { lastAutoTable?: { finalY?: number } }).lastAutoTable?.finalY ?? y;
    y = finalY + 16;
  }

  const filename = `torkam-analiz-${report.property_id.slice(0, 8)}.pdf`;
  doc.save(filename);
}
