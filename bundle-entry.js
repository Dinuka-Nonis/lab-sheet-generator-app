// Bundle entry point for docx template generator
// This file imports docx and file-saver and exposes them globally

const docx = require('docx');
const { saveAs } = require('file-saver');

window.__docx = docx;
window.__saveAs = saveAs;
