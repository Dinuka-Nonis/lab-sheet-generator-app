// Background script for CourseWeb LabSheet Tracker (Firefox compatibility)
// Uses chrome.downloads API so filenames/extensions are preserved reliably.

function buildSafeDocxName(fileName) {
    const fallback = "labsheet-template.docx";
    const source = typeof fileName === "string" && fileName.trim() ? fileName.trim() : fallback;
    const sanitized = source.replace(/[\\/:*?"<>|]/g, "_");
    return sanitized.toLowerCase().endsWith(".docx") ? sanitized : `${sanitized}.docx`;
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "downloadDocx") {
        try {
            const safeFileName = buildSafeDocxName(message.fileName);

            // In Firefox MV3, background scripts have DOM access so we can decode and create Blob URLs directly
            const byteCharacters = atob(message.base64);
            const byteArray = new Uint8Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteArray[i] = byteCharacters.charCodeAt(i);
            }

            const blob = new Blob([byteArray], {
                type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            });

            const url = URL.createObjectURL(blob);

            chrome.downloads.download(
                {
                    url: url,
                    filename: safeFileName,
                    saveAs: false
                },
                (downloadId) => {
                    setTimeout(() => URL.revokeObjectURL(url), 10000);

                    if (chrome.runtime.lastError) {
                        console.error("[LabSheet] Background download error:", chrome.runtime.lastError.message);
                        sendResponse({ success: false, error: chrome.runtime.lastError.message });
                        return;
                    }
                    sendResponse({ success: true, downloadId });
                }
            );

            return true; // Keep message channel open for async response
        } catch (err) {
            console.error("[LabSheet] Error processing download in background:", err);
            sendResponse({ success: false, error: err.message });
        }
    }
});
