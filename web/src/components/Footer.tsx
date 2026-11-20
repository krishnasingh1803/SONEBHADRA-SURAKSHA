import React from 'react';
import { Logo } from './Logo';
import { Phone, Mail, MapPin, ExternalLink, AlertCircle } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full bg-[#003B5C] text-white border-t border-[#DFE3E8] mt-20">
      {/* 4 Columns Institutional Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10">
          {/* Col 1: About */}
          <div className="space-y-4">
            <Logo size={36} inverted={true} />
            <p className="text-xs text-[#DFE3E8] leading-relaxed pt-2">
              Suraksha is Sonbhadra District’s public road safety surveillance platform. Developed in collaboration with district transport authorities and police cells to systematically localize high-frequency collision clusters and prevent road traffic fatalities.
            </p>
            <div className="text-[11px] text-[#DFE3E8]/80">
              District Magistrate Road Safety Cell • Robertsganj, Sonbhadra
            </div>
          </div>

          {/* Col 2: Data & Analytics */}
          <div className="space-y-3">
            <h4 className="text-sm font-bold uppercase tracking-wider text-white border-b border-white/20 pb-2">
              Data & Surveillance
            </h4>
            <ul className="space-y-2 text-xs text-[#DFE3E8]">
              <li>
                <a
                  href="/data/processed/accidents_clean.csv"
                  download
                  className="hover:text-white hover:underline flex items-center gap-1.5"
                >
                  <ExternalLink className="w-3.5 h-3.5 text-[#007eb4]" />
                  <span>Sonbhadra Clean Collisions CSV</span>
                </a>
              </li>
              <li>
                <a
                  href="/data/processed/clusters.csv"
                  download
                  className="hover:text-white hover:underline flex items-center gap-1.5"
                >
                  <ExternalLink className="w-3.5 h-3.5 text-[#007eb4]" />
                  <span>DBSCAN Blackspot Clusters CSV</span>
                </a>
              </li>
              <li>
                <span className="text-[#DFE3E8]/80">
                  DBSCAN Algorithm: eps=300m, min_samples=3
                </span>
              </li>
              <li>
                <span className="text-[#DFE3E8]/80">
                  Geocode Median Accuracy: 29.7m (n=30 sample)
                </span>
              </li>
              <li>
                <a
                  href="http://127.0.0.1:8000/docs"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-white hover:underline flex items-center gap-1.5 text-sky-300"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>FastAPI Data Service Docs</span>
                </a>
              </li>
            </ul>
          </div>

          {/* Col 3: Policies & Standards */}
          <div className="space-y-3">
            <h4 className="text-sm font-bold uppercase tracking-wider text-white border-b border-white/20 pb-2">
              Governance & Standards
            </h4>
            <ul className="space-y-2 text-xs text-[#DFE3E8]">
              <li>
                <span>Ministry of Road Transport & Highways (MoRTH) Protocol</span>
              </li>
              <li>
                <span>Indian Road Congress (IRC) Blackspot Criteria</span>
              </li>
              <li>
                <span>UP State Road Safety Policy (Empirical Mapping)</span>
              </li>
              <li>
                <span>Open Government Data (OGD) Framework</span>
              </li>
              <li>
                <span>Citizen Data Privacy & Confidentiality</span>
              </li>
            </ul>
          </div>

          {/* Col 4: Contact & Emergency */}
          <div className="space-y-3">
            <h4 className="text-sm font-bold uppercase tracking-wider text-white border-b border-white/20 pb-2">
              Emergency & Inquiries
            </h4>
            <div className="space-y-2.5 text-xs text-[#DFE3E8]">
              <div className="flex items-start gap-2">
                <MapPin className="w-4 h-4 text-[#007eb4] flex-shrink-0 mt-0.5" />
                <span>District Administrative Complex, Robertsganj, Sonbhadra, UP 231216</span>
              </div>
              <div className="flex items-center gap-2">
                <Phone className="w-4 h-4 text-[#2E7D32] flex-shrink-0" />
                <span>UP Police Traffic Emergency: <strong>112</strong></span>
              </div>
              <div className="flex items-center gap-2">
                <Phone className="w-4 h-4 text-[#D32F2F] flex-shrink-0" />
                <span>National Highway Ambulance: <strong>1033 / 108</strong></span>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4 text-[#F59E0B] flex-shrink-0" />
                <span>roadsafety.sonbhadra@up.gov.in</span>
              </div>
            </div>
          </div>
        </div>

        {/* Notice on Data Scope & Limitations */}
        <div className="mt-12 pt-6 border-t border-white/15 bg-white/5 p-4 rounded-[4px] flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-sky-300 flex-shrink-0 mt-0.5" />
          <div className="text-xs text-[#DFE3E8] leading-relaxed">
            <strong className="text-white block mb-1">
              Data Scope & Analytical Notice:
            </strong>
            The collision records analyzed on this portal are compiled from regional media reports and verified citizen alerts in Sonbhadra District. Published news accounts naturally emphasize fatal and serious crashes, while minor property-damage collisions may not be reflected. Blackspot boundaries are indicative spatial surveillance clusters to guide police patrol prioritization and engineering inspections; they do not imply sole mechanical fault.
          </div>
        </div>

        {/* Copyright & Disclaimer */}
        <div className="mt-8 pt-6 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between text-xs text-[#DFE3E8]/70 gap-3">
          <div>
            © 2026 District Road Safety Cell, Sonbhadra. Public domain analytical publication.
          </div>
          <div>
            Suraksha Intelligence Version 2.4.0 (Institutional Release)
          </div>
        </div>
      </div>
    </footer>
  );
};
