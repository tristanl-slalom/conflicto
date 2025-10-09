import { useState, useRef, useEffect } from 'react';
import { Copy, ExternalLink, QrCode, Maximize2, CheckCircle, AlertTriangle } from 'lucide-react';
import QRCodeStyling from 'qr-code-styling';
import { SessionDetail } from '../../api/generated';

interface QRCodeDisplayProps {
  session?: SessionDetail;
  size?: 'small' | 'medium' | 'large';
  showUrl?: boolean;
  showCopyActions?: boolean;
  className?: string;
}

export function QRCodeDisplay({
  session,
  size = 'medium',
  showUrl = true,
  showCopyActions = true,
  className = ''
}: QRCodeDisplayProps) {
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const [showLargeQR, setShowLargeQR] = useState(false);

  if (!session?.qr_code) {
    return (
      <div className={`bg-slate-800 rounded-lg p-6 border border-slate-700 ${className}`}>
        <div className="flex items-center justify-center text-slate-400 py-8">
          <AlertTriangle className="w-5 h-5 mr-2" />
          <span>No QR code available</span>
        </div>
      </div>
    );
  }

  const getJoinUrl = () => `${window.location.origin}/session/${session.qr_code}`;

  const handleCopyCode = async (text: string, type: 'qr' | 'url') => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedCode(type);
      setTimeout(() => setCopiedCode(null), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const getQRSize = () => {
    switch (size) {
      case 'small': return 'w-32 h-32';
      case 'medium': return 'w-48 h-48';
      case 'large': return 'w-64 h-64';
      default: return 'w-48 h-48';
    }
  };

  const qrRef = useRef<HTMLDivElement>(null);
  const qrLargeRef = useRef<HTMLDivElement>(null);

  const createQRCode = (size: number) => {
    const joinUrl = getJoinUrl();

    return new QRCodeStyling({
      width: size,
      height: size,
      type: "svg",
      data: joinUrl,
      image: undefined, // Could add a logo here
      dotsOptions: {
        color: "#1e293b", // slate-800
        type: "rounded"
      },
      backgroundOptions: {
        color: "#ffffff",
      },
      cornersSquareOptions: {
        color: "#0f172a", // slate-900
        type: "extra-rounded",
      },
      cornersDotOptions: {
        color: "#0f172a", // slate-900
        type: "dot",
      },
      margin: 8
    });
  };

  useEffect(() => {
    if (session?.qr_code) {
      const qrSize = size === 'small' ? 128 : size === 'medium' ? 192 : 256;
      const qrCode = createQRCode(qrSize);

      if (qrRef.current) {
        qrRef.current.innerHTML = '';
        qrCode.append(qrRef.current);
      }
    }
  }, [session?.qr_code, size]);

  useEffect(() => {
    if (showLargeQR && session?.qr_code) {
      const qrCode = createQRCode(320);

      if (qrLargeRef.current) {
        qrLargeRef.current.innerHTML = '';
        qrCode.append(qrLargeRef.current);
      }
    }
  }, [showLargeQR, session?.qr_code]);

  return (
    <>
      <div className={`bg-slate-800 rounded-lg p-6 border border-slate-700 ${className}`}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-white font-medium flex items-center gap-2">
            <QrCode className="w-5 h-5" />
            QR Code
          </h3>
          {showCopyActions && (
            <button
              onClick={() => setShowLargeQR(true)}
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-600 rounded transition-colors"
              title="View large QR code"
            >
              <Maximize2 className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* QR Code Display */}
        <div className="flex justify-center mb-4">
          <div className={`bg-white p-4 rounded-lg flex items-center justify-center ${getQRSize()}`}>
            <div ref={qrRef} className="flex items-center justify-center" />
          </div>
        </div>

        {/* QR Code Info */}
        <div className="space-y-3">
          <div>
            <label className="block text-sm text-slate-300 mb-1">QR Code</label>
            <div className="flex items-center gap-2">
              <code className="flex-1 px-3 py-2 bg-slate-700 rounded text-white text-sm font-mono">
                {session.qr_code}
              </code>
              {showCopyActions && (
                <button
                  onClick={() => handleCopyCode(session.qr_code!, 'qr')}
                  className="p-2 text-slate-400 hover:text-white hover:bg-slate-600 rounded transition-colors"
                  title="Copy QR code"
                >
                  {copiedCode === 'qr' ? (
                    <CheckCircle className="w-4 h-4 text-green-400" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </button>
              )}
            </div>
          </div>

          {showUrl && (
            <div>
              <label className="block text-sm text-slate-300 mb-1">Join URL</label>
              <div className="flex items-center gap-2">
                <code className="flex-1 px-3 py-2 bg-slate-700 rounded text-white text-sm font-mono break-all">
                  {getJoinUrl()}
                </code>
                {showCopyActions && (
                  <>
                    <button
                      onClick={() => handleCopyCode(getJoinUrl(), 'url')}
                      className="p-2 text-slate-400 hover:text-white hover:bg-slate-600 rounded transition-colors"
                      title="Copy join URL"
                    >
                      {copiedCode === 'url' ? (
                        <CheckCircle className="w-4 h-4 text-green-400" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </button>
                    <a
                      href={getJoinUrl()}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-2 text-slate-400 hover:text-white hover:bg-slate-600 rounded transition-colors"
                      title="Open join URL"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Session Status Info */}
        <div className="mt-4 p-3 bg-slate-700/30 rounded-lg">
          <div className="text-xs text-slate-400 space-y-1">
            <div className="flex justify-between">
              <span>Status:</span>
              <span className="text-white capitalize">{session.status}</span>
            </div>
            {session.status === 'draft' && (
              <div className="text-yellow-400 text-center mt-2">
                Start session to enable joining
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Large QR Code Modal */}
      {showLargeQR && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg p-6 max-w-md mx-4 border border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-white">Scan to Join Session</h3>
              <button
                onClick={() => setShowLargeQR(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="flex justify-center mb-4">
              <div className="bg-white p-6 rounded-lg flex items-center justify-center">
                <div ref={qrLargeRef} className="flex items-center justify-center" />
              </div>
            </div>

            <div className="text-center text-slate-300 space-y-2">
              <p className="font-medium">{session.title}</p>
              <p className="text-sm text-slate-400">
                Point your phone camera at the QR code to join
              </p>
            </div>

            <div className="mt-4 flex gap-2">
              <button
                onClick={() => handleCopyCode(getJoinUrl(), 'url')}
                className="flex-1 py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                {copiedCode === 'url' ? 'Copied!' : 'Copy Link'}
              </button>
              <button
                onClick={() => setShowLargeQR(false)}
                className="px-4 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
