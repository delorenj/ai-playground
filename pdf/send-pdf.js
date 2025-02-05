#!/usr/bin/env node

import FormData from 'form-data';
import fs from 'fs';
import { basename } from 'path';
import http from 'http';

if (process.argv.length < 3) {
  console.error('Usage: node send-pdf.js <path-to-pdf> [extract_images=true] [timeout_seconds=300]');
  process.exit(1);
}

const pdfPath = process.argv[2];
const extractImages = process.argv[3] !== 'false'; // Optional parameter, defaults to true
const timeoutSeconds = parseInt(process.argv[4]) || 300; // Optional timeout in seconds, defaults to 5 minutes

// Verify file exists and is accessible
try {
  fs.accessSync(pdfPath, fs.constants.R_OK);
  const stats = fs.statSync(pdfPath);
  const fileSizeMB = stats.size / (1024 * 1024);
  console.log(`File size: ${fileSizeMB.toFixed(2)} MB`);
} catch (err) {
  console.error(`Error: Cannot access file ${pdfPath}`);
  console.error(err.message);
  process.exit(1);
}

// Create form data with PDF file
const form = new FormData();
form.append('pdf_file', fs.createReadStream(pdfPath), {
  filename: basename(pdfPath),
  contentType: 'application/pdf'
});
form.append('extract_images', extractImages ? 'true' : 'false');

// Prepare the request options
const options = {
  hostname: 'localhost',
  port: 3333,
  path: '/convert',
  method: 'POST',
  headers: form.getHeaders(),
  timeout: timeoutSeconds * 1000 // Convert seconds to milliseconds
};

console.log(`Sending ${pdfPath} to marker-api server...`);
console.log(`Image extraction: ${extractImages ? 'enabled' : 'disabled'}`);
console.log(`Request timeout: ${timeoutSeconds} seconds`);

// Send the request
const req = http.request(options, (res) => {
  let data = '';
  let lastProgressTime = Date.now();

  // Set timeout for the response
  res.setTimeout(timeoutSeconds * 1000, () => {
    console.error('Response timeout - server took too long to respond');
    req.destroy();
  });

  res.on('data', (chunk) => {
    data += chunk;
    // Update progress indicator
    lastProgressTime = Date.now();
    process.stdout.write('.');
  });

  res.on('end', () => {
    console.log('\nResponse received');
    if (res.statusCode >= 200 && res.statusCode < 300) {
      try {
        const response = JSON.parse(data);
        console.log('\nMarkdown Output:');
        console.log('---------------');
        console.log(response.markdown);
        
        if (response.metadata) {
          console.log('\nMetadata:');
          console.log('---------');
          console.log(response.metadata);
        }
        
        if (response.images) {
          console.log('\nExtracted Images:');
          console.log('----------------');
          console.log(`Found ${Object.keys(response.images).length} images`);
          
          // Create images directory if it doesn't exist
          const imagesDir = './extracted_images';
          if (!fs.existsSync(imagesDir)) {
            fs.mkdirSync(imagesDir);
          }
          
          // Save images
          for (const [imageName, imageData] of Object.entries(response.images)) {
            const base64Data = imageData.split(';base64,').pop();
            const imageFileName = `${imagesDir}/${imageName}.png`;
            fs.writeFileSync(imageFileName, base64Data, { encoding: 'base64' });
            console.log(`Saved ${imageFileName}`);
          }
        }
      } catch (err) {
        console.error('Error parsing server response:', err.message);
        console.error('Raw response:', data);
      }
    } else {
      console.error(`Error: Server responded with status code ${res.statusCode}`);
      console.error('Response:', data);
    }
  });
});

// Set timeout for the request
req.setTimeout(timeoutSeconds * 1000, () => {
  console.error('Request timeout - server is not responding');
  req.destroy();
});

req.on('error', (error) => {
  if (error.code === 'ECONNREFUSED') {
    console.error('Error: Could not connect to the server. Is it running?');
  } else if (error.code === 'ETIMEDOUT') {
    console.error('Error: Connection timed out. The server took too long to respond.');
  } else {
    console.error('Error sending request:', error.message);
  }
  process.exit(1);
});

// Add upload progress indicator
let uploadedBytes = 0;
const fileSize = fs.statSync(pdfPath).size;

form.on('data', (chunk) => {
  uploadedBytes += chunk.length;
  const progress = (uploadedBytes / fileSize) * 100;
  process.stdout.write(`\rUploading: ${progress.toFixed(1)}%`);
});

// Pipe form data to the request
form.pipe(req);