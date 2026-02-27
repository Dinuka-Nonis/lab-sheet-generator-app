// Background service worker for CourseWeb LabSheet Tracker
// Uses chrome.downloads API so filenames/extensions are preserved reliably.

function buildSafeDocxName(fileName) {
    const fallback = "labsheet-template.docx";
    const source = typeof fileName === "string" && fileName.trim() ? fileName.trim() : fallback;
    const sanitized = source.replace(/[\\/:*?"<>|]/g, "_");
    return sanitized.toLowerCase().endsWith(".docx") ? sanitized : `${sanitized}.docx`;
}

let creatingOffscreen;
async function setupOffscreenDocument(path) {
    const url = chrome.runtime.getURL(path);
    const existingContexts = await chrome.runtime.getContexts({
        contextTypes: ['OFFSCREEN_DOCUMENT'],
        documentUrls: [url]
    });

    if (existingContexts.length > 0) {
        return;
    }

    if (creatingOffscreen) {
        await creatingOffscreen;
    } else {
        creatingOffscreen = chrome.offscreen.createDocument({
            url: path,
            reasons: ['BLOBS'],
            justification: 'To use Blob URLs to trigger DOCX file downloads with correct filenames'
        });
        await creatingOffscreen;
        creatingOffscreen = null;
    }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "downloadDocx") {
        const safeFileName = buildSafeDocxName(message.fileName);

        // Forward to the offscreen document instead of using chrome.downloads
        setupOffscreenDocument("offscreen.html").then(() => {
            chrome.runtime.sendMessage(
                {
                    target: "offscreen",
                    action: "createBlobAndDownload",
                    base64: message.base64,
                    fileName: safeFileName
                },
                (response) => {
                    if (chrome.runtime.lastError) {
                        console.error("[LabSheet] Offscreen message error:", chrome.runtime.lastError.message);
                        sendResponse({ success: false, error: chrome.runtime.lastError.message });
                        return;
                    }
                    sendResponse(response);
                }
            );
        }).catch((err) => {
            console.error("[LabSheet] Offscreen creation error:", err);
            sendResponse({ success: false, error: err.message });
        });

        return true; // Keep message channel open for async response
    }
});
