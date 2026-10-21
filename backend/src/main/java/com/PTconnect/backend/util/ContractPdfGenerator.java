package com.PTconnect.backend.util;

import com.PTconnect.backend.entity.Enrollment;
import com.lowagie.text.*;
import com.lowagie.text.Font;
import com.lowagie.text.pdf.*;
import com.lowagie.text.pdf.draw.LineSeparator;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.awt.Color;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.format.DateTimeFormatter;

@Component
@Slf4j
public class ContractPdfGenerator {

    private static final String CONTRACT_DIR = "uploads/contracts";

    public byte[] generateContractPdf(Enrollment enrollment, String transactionRef) {
        Document document = new Document(PageSize.A4, 40, 40, 50, 50);
        ByteArrayOutputStream baos = new ByteArrayOutputStream();

        try {
            PdfWriter.getInstance(document, baos);
            document.open();

            // Fonts
            Font titleFont = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 18, Color.DARK_GRAY);
            Font subtitleFont = FontFactory.getFont(FontFactory.HELVETICA, 11, Color.GRAY);
            Font sectionFont = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 12, new Color(25, 118, 210));
            Font bodyFont = FontFactory.getFont(FontFactory.HELVETICA, 10, Color.BLACK);
            Font boldFont = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 10, Color.BLACK);
            Font noteFont = FontFactory.getFont(FontFactory.HELVETICA_OBLIQUE, 9, Color.DARK_GRAY);

            // Header
            Paragraph title = new Paragraph("CONG HOA XA HOI CHU NGHIA VIET NAM", boldFont);
            title.setAlignment(Element.ALIGN_CENTER);
            document.add(title);

            Paragraph motto = new Paragraph("Doc lap - Tu do - Hanh phuc", subtitleFont);
            motto.setAlignment(Element.ALIGN_CENTER);
            document.add(motto);

            document.add(new Paragraph(" "));
            LineSeparator ls = new LineSeparator();
            ls.setLineColor(Color.LIGHT_GRAY);
            document.add(ls);
            document.add(new Paragraph(" "));

            Paragraph docTitle = new Paragraph("HOP DONG DICH VU HUAN LUYEN CA NHAN (PT)", titleFont);
            docTitle.setAlignment(Element.ALIGN_CENTER);
            document.add(docTitle);

            String contractNum = "So: PTC-HD-" + String.format("%06d", enrollment.getId());
            Paragraph docNum = new Paragraph(contractNum, subtitleFont);
            docNum.setAlignment(Element.ALIGN_CENTER);
            document.add(docNum);
            document.add(new Paragraph(" "));

            // Thong tin cac ben
            Paragraph pAHeader = new Paragraph("I. THONG TIN CAC BEN THOA THUAN", sectionFont);
            document.add(pAHeader);

            PdfPTable partiesTable = new PdfPTable(2);
            partiesTable.setWidthPercentage(100);
            partiesTable.setSpacingBefore(8f);
            partiesTable.setSpacingAfter(12f);

            // Ben A - Student
            PdfPCell cellA = new PdfPCell();
            cellA.setPadding(8f);
            cellA.setBorderColor(Color.LIGHT_GRAY);
            cellA.addElement(new Paragraph("BEN A (KHACH HANG / HOC VIEN):", boldFont));
            String studentName = (enrollment.getStudent() != null) ? enrollment.getStudent().getFullName() : "N/A";
            String studentEmail = (enrollment.getStudent() != null) ? enrollment.getStudent().getEmail() : "N/A";
            String studentPhone = (enrollment.getStudent() != null && enrollment.getStudent().getPhone() != null)
                    ? enrollment.getStudent().getPhone() : "Chua cap nhat";
            cellA.addElement(new Paragraph("- Ho va ten: " + studentName, bodyFont));
            cellA.addElement(new Paragraph("- Email: " + studentEmail, bodyFont));
            cellA.addElement(new Paragraph("- Dien thoai: " + studentPhone, bodyFont));
            partiesTable.addCell(cellA);

            // Ben B - PT
            PdfPCell cellB = new PdfPCell();
            cellB.setPadding(8f);
            cellB.setBorderColor(Color.LIGHT_GRAY);
            cellB.addElement(new Paragraph("BEN B (HUAN LUYEN VIEN - PT):", boldFont));
            String ptName = (enrollment.getPt() != null && enrollment.getPt().getPt() != null)
                    ? enrollment.getPt().getPt().getFullName() : "N/A";
            String ptEmail = (enrollment.getPt() != null && enrollment.getPt().getPt() != null)
                    ? enrollment.getPt().getPt().getEmail() : "N/A";
            Integer expYears = (enrollment.getPt() != null) ? enrollment.getPt().getExperienceYears() : 0;
            cellB.addElement(new Paragraph("- Ho va ten: " + ptName, bodyFont));
            cellB.addElement(new Paragraph("- Email: " + ptEmail, bodyFont));
            cellB.addElement(new Paragraph("- Kinh nghiem: " + expYears + " nam", bodyFont));
            partiesTable.addCell(cellB);

            document.add(partiesTable);

            // Noi dung goi tap
            Paragraph pBHeader = new Paragraph("II. CHI TIET GOI HUAN LUYEN & THANH TOAN", sectionFont);
            document.add(pBHeader);

            PdfPTable courseTable = new PdfPTable(2);
            courseTable.setWidthPercentage(100);
            courseTable.setSpacingBefore(8f);
            courseTable.setSpacingAfter(12f);

            addTableRow(courseTable, "Khoa hoc / Goi tap:",
                    (enrollment.getCourse() != null) ? enrollment.getCourse().getTitle() : "Goi tap ca nhan", boldFont, bodyFont);
            addTableRow(courseTable, "Dia diem tap luyen co dinh:",
                    enrollment.getTrainingLocation(), boldFont, bodyFont);
            addTableRow(courseTable, "Tong so buoi tap:",
                    enrollment.getTotalSessions() + " buoi", boldFont, bodyFont);

            DateTimeFormatter dtf = DateTimeFormatter.ofPattern("dd/MM/yyyy");
            String dateRange = enrollment.getStartDate().format(dtf) + " den " + enrollment.getEndDate().format(dtf);
            addTableRow(courseTable, "Thoi han hop dong:", dateRange, boldFont, bodyFont);

            String formattedPrice = String.format("%,.0f VND", enrollment.getFinalPrice());
            addTableRow(courseTable, "Hoc phi chot (Final Price):", formattedPrice, boldFont, boldFont);
            addTableRow(courseTable, "Phuong thuc thanh toan:", "Vi dien tu noi bo PT Connect (WALLET)", boldFont, bodyFont);
            addTableRow(courseTable, "Ma giao dich thanh toan:", (transactionRef != null) ? transactionRef : "N/A", boldFont, bodyFont);

            document.add(courseTable);

            // Dieu khoan cam ket
            Paragraph pCHeader = new Paragraph("III. DIEU KHOAN CAM KET & QUY DINH", sectionFont);
            document.add(pCHeader);

            Paragraph terms = new Paragraph();
            terms.setSpacingBefore(6f);
            terms.setSpacingAfter(15f);
            terms.add(new Paragraph("1. Ben B cam ket huong dan dung giao an khoa hoc, bao dam an toan tap luyen.", bodyFont));
            terms.add(new Paragraph("2. Ben A cam ket tuan thu gio giac tap luyen. Moi ca tap duoc dat truoc tren he thong PT Connect.", bodyFont));
            terms.add(new Paragraph("3. Chinh sach huy lich: Thuc hien tu dong theo Quy dinh Huy lich & Den bu cua Nen tang PT Connect.", bodyFont));
            terms.add(new Paragraph("4. Hop dong co hieu luc ke tu thoi diem Ben A thanh toan thanh cong qua Vi dien tu.", bodyFont));
            document.add(terms);

            // Chu ky dien tu
            PdfPTable signTable = new PdfPTable(3);
            signTable.setWidthPercentage(100);
            signTable.setSpacingBefore(10f);

            PdfPCell signA = new PdfPCell();
            signA.setBorder(Rectangle.NO_BORDER);
            signA.setHorizontalAlignment(Element.ALIGN_CENTER);
            signA.addElement(new Paragraph("DAI DIEN BEN A", boldFont));
            signA.addElement(new Paragraph("(Ky dien tu)", noteFont));
            signA.addElement(new Paragraph("\n[Xac nhan OTP / Vi]\n" + studentName, bodyFont));
            signTable.addCell(signA);

            PdfPCell signB = new PdfPCell();
            signB.setBorder(Rectangle.NO_BORDER);
            signB.setHorizontalAlignment(Element.ALIGN_CENTER);
            signB.addElement(new Paragraph("DAI DIEN BEN B", boldFont));
            signB.addElement(new Paragraph("(Ky dien tu)", noteFont));
            signB.addElement(new Paragraph("\n[PT Da Phe Duyet]\n" + ptName, bodyFont));
            signTable.addCell(signB);

            PdfPCell signPlatform = new PdfPCell();
            signPlatform.setBorder(Rectangle.NO_BORDER);
            signPlatform.setHorizontalAlignment(Element.ALIGN_CENTER);
            signPlatform.addElement(new Paragraph("NEN TANG PT CONNECT", boldFont));
            signPlatform.addElement(new Paragraph("(Chung thuc dien tu)", noteFont));
            signPlatform.addElement(new Paragraph("\n[CHUNG THUC SO]\nPT-Connect Platform", bodyFont));
            signTable.addCell(signPlatform);

            document.add(signTable);

            document.close();

            byte[] pdfBytes = baos.toByteArray();
            saveContractToFile(enrollment.getId(), pdfBytes);
            return pdfBytes;

        } catch (DocumentException e) {
            log.error("Loi khi sinh file PDF hop dong cho enrollment id {}: {}", enrollment.getId(), e.getMessage());
            throw new RuntimeException("Loi khi sinh file hop dong PDF: " + e.getMessage(), e);
        }
    }

    private void addTableRow(PdfPTable table, String label, String value, Font labelFont, Font valFont) {
        PdfPCell lCell = new PdfPCell(new Phrase(label, labelFont));
        lCell.setPadding(6f);
        lCell.setBackgroundColor(new Color(245, 245, 245));
        lCell.setBorderColor(Color.LIGHT_GRAY);
        table.addCell(lCell);

        PdfPCell vCell = new PdfPCell(new Phrase(value, valFont));
        vCell.setPadding(6f);
        vCell.setBorderColor(Color.LIGHT_GRAY);
        table.addCell(vCell);
    }

    private void saveContractToFile(Long enrollmentId, byte[] pdfBytes) {
        try {
            Path dirPath = Paths.get(CONTRACT_DIR);
            if (!Files.exists(dirPath)) {
                Files.createDirectories(dirPath);
            }
            Path filePath = dirPath.resolve("contract_" + enrollmentId + ".pdf");
            Files.write(filePath, pdfBytes);
            log.info("Da luu hop dong PDF tai: {}", filePath.toAbsolutePath());
        } catch (IOException e) {
            log.warn("Khong the luu file hop dong ra o dia: {}", e.getMessage());
        }
    }

    public byte[] getExistingContractPdf(Long enrollmentId) {
        try {
            Path filePath = Paths.get(CONTRACT_DIR).resolve("contract_" + enrollmentId + ".pdf");
            if (Files.exists(filePath)) {
                return Files.readAllBytes(filePath);
            }
        } catch (IOException e) {
            log.warn("Loi khi doc file hop dong: {}", e.getMessage());
        }
        return null;
    }
}
