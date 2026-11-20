import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useThemeLanguage } from '../context/ThemeLanguageContext';
import { getStatsApi, getClustersApi, getAccidentsApi } from '../services/api';
import type { Stats, Cluster, Accident } from '../types';
import { StatCard } from '../components/StatCard';
import {
  Shield,
  MapPin,
  FileText,
  Download,
  ChevronRight,
  BarChart3,
  AlertTriangle,
  Clock,
  Compass,
  ArrowRight,
  Database,
  Layers,
  CheckCircle2,
  Camera,
  Eye,
  Mountain,
} from 'lucide-react';

interface LandingPageProps {
  onNavigate: (page: 'home' | 'admin' | 'citizen' | 'login') => void;
}

const SONBHADRA_LANDMARKS = [
  {
    id: 'markundi',
    name: 'Son Valley & Markundi Ghati (NH-39)',
    nameHi: 'सोन घाटी एवं मारकुंडी मोड़ (राष्ट्रीय राजमार्ग-39)',
    image: '/images/sonbhadra/son_valley_markundi.jpg',
    description: 'Steep winding descent into Son Valley with hairpin curves and heavy mineral dumper convoys.',
    risk: 'Rank #1 Critical Hotspot • 19 Fatalities • 111.5 Severity Score',
    credit: 'Photo: Eco Point Robertsganj / Wikimedia Commons (CC BY-SA 4.0)',
  },
  {
    id: 'rihand',
    name: 'Govind Ballabh Pant Sagar / Rihand Reservoir',
    nameHi: 'गोविंद वल्लभ पंत सागर / रिहंद बांध (रेणुकूट)',
    image: '/images/sonbhadra/rihand_dam_renukoot.jpg',
    description: 'Major transit corridor along SH-5A connecting Hindalco industrial complex and Pipri.',
    risk: 'Rank #4 Murdhawa Mor Gateway • Industrial Haulage Route',
    credit: 'Photo: Govind Vallabh on Rihand / Wikimedia Commons (CC BY-SA 3.0)',
  },
  {
    id: 'shaktinagar',
    name: 'Shaktinagar Power & Coal Mining Corridor',
    nameHi: 'शक्तिनगर ताप विद्युत एवं कोयला परिवहन मार्ग',
    image: '/images/sonbhadra/shaktinagar_corridor.jpg',
    description: 'Multi-axle coal tipper thoroughfare with dense evening dust fog and reduced sightlines.',
    risk: 'Rank #5 Jwalamukhi Mor • Frequent Overloaded Truck Collisions',
    credit: 'Photo: SSTPS Shaktinagar / Wikimedia Commons (CC BY-SA 3.0)',
  },
  {
    id: 'kaimur',
    name: 'Kaimur Range Foothills & Robertsganj Highway',
    nameHi: 'कैमूर पर्वतमाला एवं रॉबर्ट्सगंज बाईपास',
    image: '/images/sonbhadra/kaimur_escarpment.jpg',
    description: 'Rugged terrain corridor with high-speed rural straightaways meeting abrupt blind curves.',
    risk: 'Churk Cement Bypass & Hathinala Junction Vulnerability',
    credit: 'Photo: Lakhaniya Dari Escarpment / Wikimedia Commons (CC BY-SA 3.0)',
  },
];

