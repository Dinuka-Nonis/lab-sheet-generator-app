// Offscreen document script for CourseWeb LabSheet Tracker
// Creates blob URLs for downloading DOCX files with proper filenames
// URL.createObjectURL IS available here (unlike in service workers)

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.target !== "offscreen") return;

    if (message.action === "createBlobAndDownload") {
        try {
            // Convert base64 to binary array
            const byteCharacters = atob(message.base64);
            const byteArray = new Uint8Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteArray[i] = byteCharacters.charCodeAt(i);
            }

            // Create blob with correct MIME type
            const blob = new Blob([byteArray], {
                type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            });

            // Create blob URL (this works in offscreen documents!)
            const url = URL.createObjectURL(blob);

            // Use an anchor element to trigger download with proper filename
            const a = document.createElement("a");
            a.href = url;
            a.download = message.fileName;
            a.click();

            // Clean up after a delay
            setTimeout(() => URL.revokeObjectURL(url), 10000);

            sendResponse({ success: true });
        } catch (err) {
            console.error("[LabSheet Offscreen] Error:", err);
            sendResponse({ success: false, error: err.message });
        }
        return true;
    }
});
