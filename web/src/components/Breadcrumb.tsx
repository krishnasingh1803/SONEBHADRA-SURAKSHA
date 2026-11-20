import React from 'react';
import { ChevronRight, Home } from 'lucide-react';

export interface BreadcrumbItem {
  label: string;
  onClick?: () => void;
  active?: boolean;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({ items }) => {
  return (
    <nav
      aria-label="Breadcrumb"
      className="w-full bg-[#F4F6F8] border-b border-[#DFE3E8] py-2 px-4 sm:px-6 lg:px-8 text-xs text-[#5B6770]"
    >
      <div className="max-w-7xl mx-auto flex items-center flex-wrap gap-1.5">
        <button
          onClick={items[0]?.onClick}
          className="inline-flex items-center gap-1 hover:text-[#007eb4] focus-visible:outline-2 focus-visible:outline-[#007eb4] p-0.5"
          aria-label="Home"
        >
          <Home className="w-3.5 h-3.5 flex-shrink-0" />
          <span>Home</span>
        </button>

        {items.slice(1).map((item, index) => (
          <React.Fragment key={index}>
            <ChevronRight className="w-3 h-3 text-[#DFE3E8] flex-shrink-0" aria-hidden="true" />
            {item.active || !item.onClick ? (
              <span className="font-semibold text-[#1A1A1A]" aria-current="page">
                {item.label}
              </span>
            ) : (
              <button
                onClick={item.onClick}
                className="hover:text-[#007eb4] hover:underline focus-visible:outline-2 focus-visible:outline-[#007eb4] p-0.5 text-left"
              >
                {item.label}
              </button>
            )}
          </React.Fragment>
        ))}
      </div>
    </nav>
  );
};
