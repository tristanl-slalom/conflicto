import React, { useEffect, useRef } from 'react';
import QRCodeStyling from 'qr-code-styling';

interface QRCodeDisplayProps {
  sessionId: number;
  size?: number;
  className?: string;
}

const QRCodeDisplay: React.FC<QRCodeDisplayProps> = ({ 
  sessionId, 
  size = 256, 
  className 
}) => {
  const qrCodeRef = useRef<HTMLDivElement>(null);
  const qrCode = useRef<QRCodeStyling | null>(null);

  useEffect(() => {
    if (!sessionId) return;

    // Generate join URL using session ID
    const joinUrl = `https://app.caja.dbash.dev/join/${sessionId}`;

    // Create QR code instance with styling
    qrCode.current = new QRCodeStyling({
      width: size,
      height: size,
      type: "svg",
      data: joinUrl,
      image: "/logo192.png", // Use app logo in center
      dotsOptions: {
        color: "#1f2937", // Dark gray dots
        type: "rounded"
      },
      backgroundOptions: {
        color: "#ffffff", // White background
      },
      imageOptions: {
        crossOrigin: "anonymous",
        margin: 8,
        imageSize: 0.2 // Logo size relative to QR code
      },
      cornersSquareOptions: {
        color: "#3b82f6", // Blue corner squares
        type: "extra-rounded"
      },
      cornersDotOptions: {
        color: "#3b82f6", // Blue corner dots
        type: "dot"
      },
      qrOptions: {
        errorCorrectionLevel: "M" // Medium error correction for logo
      }
    });

    // Render QR code to DOM element
    if (qrCodeRef.current) {
      qrCodeRef.current.innerHTML = '';
      qrCode.current.append(qrCodeRef.current);
    }

    return () => {
      // Cleanup
      if (qrCodeRef.current) {
        qrCodeRef.current.innerHTML = '';
      }
    };
  }, [sessionId, size]);

  return (
    <div className={`qr-code-container ${className || ''}`}>
      <div 
        ref={qrCodeRef} 
        className="qr-code-display flex justify-center items-center"
      />
      <div className="qr-code-info text-center mt-4 text-sm text-gray-600">
        <p>Scan to join session</p>
        <p className="font-mono text-xs mt-1">
          Session ID: {sessionId}
        </p>
      </div>
    </div>
  );
};

export default QRCodeDisplay;