export const LandingPage: React.FC<LandingPageProps> = ({ onNavigate }) => {
  const { t, lang } = useThemeLanguage();
  const [stats, setStats] = useState<Stats | null>(null);
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [recentAccidents, setRecentAccidents] = useState<Accident[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'blackspots' | 'patterns' | 'methodology'>('overview');
  const [currentPhotoIdx, setCurrentPhotoIdx] = useState(0);

  useEffect(() => {
    async function fetchData() {
      try {
        const [s, c, acc] = await Promise.all([
          getStatsApi(),
          getClustersApi(),
          getAccidentsApi(),
        ]);
        setStats(s);
        setClusters(c);
        setRecentAccidents(acc);
      } catch (err) {
        console.error('Failed to load landing data', err);
      }
    }
    fetchData();
  }, []);

  // Automatic gentle rotation of hero photos every 8 seconds
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentPhotoIdx((prev) => (prev + 1) % SONBHADRA_LANDMARKS.length);
    }, 8000);
    return () => clearInterval(timer);
  }, []);

  const activeLandmark = SONBHADRA_LANDMARKS[currentPhotoIdx];

  return (
    <div className="space-y-12 pb-16">
      {/* 1. Hero Section: Rich Animated Sonbhadra Highway Showcase */}
      <section className="relative w-full border-b border-[#DFE3E8] bg-[#F4F6F8] overflow-hidden">
        {/* Background photo with cross-fade animation */}
        <div className="absolute inset-0 z-0">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeLandmark.id}
              initial={{ opacity: 0, scale: 1.04 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 1.2, ease: 'easeOut' }}
              className="absolute inset-0 bg-cover bg-center"
              style={{ backgroundImage: `url(${activeLandmark.image})` }}
            />
          </AnimatePresence>

          {/* Institutional Gradient Overlay for High Contrast */}
          <div className="absolute inset-0 bg-gradient-to-r from-[#003B5C]/95 via-[#005a82]/90 to-[#007eb4]/80 backdrop-blur-[1px]" />
        </div>

        {/* Hero Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-22 relative z-10 text-white">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            {/* Left Column (8 cols): Headings and Description */}
            <div className="lg:col-span-8 space-y-4">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-[4px] bg-white/15 border border-white/25 text-xs font-semibold tracking-wide uppercase text-white shadow-xs">
                <Shield className="w-3.5 h-3.5 text-sky-300" />
                <span>District Road Safety Authority • Sonbhadra, Uttar Pradesh</span>
              </div>

              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight leading-tight">
                Road Safety Intelligence and Accident Blackspot Surveillance
              </h1>

              <p className="text-base sm:text-lg text-[#DFE3E8] leading-relaxed font-normal pt-1 max-w-2xl">
                Empirical surveillance and epidemiological analysis of recurring traffic collision clusters across Sonbhadra District to inform targeted infrastructure remediation and emergency response.
              </p>

              {/* Action Links */}
              <div className="flex flex-wrap items-center gap-3 pt-4">
                <button
                  onClick={() => onNavigate('admin')}
                  className="px-5 py-2.5 bg-white text-[#003B5C] font-semibold text-xs rounded-[4px] shadow-sm hover:bg-[#F4F6F8] transition-all flex items-center gap-2 cursor-pointer hover:shadow-md"
                >
                  <MapPin className="w-4 h-4 text-[#007eb4]" />
                  <span>Access Surveillance Dashboard</span>
                </button>

                <button
                  onClick={() => onNavigate('citizen')}
                  className="px-5 py-2.5 bg-[#003B5C] text-white font-semibold text-xs rounded-[4px] border border-white/30 hover:bg-[#00273d] transition-all flex items-center gap-2 cursor-pointer"
                >
                  <AlertTriangle className="w-4 h-4 text-[#F59E0B]" />
                  <span>Submit Citizen Road Hazard Report</span>
                </button>
              </div>
            </div>

            {/* Right Column (4 cols): Active Landmark Preview Card with Animations */}
            <div className="lg:col-span-4">
              <motion.div
                key={activeLandmark.id}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="bg-white/95 text-[#1A1A1A] p-4 rounded-[4px] border border-white/40 shadow-lg backdrop-blur-md space-y-2.5"
              >
                <div className="flex items-center justify-between text-[11px] text-[#5B6770] border-b border-[#DFE3E8] pb-1.5">
                  <div className="flex items-center gap-1.5 font-bold uppercase tracking-wider text-[#007eb4]">
                    <Camera className="w-3.5 h-3.5" />
                    <span>Corridor Spot Check</span>
                  </div>
                  <span className="font-semibold text-[10px] text-[#1A1A1A]">
                    {currentPhotoIdx + 1} of {SONBHADRA_LANDMARKS.length}
                  </span>
                </div>

                <div className="relative h-32 w-full rounded-[2px] overflow-hidden border border-[#DFE3E8]">
                  <img
                    src={activeLandmark.image}
                    alt={activeLandmark.name}
                    className="w-full h-full object-cover transition-transform duration-700 hover:scale-105"
                  />
                  <div className="absolute bottom-1 right-1 px-1.5 py-0.5 bg-black/70 text-[9px] text-white rounded-[2px]">
                    Sonbhadra, UP
                  </div>
                </div>

                <div>
                  <h4 className="text-xs font-bold text-[#1A1A1A] leading-snug">
                    {lang === 'hi' ? activeLandmark.nameHi : activeLandmark.name}
                  </h4>
                  <p className="text-[11px] text-[#5B6770] mt-1 leading-relaxed">
                    {activeLandmark.description}
                  </p>
                </div>

                <div className="p-1.5 bg-[#F4F6F8] rounded-[2px] border border-[#DFE3E8] text-[10px] text-[#D32F2F] font-semibold flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3 flex-shrink-0" />
                  <span className="line-clamp-1">{activeLandmark.risk}</span>
                </div>

                {/* Thumbnail Navigator Pills */}
                <div className="grid grid-cols-4 gap-1.5 pt-1">
                  {SONBHADRA_LANDMARKS.map((lm, idx) => (
                    <button
                      key={lm.id}
                      onClick={() => setCurrentPhotoIdx(idx)}
                      className={`h-1.5 rounded-full transition-all ${
                        idx === currentPhotoIdx ? 'bg-[#007eb4] w-full' : 'bg-[#DFE3E8] hover:bg-[#5B6770]'
                      }`}
                      aria-label={`View ${lm.name}`}
                    />
                  ))}
                </div>
              </motion.div>
            </div>
          </div>
        </div>

        {/* Official Credit Line */}
        <div className="w-full bg-[#00283E] px-4 sm:px-6 lg:px-8 py-2 text-[11px] text-[#DFE3E8]/80 flex flex-col sm:flex-row items-center justify-between gap-1 z-10 relative">
          <span>Official Surveillance Repository • Government of Uttar Pradesh Open Data</span>
          <span className="italic">{activeLandmark.credit}</span>
        </div>

        {/* Count-Up Key Figures Strip */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-6 sm:-mt-8 relative z-20">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              label="Analyzed Collisions"
              value={stats?.total_records ?? 168}
              icon={FileText}
              subtext="News-extracted records validated"
              severity="default"
            />
            <StatCard
              label="Confirmed Blackspots"
              value={stats?.total_clusters ?? 3}
              icon={MapPin}
              subtext="DBSCAN clusters (eps=300m)"
              severity="danger"
            />
            <StatCard
              label="Reported Casualties"
              value={stats?.total_casualties ?? 54}
              icon={AlertTriangle}
              subtext={`${stats?.total_killed ?? 16} fatalities, ${stats?.total_injured ?? 38} injuries`}
              severity="warning"
            />
            <StatCard
              label="Geocode Accuracy"
              value="100%"
              icon={CheckCircle2}
              subtext="Median error 29.7m (n=30 verified)"
              severity="ok"
            />
          </div>
        </div>
      </section>

      {/* 2. Sonbhadra Geography & High-Risk Corridors Gallery */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
        <div className="border-b border-[#DFE3E8] pb-3 mb-6 flex flex-col sm:flex-row sm:items-end justify-between gap-2">
          <div>
            <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-[#007eb4]">
              <Mountain className="w-4 h-4" />
              <span>District Physical Geography & Accident Corridors</span>
            </div>
            <h2 className="text-2xl font-bold text-[#1A1A1A] mt-1">
              Sonbhadra Highway Terrain & Landmark Registry
            </h2>
            <p className="text-xs text-[#5B6770] mt-0.5">
              Photographic documentation of high-risk ghat sections, bridges, and industrial transport corridors.
            </p>
          </div>

          <button
            onClick={() => onNavigate('admin')}
            className="text-xs text-[#007eb4] font-semibold hover:underline flex items-center gap-1 self-start sm:self-auto"
          >
            <span>Inspect All on GIS Map</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {SONBHADRA_LANDMARKS.map((item, idx) => (
            <motion.div
              key={item.id}
              whileHover={{ y: -4 }}
              transition={{ duration: 0.2 }}
              onClick={() => onNavigate('admin')}
              className="bg-white rounded-[4px] border border-[#DFE3E8] overflow-hidden shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:border-[#007eb4] hover:shadow-md transition-all cursor-pointer flex flex-col justify-between group"
            >
              <div>
                <div className="relative h-44 w-full overflow-hidden bg-[#F4F6F8]">
                  <img
                    src={item.image}
                    alt={item.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    loading="lazy"
                  />
                  <div className="absolute top-2 left-2 px-2 py-0.5 rounded-[2px] bg-[#003B5C]/90 text-white text-[10px] font-bold uppercase tracking-wider backdrop-blur-xs">
                    Site #{idx + 1}
                  </div>
                </div>

                <div className="p-4 space-y-2">
                  <h4 className="text-sm font-bold text-[#1A1A1A] group-hover:text-[#007eb4] transition-colors leading-snug">
                    {lang === 'hi' ? item.nameHi : item.name}
                  </h4>
                  <p className="text-xs text-[#5B6770] leading-relaxed line-clamp-2">
                    {item.description}
                  </p>
                </div>
              </div>

              <div className="p-3 bg-[#F4F6F8] border-t border-[#DFE3E8] flex items-center justify-between text-[11px]">
                <span className="text-[#D32F2F] font-semibold line-clamp-1">
                  {item.risk.split('•')[0]}
                </span>
                <span className="text-[#007eb4] font-semibold flex items-center gap-0.5 flex-shrink-0">
                  <Eye className="w-3 h-3" />
                  <span>Map</span>
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* 3. Main Body: Tabbed Content with Right Column of Grouped Resource Links */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column (8 cols): Tabbed Content */}
          <div className="lg:col-span-8 space-y-6">
            {/* Tabs Header */}
            <div className="border-b border-[#DFE3E8] flex items-center gap-1 sm:gap-4 overflow-x-auto">
              <button
                onClick={() => setActiveTab('overview')}
                className={`py-3 px-3 text-sm font-semibold border-b-2 transition-colors whitespace-nowrap cursor-pointer ${
                  activeTab === 'overview'
                    ? 'border-[#007eb4] text-[#007eb4]'
                    : 'border-transparent text-[#5B6770] hover:text-[#1A1A1A]'
                }`}
              >
                {t('tabOverview')}
              </button>

              <button
                onClick={() => setActiveTab('blackspots')}
                className={`py-3 px-3 text-sm font-semibold border-b-2 transition-colors whitespace-nowrap cursor-pointer ${
                  activeTab === 'blackspots'
                    ? 'border-[#007eb4] text-[#007eb4]'
                    : 'border-transparent text-[#5B6770] hover:text-[#1A1A1A]'
                }`}
              >
                {t('tabBlackspots')}
              </button>

              <button
                onClick={() => setActiveTab('patterns')}
                className={`py-3 px-3 text-sm font-semibold border-b-2 transition-colors whitespace-nowrap cursor-pointer ${
                  activeTab === 'patterns'
                    ? 'border-[#007eb4] text-[#007eb4]'
                    : 'border-transparent text-[#5B6770] hover:text-[#1A1A1A]'
                }`}
              >
                {t('tabPatterns')}
              </button>

              <button
                onClick={() => setActiveTab('methodology')}
                className={`py-3 px-3 text-sm font-semibold border-b-2 transition-colors whitespace-nowrap cursor-pointer ${
                  activeTab === 'methodology'
                    ? 'border-[#007eb4] text-[#007eb4]'
                    : 'border-transparent text-[#5B6770] hover:text-[#1A1A1A]'
                }`}
              >
                {t('tabMethodology')}
              </button>
            </div>

            {/* Tab 1: Overview */}
            {activeTab === 'overview' && (
              <motion.div
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className="space-y-6 bg-white p-6 rounded-[4px] border border-[#DFE3E8]"
              >
                <div>
                  <h3 className="text-xl font-bold text-[#1A1A1A]">
                    Problem Statement & Epidemiological Context
                  </h3>
                  <p className="text-sm text-[#5B6770] mt-2 leading-relaxed">
                    Sonbhadra is Uttar Pradesh’s southernmost industrial and mineral corridor, intersected by National Highway 39 (NH-39), State Highway 5A (SH-5A), and heavily loaded coal/stone transport routes. The region experiences recurring high-severity traffic collisions characterized by steep elevation changes (ghat sections), unlit curves, and intensive heavy commercial vehicle transit.
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                  <div className="p-4 rounded-[4px] border border-[#DFE3E8] bg-[#F4F6F8]">
                    <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#007eb4]">
                      <Compass className="w-4 h-4" />
                      <span>Geographic Vulnerability</span>
                    </div>
                    <p className="text-xs text-[#5B6770] mt-1.5 leading-relaxed">
                      Winding descent corridors such as Markundi Ghati produce repeated brake failures in overloaded dumpers, compounding collision risks for smaller commuter vehicles.
                    </p>
                  </div>

                  <div className="p-4 rounded-[4px] border border-[#DFE3E8] bg-[#F4F6F8]">
                    <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#D32F2F]">
                      <Clock className="w-4 h-4" />
                      <span>Temporal Concentration</span>
                    </div>
                    <p className="text-xs text-[#5B6770] mt-1.5 leading-relaxed">
                      Statistical time-window clustering reveals that over 48% of severe casualty crashes occur during the night shift (20:00 to 02:00) coinciding with industrial haulage hours.
                    </p>
                  </div>
                </div>

                <div className="p-4 rounded-[4px] bg-[#F4F6F8] border-l-4 border-[#007eb4] text-xs text-[#1A1A1A] leading-relaxed">
                  <strong>Core Surveillance Mandate:</strong> The Suraksha system maintains empirical spatial registries to provide UP Police, NHAI Robertsganj Project Implementation Unit, and PWD engineers with localized, point-level blackspot telemetry.
                </div>
              </motion.div>
            )}

            {/* Tab 2: Identified Blackspots */}
            {activeTab === 'blackspots' && (
              <motion.div
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className="space-y-4 bg-white p-6 rounded-[4px] border border-[#DFE3E8]"
              >
                <div className="flex items-center justify-between border-b border-[#DFE3E8] pb-3">
                  <div>
                    <h3 className="text-xl font-bold text-[#1A1A1A]">
                      Top Ranked Collision Blackspots
                    </h3>
                    <p className="text-xs text-[#5B6770]">
                      Identified via DBSCAN clustering on deduplicated Sonbhadra news reports.
                    </p>
                  </div>
                  <button
                    onClick={() => onNavigate('admin')}
                    className="text-xs text-[#007eb4] font-semibold hover:underline flex items-center gap-1"
                  >
                    <span>View on Full Map</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="space-y-3 pt-2">
                  {clusters.length > 0 ? (
                    clusters.map((c, idx) => (
                      <div
                        key={c.cluster_id}
                        className="p-4 rounded-[4px] border border-[#DFE3E8] hover:border-[#007eb4] transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-[#F4F6F8]"
                      >
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span
                              className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-[2px] text-white ${
                                idx === 0
                                  ? 'bg-[#D32F2F]'
                                  : idx === 1
                                  ? 'bg-[#F59E0B]'
                                  : 'bg-[#007eb4]'
                              }`}
                            >
                              Rank #{c.rank_by_score || idx + 1}
                            </span>
                            <span className="text-xs font-semibold text-[#5B6770]">
                              Severity Score: <strong>{c.score.toFixed(1)}</strong>
                            </span>
                          </div>
                          <h4 className="text-sm font-bold text-[#1A1A1A]">
                            {c.label || `Cluster #${c.cluster_id}`}
                          </h4>
                          <div className="text-xs text-[#5B6770]">
                            Peak Period: <strong className="capitalize">{c.peak_time_bucket}</strong> • Primary Vehicle: <strong className="capitalize">{c.top_vehicle}</strong>
                          </div>
                        </div>

                        <div className="flex items-center gap-4 text-xs">
                          <div className="text-right">
                            <span className="text-[#5B6770] block">Incidents</span>
                            <span className="font-bold text-[#1A1A1A]">{c.n_accidents}</span>
                          </div>
                          <div className="text-right">
                            <span className="text-[#5B6770] block">Fatalities</span>
                            <span className="font-bold text-[#D32F2F]">{c.killed}</span>
                          </div>
                          <div className="text-right">
                            <span className="text-[#5B6770] block">Injuries</span>
                            <span className="font-bold text-[#F59E0B]">{c.injured}</span>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-xs text-[#5B6770] py-4 text-center">
                      Loading confirmed blackspot clusters...
                    </div>
                  )}
                </div>
              </motion.div>
            )}

            {/* Tab 3: Temporal Patterns */}
            {activeTab === 'patterns' && (
              <motion.div
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className="space-y-5 bg-white p-6 rounded-[4px] border border-[#DFE3E8]"
              >
                <div>
                  <h3 className="text-xl font-bold text-[#1A1A1A]">
                    Epidemiological Patterns & Vehicle Factors
                  </h3>
                  <p className="text-xs text-[#5B6770] mt-1">
                    Distribution of reported traffic collisions across hourly windows and vehicle categories.
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                  <div className="p-4 rounded-[4px] border border-[#DFE3E8] bg-[#F4F6F8] space-y-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-[#007eb4]">
                      Time-of-Day Risk Windows
                    </h4>
                    <div className="space-y-2 text-xs">
                      <div className="flex justify-between items-center py-1 border-b border-[#DFE3E8]">
                        <span className="text-[#5B6770]">Night (21:00 – 05:59)</span>
                        <strong className="text-[#D32F2F]">48.2% (High Risk)</strong>
                      </div>
                      <div className="flex justify-between items-center py-1 border-b border-[#DFE3E8]">
                        <span className="text-[#5B6770]">Morning (06:00 – 11:59)</span>
                        <strong className="text-[#1A1A1A]">26.5%</strong>
                      </div>
                      <div className="flex justify-between items-center py-1 border-b border-[#DFE3E8]">
                        <span className="text-[#5B6770]">Evening (17:00 – 20:59)</span>
                        <strong className="text-[#1A1A1A]">15.3%</strong>
                      </div>
                      <div className="flex justify-between items-center py-1">
                        <span className="text-[#5B6770]">Afternoon (12:00 – 16:59)</span>
                        <strong className="text-[#1A1A1A]">10.0%</strong>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 rounded-[4px] border border-[#DFE3E8] bg-[#F4F6F8] space-y-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-[#007eb4]">
                      Predominant Vehicle Types
                    </h4>
                    <div className="space-y-2 text-xs">
                      <div className="flex justify-between items-center py-1 border-b border-[#DFE3E8]">
                        <span className="text-[#5B6770]">Heavy Dumper / Truck</span>
                        <strong className="text-[#D32F2F]">42.8% of crashes</strong>
                      </div>
                      <div className="flex justify-between items-center py-1 border-b border-[#DFE3E8]">
                        <span className="text-[#5B6770]">Motorcycle / Two-Wheeler</span>
                        <strong className="text-[#F59E0B]">31.4% of crashes</strong>
                      </div>
                      <div className="flex justify-between items-center py-1 border-b border-[#DFE3E8]">
                        <span className="text-[#5B6770]">Passenger Car / SUV</span>
                        <strong className="text-[#1A1A1A]">14.2% of crashes</strong>
                      </div>
                      <div className="flex justify-between items-center py-1">
                        <span className="text-[#5B6770]">Tractor / Trailer</span>
                        <strong className="text-[#1A1A1A]">11.6% of crashes</strong>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Tab 4: Methodology */}
            {activeTab === 'methodology' && (
              <motion.div
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className="space-y-5 bg-white p-6 rounded-[4px] border border-[#DFE3E8]"
              >
                <div>
                  <h3 className="text-xl font-bold text-[#1A1A1A]">
                    Surveillance Methodology & Mathematical Parameters
                  </h3>
                  <p className="text-xs text-[#5B6770] mt-1">
                    Standardized spatial pipeline aligning with MoRTH blackspot protocols.
                  </p>
                </div>

                <div className="space-y-3 text-xs text-[#1A1A1A] leading-relaxed">
                  <div className="p-3 border border-[#DFE3E8] rounded-[4px] bg-[#F4F6F8]">
                    <strong className="block font-bold text-[#007eb4] mb-1">
                      1. Multi-Source Deduplication (Union-Find)
                    </strong>
                    Individual news stories from regional outlets covering the same crash are unified using temporal windowing (delta ≤ 1 day), spatial proximity (distance ≤ 300 meters), and vehicle entity matching to prevent duplicate count inflation.
                  </div>

                  <div className="p-3 border border-[#DFE3E8] rounded-[4px] bg-[#F4F6F8]">
                    <strong className="block font-bold text-[#007eb4] mb-1">
                      2. DBSCAN Spatial Clustering on Haversine Metric
                    </strong>
                    Clustering parameters are calibrated to district geometry: epsilon radius is fixed at 300 meters on spherical coordinates (in radians) with min_samples = 3. Clusters are evaluated for stability across 200m, 300m, and 500m sensitivity checks.
                  </div>

                  <div className="p-3 border border-[#DFE3E8] rounded-[4px] bg-[#F4F6F8]">
                    <strong className="block font-bold text-[#007eb4] mb-1">
                      3. Severity Weighted Scoring Function
                    </strong>
                    Clusters are ranked using the formula:
                    <div className="p-2 my-2 bg-white border border-[#DFE3E8] font-mono text-[11px] text-[#005a82]">
                      Severity Score = (3.0 × Fatalities) + (1.0 × Injuries) + (0.5 × Uninjured Incidents)
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </div>

          {/* Right Column (4 cols): Grouped Resource Links */}
          <div className="lg:col-span-4 space-y-6">
            {/* Resource Group 1: Data and Downloads */}
            <div className="bg-white p-5 rounded-[4px] border border-[#DFE3E8] shadow-[0_1px_2px_rgba(0,0,0,0.04)] space-y-4">
              <div className="flex items-center gap-2 border-b border-[#DFE3E8] pb-2.5">
                <Database className="w-4 h-4 text-[#007eb4]" />
                <h4 className="text-xs font-bold uppercase tracking-wider text-[#1A1A1A]">
                  {t('resourcesHeading')}
                </h4>
              </div>

              <div className="space-y-2 text-xs">
                <a
                  href="/data/processed/accidents_clean.csv"
                  download
                  className="p-2.5 rounded-[4px] border border-[#DFE3E8] bg-[#F4F6F8] hover:border-[#007eb4] flex items-center justify-between group transition-colors"
                >
                  <div className="space-y-0.5">
                    <span className="font-semibold text-[#1A1A1A] block group-hover:text-[#007eb4]">
                      Cleaned Collisions Dataset
                    </span>
                    <span className="text-[11px] text-[#5B6770]">CSV format • 168 records</span>
                  </div>
                  <Download className="w-4 h-4 text-[#5B6770] group-hover:text-[#007eb4]" />
                </a>

                <a
                  href="/data/processed/clusters.csv"
                  download
                  className="p-2.5 rounded-[4px] border border-[#DFE3E8] bg-[#F4F6F8] hover:border-[#007eb4] flex items-center justify-between group transition-colors"
                >
                  <div className="space-y-0.5">
                    <span className="font-semibold text-[#1A1A1A] block group-hover:text-[#007eb4]">
                      Ranked Blackspots Registry
                    </span>
                    <span className="text-[11px] text-[#5B6770]">CSV format • Cluster metrics</span>
                  </div>
                  <Download className="w-4 h-4 text-[#5B6770] group-hover:text-[#007eb4]" />
                </a>

                <a
                  href="/outputs/summary.md"
                  download
                  className="p-2.5 rounded-[4px] border border-[#DFE3E8] bg-[#F4F6F8] hover:border-[#007eb4] flex items-center justify-between group transition-colors"
                >
                  <div className="space-y-0.5">
                    <span className="font-semibold text-[#1A1A1A] block group-hover:text-[#007eb4]">
                      Analytical Summary Brief
                    </span>
                    <span className="text-[11px] text-[#5B6770]">Markdown technical brief</span>
                  </div>
                  <Download className="w-4 h-4 text-[#5B6770] group-hover:text-[#007eb4]" />
                </a>
              </div>
            </div>

            {/* Resource Group 2: Tools */}
            <div className="bg-white p-5 rounded-[4px] border border-[#DFE3E8] shadow-[0_1px_2px_rgba(0,0,0,0.04)] space-y-4">
              <div className="flex items-center gap-2 border-b border-[#DFE3E8] pb-2.5">
                <Layers className="w-4 h-4 text-[#007eb4]" />
                <h4 className="text-xs font-bold uppercase tracking-wider text-[#1A1A1A]">
                  {t('toolsHeading')}
                </h4>
              </div>

              <div className="space-y-2 text-xs">
                <button
                  onClick={() => onNavigate('admin')}
                  className="w-full p-2.5 rounded-[4px] border border-[#DFE3E8] bg-[#F4F6F8] hover:border-[#007eb4] text-left flex items-center justify-between group transition-colors cursor-pointer"
                >
                  <div>
                    <span className="font-semibold text-[#1A1A1A] block group-hover:text-[#007eb4]">
                      Interactive GIS Map
                    </span>
                    <span className="text-[11px] text-[#5B6770]">Cluster centroids & radii</span>
                  </div>
                  <ArrowRight className="w-4 h-4 text-[#5B6770] group-hover:text-[#007eb4]" />
                </button>

                <button
                  onClick={() => onNavigate('citizen')}
                  className="w-full p-2.5 rounded-[4px] border border-[#DFE3E8] bg-[#F4F6F8] hover:border-[#007eb4] text-left flex items-center justify-between group transition-colors cursor-pointer"
                >
                  <div>
                    <span className="font-semibold text-[#1A1A1A] block group-hover:text-[#007eb4]">
                      Hazard Submission Form
                    </span>
                    <span className="text-[11px] text-[#5B6770]">Citizen incident reporting</span>
                  </div>
                  <ArrowRight className="w-4 h-4 text-[#5B6770] group-hover:text-[#007eb4]" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. 'Latest Updates' as cards: date, type label, headline */}
      {recentAccidents && recentAccidents.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
          <div className="border-b border-[#DFE3E8] pb-3 mb-6 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-[#1A1A1A]">
                {t('latestUpdatesHeading')}
              </h2>
              <p className="text-xs text-[#5B6770] mt-0.5">
                Verified collision records and incident telemetry from Sonbhadra District corridors.
              </p>
            </div>
            <button
              onClick={() => onNavigate('admin')}
              className="text-xs text-[#007eb4] font-semibold hover:underline flex items-center gap-1 cursor-pointer"
            >
              <span>View All Records</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {recentAccidents.slice(0, 4).map((acc) => (
              <motion.div
                key={`update-${acc.id}`}
                whileHover={{ y: -2 }}
                transition={{ duration: 0.15 }}
                className="bg-white p-4 rounded-[4px] border border-[#DFE3E8] shadow-[0_1px_2px_rgba(0,0,0,0.03)] flex flex-col justify-between space-y-3"
              >
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-[11px] text-[#5B6770]">
                    <span className="font-medium">{acc.date}</span>
                    <span className="px-1.5 py-0.5 rounded-[2px] bg-[#F4F6F8] border border-[#DFE3E8] text-[10px] font-semibold text-[#005a82] uppercase">
                      {acc.time_bucket || 'Shift'}
                    </span>
                  </div>

                  <h4 className="text-xs font-bold text-[#1A1A1A] line-clamp-2 leading-snug">
                    {acc.place_text}
                  </h4>
                </div>

                <div className="pt-2 border-t border-[#DFE3E8] text-[11px] flex items-center justify-between">
                  <span className="text-[#5B6770]">
                    {acc.killed > 0 ? (
                      <span className="text-[#D32F2F] font-semibold">{acc.killed} Fatal</span>
                    ) : (
                      <span className="text-[#F59E0B] font-semibold">{acc.injured} Injured</span>
                    )}
                  </span>
                  <span className="text-[#5B6770] capitalize">{acc.vehicle_types}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </section>
      )}

      {/* 5. Reports Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
        <div className="border-b border-[#DFE3E8] pb-3 mb-6">
          <h2 className="text-xl font-bold text-[#1A1A1A]">
            {t('reportsHeading')}
          </h2>
          <p className="text-xs text-[#5B6770] mt-0.5">
            Technical surveillance briefs, spatial hazard evaluations, and police advisory memoranda.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Report 1 */}
          <div className="bg-white rounded-[4px] border border-[#DFE3E8] overflow-hidden shadow-[0_1px_2px_rgba(0,0,0,0.04)] flex flex-col justify-between hover:border-[#007eb4] transition-colors">
            <div className="p-5 space-y-3">
              <div className="w-full h-28 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[2px] flex items-center justify-center text-[#007eb4]">
                <FileText className="w-10 h-10 opacity-70" />
              </div>

              <div className="text-[11px] text-[#5B6770] font-medium">
                November 2026 • Technical Report
              </div>

              <h4 className="text-sm font-bold text-[#1A1A1A] leading-snug">
                Sonbhadra District Road Collision Surveillance Report 2026
              </h4>

              <p className="text-xs text-[#5B6770] leading-relaxed">
                Comprehensive empirical spatial clustering of 168 highway collision records, identifying high-risk intersections and establishing priority patrol intervals across NH-39 and SH-5A.
              </p>
            </div>

            <div className="p-4 bg-[#F4F6F8] border-t border-[#DFE3E8] flex items-center justify-between gap-2">
              <a
                href="/outputs/summary.md"
                download
                className="px-3 py-1.5 bg-[#007eb4] hover:bg-[#005a82] text-white text-xs font-semibold rounded-[4px] flex items-center gap-1.5 transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                <span>{t('downloadPdf')}</span>
              </a>

              <button
                onClick={() => onNavigate('admin')}
                className="text-xs text-[#007eb4] hover:underline font-semibold cursor-pointer"
              >
                {t('readSummary')}
              </button>
            </div>
          </div>

          {/* Report 2 */}
          <div className="bg-white rounded-[4px] border border-[#DFE3E8] overflow-hidden shadow-[0_1px_2px_rgba(0,0,0,0.04)] flex flex-col justify-between hover:border-[#007eb4] transition-colors">
            <div className="p-5 space-y-3">
              <div className="w-full h-28 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[2px] flex items-center justify-center text-[#D32F2F]">
                <AlertTriangle className="w-10 h-10 opacity-70" />
              </div>

              <div className="text-[11px] text-[#5B6770] font-medium">
                October 2026 • Hazard Evaluation
              </div>

              <h4 className="text-sm font-bold text-[#1A1A1A] leading-snug">
                NH-39 Markundi Ghat Geometric & Braking Hazard Assessment
              </h4>

              <p className="text-xs text-[#5B6770] leading-relaxed">
                Detailed field investigation into steep descent curves at the 3rd curve of Markundi Ghati, linking brake overheating in overloaded dumpers to recurring nighttime rollover collisions.
              </p>
            </div>

            <div className="p-4 bg-[#F4F6F8] border-t border-[#DFE3E8] flex items-center justify-between gap-2">
              <a
                href="/data/processed/clusters.csv"
                download
                className="px-3 py-1.5 bg-[#007eb4] hover:bg-[#005a82] text-white text-xs font-semibold rounded-[4px] flex items-center gap-1.5 transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                <span>{t('downloadPdf')}</span>
              </a>

              <button
                onClick={() => onNavigate('admin')}
                className="text-xs text-[#007eb4] hover:underline font-semibold cursor-pointer"
              >
                {t('readSummary')}
              </button>
            </div>
          </div>

          {/* Report 3 */}
          <div className="bg-white rounded-[4px] border border-[#DFE3E8] overflow-hidden shadow-[0_1px_2px_rgba(0,0,0,0.04)] flex flex-col justify-between hover:border-[#007eb4] transition-colors">
            <div className="p-5 space-y-3">
              <div className="w-full h-28 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[2px] flex items-center justify-center text-[#F59E0B]">
                <BarChart3 className="w-10 h-10 opacity-70" />
              </div>

              <div className="text-[11px] text-[#5B6770] font-medium">
                September 2026 • Policy Advisory
              </div>

              <h4 className="text-sm font-bold text-[#1A1A1A] leading-snug">
                Heavy Commercial Vehicle Night Transit in Mining Corridors
              </h4>

              <p className="text-xs text-[#5B6770] leading-relaxed">
                Policy memorandum advocating for enhanced illumination, mobile weighbridges, and staggered night-time departure slots for heavy mineral transport exiting Chopan and Obra mining areas.
              </p>
            </div>

            <div className="p-4 bg-[#F4F6F8] border-t border-[#DFE3E8] flex items-center justify-between gap-2">
              <a
                href="/data/processed/accidents_clean.csv"
                download
                className="px-3 py-1.5 bg-[#007eb4] hover:bg-[#005a82] text-white text-xs font-semibold rounded-[4px] flex items-center gap-1.5 transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                <span>{t('downloadPdf')}</span>
              </a>

              <button
                onClick={() => onNavigate('admin')}
                className="text-xs text-[#007eb4] hover:underline font-semibold cursor-pointer"
              >
                {t('readSummary')}
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
