// ============================================
// CourseWeb LabSheet Tracker — DOCX Template Generator
// ============================================
// Uses the docx library (bundled in docx-bundle.js) to generate
// professional lab report cover page templates.

(function () {
    "use strict";

    // Wait for docx bundle to be available
    const docx = window.__docx;
    const saveAs = window.__saveAs;

    if (!docx || !saveAs) {
        console.error("[LabSheet Template] docx or file-saver not loaded");
        return;
    }

    const {
        Document,
        Packer,
        Paragraph,
        TextRun,
        AlignmentType,
        HeadingLevel,
        BorderStyle,
        ImageRun,
        Table,
        TableRow,
        TableCell,
        WidthType,
        VerticalAlign,
        ShadingType,
        TabStopType,
        TabStopPosition,
        PageBreak,
        convertInchesToTwip,
        Header,
        Footer,
        PageNumber,
        NumberFormat,
    } = docx;

    // ---- Helpers ----

    function extractITNumber() {
        // Extract from user menu or page content
        const userMenu = document.querySelector(
            ".usermenu, .userbutton, [data-action='user-menu']"
        );
        if (userMenu) {
            const match = userMenu.textContent.match(/IT\d{8}/);
            if (match) return match[0];
        }
        // Fallback: check page body
        const bodyMatch = document.body.textContent.match(/IT\d{8}/);
        return bodyMatch ? bodyMatch[0] : "IT________";
    }

    function extractStudentName() {
        // Extract full name from the user menu (Moodle stores it in the user button)
        const userBtn = document.querySelector(
            ".usermenu .userbutton .usertext, .usermenu .usertext, .userbutton span.usertext"
        );
        if (userBtn) {
            const name = userBtn.textContent.trim().replace(/IT\d{8}/g, "").trim();
            if (name) return name;
        }
        // Fallback: try the logged-in user link
        const userLink = document.querySelector('.logininfo a[href*="user/profile"], .userloggedinas a');
        if (userLink) {
            const name = userLink.textContent.trim().replace(/IT\d{8}/g, "").trim();
            if (name) return name;
        }
        return "________________";
    }

    function extractLabNumber(assignmentName) {
        // Try to extract lab number from assignment name
        const patterns = [
            /lab\s*sheet\s*(\d+)/i,
            /labsheet\s*(\d+)/i,
            /lab\s*(\d+)/i,
            /practical\s*(\d+)/i,
        ];
        for (const pat of patterns) {
            const m = assignmentName.match(pat);
            if (m) return m[1];
        }
        return "___";
    }

    function extractModuleCode(moduleName) {
        const m = (moduleName || "").match(/^([A-Z]{2,4}\d{3,4})/);
        return m ? m[1] : "";
    }

    function extractModuleFullName(moduleName) {
        // "SE3032 - Graphics and Visualization [2026/JAN]" → "Graphics and Visualization"
        const m = (moduleName || "").match(
            /^[A-Z]{2,4}\d{3,4}\s*[-–]\s*(.+?)(?:\s*\[.*\])?$/
        );
        return m ? m[1].trim() : moduleName || "";
    }

    // Cache the logo so it's only fetched once per page load
    let _cachedLogo = null;

    async function fetchLogoAsBase64() {
        if (_cachedLogo) return _cachedLogo;
        const base64 = "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";
        _cachedLogo = { base64, width: 734, height: 90 };
        return _cachedLogo;
    }

    // ---- DOCX Generation ----

    async function generateLabTemplate(submission) {
        const itNumber = extractITNumber();
        const labNumber = extractLabNumber(
            submission.assignmentName || submission.eventName || ""
        );
        const moduleCode = extractModuleCode(submission.moduleName || "");
        const moduleFullName = extractModuleFullName(submission.moduleName || "");
        const assignmentName = submission.assignmentName || submission.eventName || "Lab Sheet";
        const dueDate = submission.dueDate || "____________";

        // Fetch logo
        const logoData = await fetchLogoAsBase64();

        // Build document sections
        const coverPageChildren = [];

        // ---- Logo ----
        if (logoData) {
            coverPageChildren.push(
                new Paragraph({
                    alignment: AlignmentType.CENTER,
                    spacing: { after: 400 },
                    children: [
                        new ImageRun({
                            data: Uint8Array.from(atob(logoData.base64), (c) =>
                                c.charCodeAt(0)
                            ),
                            transformation: {
                                width: 450,
                                height: 88,
                            },
                            type: "png",
                        }),
                    ],
                })
            );
        } else {
            // Text fallback for logo
            coverPageChildren.push(
                new Paragraph({
                    alignment: AlignmentType.CENTER,
                    spacing: { after: 200 },
                    children: [
                        new TextRun({
                            text: "Sri Lanka Institute of Information Technology",
                            bold: true,
                            size: 32,
                            font: "Calibri",
                            color: "1F3864",
                        }),
                    ],
                }),
                new Paragraph({
                    alignment: AlignmentType.CENTER,
                    spacing: { after: 400 },
                    children: [
                        new TextRun({
                            text: "Malabe, Sri Lanka",
                            size: 22,
                            font: "Calibri",
                            color: "4472C4",
                        }),
                    ],
                })
            );
        }

        // ---- Faculty ----
        coverPageChildren.push(
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { before: 200, after: 100 },
                children: [
                    new TextRun({
                        text: "Faculty of Computing",
                        size: 26,
                        font: "Calibri",
                        color: "2E75B6",
                    }),
                ],
            })
        );

        // ---- Divider line ----
        coverPageChildren.push(
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { before: 200, after: 200 },
                border: {
                    bottom: {
                        style: BorderStyle.SINGLE,
                        size: 6,
                        color: "2E75B6",
                        space: 1,
                    },
                },
                children: [],
            })
        );

        // ---- Module Code (big) ----
        coverPageChildren.push(
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { before: 600, after: 100 },
                children: [
                    new TextRun({
                        text: moduleCode || "Module Code",
                        bold: true,
                        size: 56,
                        font: "Calibri",
                        color: "1F3864",
                    }),
                ],
            })
        );

        // ---- Module Name ----
        coverPageChildren.push(
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 400 },
                children: [
                    new TextRun({
                        text: moduleFullName || "Module Name",
                        size: 32,
                        font: "Calibri",
                        color: "4472C4",
                    }),
                ],
            })
        );

        // ---- Lab/Assignment Title (large) ----
        coverPageChildren.push(
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { before: 400, after: 200 },
                children: [
                    new TextRun({
                        text: `Lab ${labNumber}`,
                        bold: true,
                        size: 44,
                        font: "Calibri",
                        color: "1F3864",
                    }),
                ],
            })
        );

        coverPageChildren.push(
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 600 },
                children: [
                    new TextRun({
                        text: assignmentName,
                        size: 28,
                        font: "Calibri",
                        color: "595959",
                        italics: true,
                    }),
                ],
            })
        );

        // ---- Details Table ----
        const detailsTable = new Table({
            width: { size: 60, type: WidthType.PERCENTAGE },
            alignment: AlignmentType.CENTER,
            rows: [
                createDetailRow("Student ID", itNumber),
                createDetailRow("Student Name", extractStudentName()),
                createDetailRow("Module", `${moduleCode} - ${moduleFullName}`),
                createDetailRow("Lab Number", `Lab ${labNumber}`),
            ],
        });

        coverPageChildren.push(
            new Paragraph({ spacing: { before: 400 }, children: [] })
        );
        coverPageChildren.push(detailsTable);

        // ---- Divider ----
        coverPageChildren.push(
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { before: 600, after: 200 },
                border: {
                    bottom: {
                        style: BorderStyle.SINGLE,
                        size: 6,
                        color: "2E75B6",
                        space: 1,
                    },
                },
                children: [],
            })
        );

        // ---- Date ----
        const today = new Date();
        const dateStr = today.toLocaleDateString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric",
        });

        coverPageChildren.push(
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { before: 200 },
                children: [
                    new TextRun({
                        text: `Date: ${dateStr}`,
                        size: 22,
                        font: "Calibri",
                        color: "595959",
                    }),
                ],
            })
        );

        // ---- Build document ----
        const doc = new Document({
            styles: {
                default: {
                    document: {
                        run: {
                            font: "Calibri",
                            size: 24,
                        },
                    },
                },
            },
            sections: [
                {
                    properties: {
                        page: {
                            margin: {
                                top: convertInchesToTwip(1),
                                right: convertInchesToTwip(1),
                                bottom: convertInchesToTwip(1),
                                left: convertInchesToTwip(1),
                            },
                        },
                    },
                    children: coverPageChildren,
                },
            ],
        });

        // Generate and download using direct anchor approach (more reliable than saveAs in content scripts)
        const blob = await Packer.toBlob(doc);
        const fileName = `${moduleCode}_Lab${labNumber}_${itNumber}.docx`;
        downloadBlob(blob, fileName);

        return fileName;
    }

    function downloadBlob(blob, fileName) {
        // Convert blob to base64 string
        const reader = new FileReader();
        reader.onloadend = () => {
            // reader.result looks like "data:application/octet-stream;base64,....."
            // We just want the base64 part
            const base64data = reader.result.split(',')[1];

            chrome.runtime.sendMessage(
                {
                    action: "downloadDocx",
                    base64: base64data,
                    fileName: fileName,
                },
                (response) => {
                    if (response && response.success) {
                        console.log(`[LabSheet Template] Downloaded: ${fileName} (ID: ${response.downloadId})`);
                    } else {
                        console.error("[LabSheet Template] Download failed:", response?.error);
                    }
                }
            );
        };
        reader.readAsDataURL(blob);
    }

    function createDetailRow(label, value) {
        return new TableRow({
            children: [
                new TableCell({
                    width: { size: 30, type: WidthType.PERCENTAGE },
                    verticalAlign: VerticalAlign.CENTER,
                    shading: {
                        type: ShadingType.SOLID,
                        color: "E7EDF5",
                    },
                    margins: {
                        top: convertInchesToTwip(0.05),
                        bottom: convertInchesToTwip(0.05),
                        left: convertInchesToTwip(0.15),
                        right: convertInchesToTwip(0.1),
                    },
                    children: [
                        new Paragraph({
                            children: [
                                new TextRun({
                                    text: label,
                                    bold: true,
                                    size: 22,
                                    font: "Calibri",
                                    color: "1F3864",
                                }),
                            ],
                        }),
                    ],
                }),
                new TableCell({
                    width: { size: 70, type: WidthType.PERCENTAGE },
                    verticalAlign: VerticalAlign.CENTER,
                    margins: {
                        top: convertInchesToTwip(0.05),
                        bottom: convertInchesToTwip(0.05),
                        left: convertInchesToTwip(0.15),
                        right: convertInchesToTwip(0.1),
                    },
                    children: [
                        new Paragraph({
                            children: [
                                new TextRun({
                                    text: value || "",
                                    size: 22,
                                    font: "Calibri",
                                    color: "333333",
                                }),
                            ],
                        }),
                    ],
                }),
            ],
        });
    }

    // ---- Batch Download ----

    async function generateAllPendingTemplates(submissions) {
        const pending = submissions.filter((s) => {
            const status = (s.submissionStatus || "").toLowerCase();
            return (
                !status.includes("submitted") ||
                status.includes("no attempt") ||
                status.includes("no submission")
            );
        });

        if (pending.length === 0) {
            alert("No pending submissions found!");
            return;
        }

        for (let i = 0; i < pending.length; i++) {
            try {
                const fileName = await generateLabTemplate(pending[i]);
                console.log(`[LabSheet Template] Generated: ${fileName}`);
                // Small delay between downloads to avoid browser blocking
                if (i < pending.length - 1) {
                    await new Promise((r) => setTimeout(r, 800));
                }
            } catch (err) {
                console.error(
                    `[LabSheet Template] Error generating template for ${pending[i].assignmentName}:`,
                    err
                );
            }
        }
    }

    // Expose globally for use by content.js
    window.__labTemplateGenerator = {
        generateLabTemplate,
        generateAllPendingTemplates,
    };

    console.log("[LabSheet Template] Generator loaded");
})();
