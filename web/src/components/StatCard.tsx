import React, { useEffect, useState } from 'react';
import type { LucideIcon } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: number | string;
  icon: LucideIcon;
  subtext?: string;
  severity?: 'default' | 'danger' | 'warning' | 'ok';
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  icon: Icon,
  subtext,
  severity = 'default',
}) => {
  const [displayValue, setDisplayValue] = useState<number | string>(
    typeof value === 'number' ? 0 : value
  );

  useEffect(() => {
    if (typeof value !== 'number') {
      setDisplayValue(value);
      return;
    }

    // Check for prefers-reduced-motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setDisplayValue(value);
      return;
    }

    let start = 0;
    const end = value;
    const duration = 600;
    const steps = 24;
    const increment = end / steps;
    const intervalTime = duration / steps;

    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setDisplayValue(end);
        clearInterval(timer);
      } else {
        setDisplayValue(Math.floor(start));
      }
    }, intervalTime);

    return () => clearInterval(timer);
  }, [value]);

  let accentBorder = 'border-[#DFE3E8]';
  let iconColor = 'text-[#007eb4]';
  let badgeBg = 'bg-[#F4F6F8]';

  if (severity === 'danger') {
    accentBorder = 'border-[#D32F2F]';
    iconColor = 'text-[#D32F2F]';
    badgeBg = 'bg-rose-50';
  } else if (severity === 'warning') {
    accentBorder = 'border-[#F59E0B]';
    iconColor = 'text-[#F59E0B]';
    badgeBg = 'bg-amber-50';
  } else if (severity === 'ok') {
    accentBorder = 'border-[#2E7D32]';
    iconColor = 'text-[#2E7D32]';
    badgeBg = 'bg-emerald-50';
  }

  return (
    <div
      className={`bg-white p-5 rounded-[4px] border ${accentBorder} shadow-[0_1px_2px_rgba(0,0,0,0.04)] flex flex-col justify-between`}
    >
      <div className="flex items-center justify-between gap-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-[#5B6770]">
          {label}
        </span>
        <div className={`p-2 rounded-[4px] ${badgeBg} ${iconColor} flex-shrink-0`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div className="mt-3">
        <div className="text-3xl font-extrabold text-[#1A1A1A] tracking-tight">
          {displayValue}
        </div>
        {subtext && (
          <div className="text-xs text-[#5B6770] mt-1 font-normal">
            {subtext}
          </div>
        )}
      </div>
    </div>
  );
};
