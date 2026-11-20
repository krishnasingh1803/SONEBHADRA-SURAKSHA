import React from 'react';

interface LogoProps {
  size?: number;
  showText?: boolean;
  inverted?: boolean;
}

export const Logo: React.FC<LogoProps> = ({ size = 36, showText = true, inverted = false }) => {
  const primaryColor = inverted ? '#FFFFFF' : '#007eb4';
  const accentColor = inverted ? '#DFE3E8' : '#005a82';
  const textColor = inverted ? '#FFFFFF' : '#1A1A1A';
  const subtextColor = inverted ? '#DFE3E8' : '#5B6770';

  return (
    <div className="flex items-center gap-3 select-none">
      <svg
        width={size}
        height={size}
        viewBox="0 0 44 44"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="flex-shrink-0"
        aria-hidden="true"
      >
        {/* Institutional Shield Outline */}
        <path
          d="M22 3L6 9V20.5C6 30.5 13 38.5 22 41C31 38.5 38 30.5 38 20.5V9L22 3Z"
          fill={inverted ? 'rgba(255,255,255,0.1)' : '#F4F6F8'}
          stroke={primaryColor}
          strokeWidth="2.5"
          strokeLinejoin="round"
        />

        {/* Road Track Geometry */}
        <path
          d="M17 32L20.5 16H23.5L27 32"
          stroke={accentColor}
          strokeWidth="2"
          strokeLinecap="round"
        />
        <line
          x1="22"
          y1="18"
          x2="22"
          y2="28"
          stroke={accentColor}
          strokeWidth="1.5"
          strokeDasharray="2 3"
        />

        {/* Road Pin / Geolocation Marker */}
        <circle
          cx="22"
          cy="14"
          r="4"
          fill={primaryColor}
          stroke={inverted ? '#003B5C' : '#FFFFFF'}
          strokeWidth="1.5"
        />
        <circle cx="22" cy="14" r="1.5" fill="#FFFFFF" />
      </svg>

      {showText && (
        <div className="flex flex-col leading-tight">
          <div className="flex items-baseline gap-1.5">
            <span
              className="font-bold text-lg tracking-tight"
              style={{ color: textColor }}
            >
              Suraksha
            </span>
            <span
              className="text-sm font-semibold tracking-normal"
              style={{ color: primaryColor }}
            >
              सुरक्षा
            </span>
          </div>
          <span
            className="text-[11px] font-medium tracking-wide uppercase"
            style={{ color: subtextColor }}
          >
            Road Safety Portal • Sonbhadra
          </span>
        </div>
      )}
    </div>
  );
};
