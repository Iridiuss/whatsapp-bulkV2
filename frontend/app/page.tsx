'use client';

import WhatsAppQR from '@/components/whatsappQR';
import { useState, useEffect } from 'react';

// Function to make URLs clickable in text
const TextWithClickableLinks = ({ text }: { text: string }) => {
  // Enhanced regex to match various URL formats and domains
  // This will detect URLs like www.example.com, http://example.com, youtube.com/watch etc.
  const urlRegex = /(https?:\/\/(?:www\.)?[^\s]+)|(?<!\S)(www\.[^\s]+)|(?<!\S)(?:[a-zA-Z0-9][-a-zA-Z0-9]+\.[a-zA-Z0-9]{2,}(?:\.[a-zA-Z0-9]{2,})?(?:\/[^\s]*)?)/g;

  // Split the text and find matches
  const processedText = text.replace(urlRegex, (match) => {
    // To mark this as a URL for the next step
    return `[[URL::${match}::URL]]`;
  });

  // Now split by our custom markers
  const parts = processedText.split(/\[\[URL::|\::URL\]\]/);

  // Build the final elements
  const elements: React.ReactNode[] = [];
  parts.forEach((part, i) => {
    // Skip empty parts
    if (!part) return;

    // Check if this part was a URL (every other part after a marker)
    if (i % 2 === 1) {
      // URLs need to start with a protocol for href
      const href = part.startsWith('http') ? part : `https://${part}`;
      elements.push(
        <a
          key={`link-${i}`}
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:underline break-all"
        >
          {part}
        </a>
      );
    } else {
      elements.push(<span key={`text-${i}`}>{part}</span>);
    }
  });

  return <div className="whitespace-pre-line">{elements}</div>;
};

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  // Fixed message that will be used
  const fixedMessage = `Hey Future Stars!
Want to boost your Math skills while learning the beautiful art of Classical Kathak Dance – all from the comfort of your home?
Here's your chance!
Join the Free Online Classical Kathak Dance + Mathematics Course
by The Art of Living Foundation 
Time: Thrice / week at 6:30 PM
Where: Zoom
Fees: Absolutely FREE!
Why Should You Join?
✅ Fun & Easy Learning
✅ Stronger Math Skills
✅ National Competition Opportunities
✅ Certificates & Government Recognition
✅ Taught by National Awardee Trainers
Ready to shine?
Join the WhatsApp group NOW to get started:
https://chat.whatsapp.com/I5luuVBs7WK7AcOGkne2X6
Watch our Youtube Video Links To see how Thousands of Youth Are Benefiting : 
https://youtu.be/oCGeNckQiIo?si=kpkwqfo2NWsNMR6s
https://youtu.be/5WVWPFCfqs0?si=q631VglxFa8dt0rS
https://youtu.be/o8gmEGFjeVo?si=-GoJKrTjHkFEIz77
Need Help? Call/WhatsApp Us:
📞 9353173653 / 9830059978
Let's learn, dance, and grow together – India is rising!`;

  useEffect(() => {
    // No need to set the message state since we're using fixedMessage directly
  }, []);

  const handleSubmit = async () => {
    if (!file) return alert('Contact file is required');

    const formData = new FormData();
    formData.append('file', file);
    // Always use the fixed message
    formData.append('message', fixedMessage);

    setLoading(true);
    setStatus('');

    const res = await fetch('/api/sendbulk', {
      method: 'POST',
      body: formData,
    });

    const data = await res.json();
    setStatus(data.message || data.error || 'Unknown result');
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-white rounded-xl shadow-2xl p-8 border border-gray-100">
        <div className="flex items-center justify-center gap-2 mb-10">
          <div className="text-4xl">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" className="w-10 h-10 fill-green-600">
              <path d="M380.9 97.1C339 55.1 283.2 32 223.9 32c-122.4 0-222 99.6-222 222 0 39.1 10.2 77.3 29.6 111L0 480l117.7-30.9c32.4 17.7 68.9 27 106.1 27h.1c122.3 0 224.1-99.6 224.1-222 0-59.3-25.2-115-67.1-157zm-157 341.6c-33.2 0-65.7-8.9-94-25.7l-6.7-4-69.8 18.3L72 359.2l-4.4-7c-18.5-29.4-28.2-63.3-28.2-98.2 0-101.7 82.8-184.5 184.6-184.5 49.3 0 95.6 19.2 130.4 54.1 34.8 34.9 56.2 81.2 56.1 130.5 0 101.8-84.9 184.6-186.6 184.6zm101.2-138.2c-5.5-2.8-32.8-16.2-37.9-18-5.1-1.9-8.8-2.8-12.5 2.8-3.7 5.6-14.3 18-17.6 21.8-3.2 3.7-6.5 4.2-12 1.4-32.6-16.3-54-29.1-75.5-66-5.7-9.8 5.7-9.1 16.3-30.3 1.8-3.7.9-6.9-.5-9.7-1.4-2.8-12.5-30.1-17.1-41.2-4.5-10.8-9.1-9.3-12.5-9.5-3.2-.2-6.9-.2-10.6-.2-3.7 0-9.7 1.4-14.8 6.9-5.1 5.6-19.4 19-19.4 46.3 0 27.3 19.9 53.7 22.6 57.4 2.8 3.7 39.1 59.7 94.8 83.8 35.2 15.2 49 16.5 66.6 13.9 10.7-1.6 32.8-13.4 37.4-26.4 4.6-13 4.6-24.1 3.2-26.4-1.3-2.5-5-3.9-10.5-6.6z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-green-600">WhatsApp Bulk Sender</h1>
        </div>

        <div className="space-y-8">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="flex items-center justify-center w-8 h-8 rounded-full bg-green-600 text-white font-bold">1</div>
              <h2 className="text-xl font-semibold text-gray-800">Connect WhatsApp</h2>
            </div>
            <div className="container mx-auto px-4 py-4">
              <WhatsAppQR />
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="flex items-center justify-center w-8 h-8 rounded-full bg-green-600 text-white font-bold">2</div>
              <h2 className="text-xl font-semibold text-gray-800">Upload Contact List</h2>
            </div>
            <div className="relative border-2 border-dashed border-gray-300 rounded-lg p-6 flex justify-center items-center bg-gray-50 hover:bg-gray-100 transition cursor-pointer">
              <input
                type="file"
                accept=".xlsx"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <div className="text-center">
                <div className="text-gray-500 mb-1">{file ? file.name : 'Drop Excel file here or click to upload'}</div>
                <p className="text-xs text-gray-400">Supports .xlsx format</p>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="flex items-center justify-center w-8 h-8 rounded-full bg-green-600 text-white font-bold">3</div>
              <h2 className="text-xl font-semibold text-gray-800">Fixed Message</h2>
              <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full font-medium">Cannot be edited</span>
            </div>
            <div className="w-full border border-gray-300 rounded-lg p-3 h-60 bg-gray-50 text-gray-800 overflow-auto">
              <TextWithClickableLinks text={fixedMessage} />
            </div>
          </div>

          <div className="space-y-4 mt-8">
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="w-full bg-green-600 hover:bg-green-700 text-white py-3 px-4 rounded-lg font-medium transition focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Sending messages, it may take a while...
                </span>
              ) : 'Send WhatsApp Messages'}
            </button>
          </div>
        </div>

        {status && (
          <div className="mt-8 p-4 rounded-lg bg-green-50 border border-green-200">
            <div className="whitespace-pre-line text-green-800 font-medium">
              {status}
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 
