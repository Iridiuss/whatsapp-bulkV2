import { NextRequest, NextResponse } from 'next/server';
import { writeFile } from 'fs/promises';
import path from 'path';
import { tmpdir } from 'os';
import { exec } from 'child_process';
import process from 'process';
import fs from 'fs';

export async function POST(req: NextRequest): Promise<Response> {
  const formData = await req.formData();
  const file = formData.get('file') as File;
  const message = formData.get('message') as string;

  if (!file || !message) {
    return NextResponse.json({ error: 'Missing contact file or message' }, { status: 400 });
  }

  try {
    // Save Excel file to temp directory
    const buffer = Buffer.from(await file.arrayBuffer());
    const filePath = path.join(tmpdir(), file.name);
    await writeFile(filePath, buffer);

    // Save the message to a temporary file to avoid command line escaping issues
    const messageFilePath = path.join(tmpdir(), `message_${Date.now()}.txt`);
    await writeFile(messageFilePath, message);

    // Command to call Python script with dynamic root directory
    const scriptPath = path.join(process.cwd(), '..', "backend", "whatsapp-mcp-server2", "send_bulk_whatsapp.py");
    console.log('Script path:', scriptPath);

    // Build command
    const command = `python ${scriptPath} ${filePath} --message-file "${messageFilePath}"`;

    return await new Promise<Response>((resolve) => {
      exec(command, (error, stdout, stderr) => {
        // Clean up temporary files
        fs.unlink(messageFilePath, (unlinkErr) => {
          if (unlinkErr) {
            console.error(`Failed to delete temporary file ${messageFilePath}:`, unlinkErr);
          }
        });

        if (error) {
          console.error('Python Error:', stderr);
          resolve(NextResponse.json({ error: stderr || 'Python script failed' }, { status: 500 }));
        } else {
          console.log('Python Output:', stdout);
          resolve(NextResponse.json({ message: stdout }));
        }
      });
    });
  } catch (err) {
    console.error('Upload error:', err);
    return NextResponse.json({ error: 'Internal error' }, { status: 500 });
  }
}

