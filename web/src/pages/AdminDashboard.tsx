import React, { useEffect, useState, useMemo } from 'react';
import { useThemeLanguage } from '../context/ThemeLanguageContext';
import { Breadcrumb } from '../components/Breadcrumb';
import {
  getAccidentsApi,
  getAdminReportsApi,
  getClustersApi,
  getStatsApi,
  updateReportStatusApi,
} from '../services/api';
import type { Accident, CitizenReport, Cluster, Stats } from '../types';
import { StatCard } from '../components/StatCard';
import { BlackspotMap } from '../components/BlackspotMap';
import {
  FileText,
  MapPin,
  AlertTriangle,
  Clock,
  Download,
  Filter,
  CheckCircle2,
  XCircle,
  Inbox,
  ArrowUpDown,
  Layers,
  Shield,
  RotateCcw,
} from 'lucide-react';

interface AdminDashboardProps {
  onNavigateHome?: () => void;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ onNavigateHome }) => {
  const { t } = useThemeLanguage();

  // Data states
  const [stats, setStats] = useState<Stats | null>(null);
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [accidents, setAccidents] = useState<Accident[]>([]);
  const [reports, setReports] = useState<CitizenReport[]>([]);

  // Filter states
  const [timeBucket, setTimeBucket] = useState('All');
  const [selectedVehicle, setSelectedVehicle] = useState('All');
  const [minSeverity, setMinSeverity] = useState(0);
  const [selectedClusterId, setSelectedClusterId] = useState<number | null>(null);

  // Sorting state for table
  const [sortField, setSortField] = useState<'rank_by_score' | 'score' | 'n_accidents' | 'killed'>('rank_by_score');
  const [sortAsc, setSortAsc] = useState(true);

  // Action message state
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [s, c, a, r] = await Promise.all([
          getStatsApi(),
          getClustersApi(),
          getAccidentsApi(),
          getAdminReportsApi().catch(() => []),
        ]);
        setStats(s);
        setClusters(c);
        setAccidents(a);
        setReports(r);
      } catch (err) {
        console.error('Error loading dashboard data', err);
      }
    }
    loadData();
  }, []);

  // Filtered clusters by minimum severity
  const filteredClusters = useMemo(() => {
    return clusters.filter((c) => c.score >= minSeverity);
  }, [clusters, minSeverity]);

  // Filtered accidents
  const filteredAccidents = useMemo(() => {
    return accidents.filter((acc) => {
      if (timeBucket !== 'All' && acc.time_bucket.toLowerCase() !== timeBucket.toLowerCase()) return false;
      if (selectedVehicle !== 'All') {
        const vParts = acc.vehicle_types.toLowerCase().replace(/,/g, ';').split(';');
        if (!vParts.includes(selectedVehicle.toLowerCase())) return false;
      }
      return true;
    });
  }, [accidents, timeBucket, selectedVehicle]);

  // Sorted clusters for Table
  const sortedClusters = useMemo(() => {
    return [...filteredClusters].sort((a, b) => {
      const valA = a[sortField];
      const valB = b[sortField];
      return sortAsc ? (valA > valB ? 1 : -1) : valA < valB ? 1 : -1;
    });
  }, [filteredClusters, sortField, sortAsc]);

  const handleSort = (field: 'rank_by_score' | 'score' | 'n_accidents' | 'killed') => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(true);
    }
  };

  const resetFilters = () => {
    setTimeBucket('All');
    setSelectedVehicle('All');
    setMinSeverity(0);
    setSelectedClusterId(null);
  };

  // CSV Export
  const exportToCSV = () => {
    const headers = [
      'Rank',
      'Landmark',
      'Incidents',
      'Killed',
      'Injured',
      'Severity Score',
      'Peak Time',
      'Primary Vehicle',
      'Recommended Action Plan',
      'Centroid Lat',
      'Centroid Lon',
    ];
    const rows = sortedClusters.map((c) => [
      c.rank_by_score,
      `"${c.label.replace(/"/g, '""')}"`,
      c.n_accidents,
      c.killed,
      c.injured,
      c.score.toFixed(1),
      c.peak_time_bucket,
      c.top_vehicle,
      `"${(c.recommended_action || 'Road markings and regular patrol rotation.').replace(/"/g, '""')}"`,
      c.centroid_lat,
      c.centroid_lon,
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `sonbhadra_blackspots_patrol_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Handle report approval/rejection
  const handleReportAction = async (reportId: number, newStatus: 'approved' | 'rejected') => {
    try {
      await updateReportStatusApi(reportId, newStatus);
      setActionFeedback(`Report #${reportId} has been ${newStatus}. Dataset synchronized.`);
      const updatedReports = await getAdminReportsApi();
      setReports(updatedReports);
      const [newStats, newAccidents] = await Promise.all([getStatsApi(), getAccidentsApi()]);
      setStats(newStats);
      setAccidents(newAccidents);
      setTimeout(() => setActionFeedback(null), 5000);
    } catch (err: any) {
      setActionFeedback(`Action failed: ${err.message}`);
    }
  };

  return (
    <div className="w-full space-y-6 pb-16">
      {/* Breadcrumb under nav on every inner page as required */}
      <Breadcrumb
        items={[
          { label: 'Home', onClick: onNavigateHome },
          { label: 'Road Safety Intelligence', onClick: onNavigateHome },
          { label: 'Surveillance Dashboard', active: true },
        ]}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#DFE3E8] pb-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#007eb4]">
              <Shield className="w-4 h-4" />
              <span>District Police & Transport Command Surveillance</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-[#1A1A1A] mt-1">
              Sonbhadra Blackspot Intelligence Dashboard
            </h1>
            <p className="text-xs text-[#5B6770] mt-0.5">
              Empirical spatial DBSCAN clusters across NH-39, Chopan Bridge, and Robertsganj mining routes.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={exportToCSV}
              className="px-4 py-2 bg-[#007eb4] hover:bg-[#005a82] text-white text-xs font-semibold rounded-[4px] flex items-center gap-2 shadow-xs transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>{t('exportCsv')}</span>
            </button>
          </div>
        </div>

        {/* Action feedback banner */}
        {actionFeedback && (
          <div className="p-3 bg-emerald-50 border border-[#2E7D32] text-xs text-[#2E7D32] rounded-[4px] flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
            <span>{actionFeedback}</span>
          </div>
        )}

        {/* KPI Metrics Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="Analyzed News Collisions"
            value={stats?.total_records ?? accidents.length}
            icon={FileText}
            subtext="Validated point-level records"
          />
          <StatCard
            label="Active Blackspot Zones"
            value={filteredClusters.length}
            icon={MapPin}
            subtext="Clusters with eps ≤ 300m"
            severity="danger"
          />
          <StatCard
            label="Total Casualties"
            value={stats?.total_casualties ?? 0}
            icon={AlertTriangle}
            subtext={`${stats?.total_killed ?? 0} deaths, ${stats?.total_injured ?? 0} injured`}
            severity="warning"
          />
          <StatCard
            label="High-Risk Shift"
            value={stats?.peak_time_window ?? 'Night'}
            icon={Clock}
            subtext="48.2% collision share"
            severity="ok"
          />
        </div>

        {/* 8. Dashboard Layout: Filter Panel on Left, Light Map in Center, Ranked Blackspot List on Right */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column (3 cols): Filter Panel */}
          <div className="lg:col-span-3 bg-white p-5 rounded-[4px] border border-[#DFE3E8] shadow-[0_1px_2px_rgba(0,0,0,0.03)] space-y-4">
            <div className="flex items-center justify-between border-b border-[#DFE3E8] pb-3">
              <div className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-[#007eb4]" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-[#1A1A1A]">
                  Filter Parameters
                </h3>
              </div>
              <button
                onClick={resetFilters}
                className="text-[11px] text-[#5B6770] hover:text-[#007eb4] flex items-center gap-1"
                title="Reset all filters"
              >
                <RotateCcw className="w-3 h-3" />
                <span>Reset</span>
              </button>
            </div>

            {/* Time of Day */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-[#1A1A1A]">
                Time Window / Shift
              </label>
              <select
                value={timeBucket}
                onChange={(e) => setTimeBucket(e.target.value)}
                className="w-full p-2 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[4px] text-xs text-[#1A1A1A] focus:outline-none focus:border-[#007eb4]"
              >
                <option value="All">All Time Windows</option>
                <option value="Morning">Morning (06:00 – 11:59)</option>
                <option value="Afternoon">Afternoon (12:00 – 16:59)</option>
                <option value="Evening">Evening (17:00 – 20:59)</option>
                <option value="Night">Night (21:00 – 05:59)</option>
              </select>
            </div>

            {/* Vehicle Involved */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-[#1A1A1A]">
                Vehicle Classification
              </label>
              <select
                value={selectedVehicle}
                onChange={(e) => setSelectedVehicle(e.target.value)}
                className="w-full p-2 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[4px] text-xs text-[#1A1A1A] focus:outline-none focus:border-[#007eb4]"
              >
                <option value="All">All Vehicle Types</option>
                <option value="truck">Truck / Dumper / Trailer</option>
                <option value="bike">Motorcycle / Two-Wheeler</option>
                <option value="car">Car / Jeep / SUV</option>
                <option value="tractor">Tractor / Agricultural</option>
                <option value="bus">Passenger Bus</option>
              </select>
            </div>

            {/* Severity Threshold Slider */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center text-xs">
                <label className="font-semibold text-[#1A1A1A]">Min Severity Score</label>
                <span className="font-bold text-[#007eb4]">{minSeverity}</span>
              </div>
              <input
                type="range"
                min="0"
                max="50"
                step="5"
                value={minSeverity}
                onChange={(e) => setMinSeverity(Number(e.target.value))}
                className="w-full accent-[#007eb4] cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-[#5B6770]">
                <span>0 (All)</span>
                <span>25</span>
                <span>50+ (Critical)</span>
              </div>
            </div>

            {/* Filter Summary */}
            <div className="p-3 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[4px] text-[11px] text-[#5B6770] space-y-1">
              <div>
                Matching Incidents: <strong className="text-[#1A1A1A]">{filteredAccidents.length}</strong>
              </div>
              <div>
                Qualified Blackspots: <strong className="text-[#1A1A1A]">{filteredClusters.length}</strong>
              </div>
            </div>
          </div>

          {/* Center Column (6 cols): Light Map */}
          <div className="lg:col-span-6 bg-white p-4 rounded-[4px] border border-[#DFE3E8] shadow-[0_1px_2px_rgba(0,0,0,0.03)] space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-[#007eb4]" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-[#1A1A1A]">
                  Spatial Blackspot Map (OpenStreetMap)
                </h3>
              </div>
              <span className="text-[11px] text-[#5B6770]">
                Sonbhadra District, UP
              </span>
            </div>

            <BlackspotMap
              clusters={filteredClusters}
              accidents={filteredAccidents}
              selectedClusterId={selectedClusterId}
              onSelectCluster={(id) => setSelectedClusterId(id)}
              height="500px"
            />
          </div>

          {/* Right Column (3 cols): Ranked Blackspot List */}
          <div className="lg:col-span-3 bg-white p-5 rounded-[4px] border border-[#DFE3E8] shadow-[0_1px_2px_rgba(0,0,0,0.03)] space-y-4">
            <div className="flex items-center justify-between border-b border-[#DFE3E8] pb-3">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-[#007eb4]" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-[#1A1A1A]">
                  Ranked Blackspots
                </h3>
              </div>
              <span className="text-xs text-[#5B6770] font-semibold">
                {filteredClusters.length} sites
              </span>
            </div>

            <div className="space-y-2.5 max-h-[480px] overflow-y-auto pr-1">
              {filteredClusters.map((cluster) => {
                const isSelected = selectedClusterId === cluster.cluster_id;
                const rank = cluster.rank_by_score || 1;
                const badgeColor =
                  rank <= 3 ? 'bg-[#D32F2F]' : rank <= 6 ? 'bg-[#F59E0B]' : 'bg-[#007eb4]';

                return (
                  <button
                    key={`list-${cluster.cluster_id}`}
                    onClick={() => setSelectedClusterId(cluster.cluster_id)}
                    className={`w-full text-left p-3 rounded-[4px] border transition-colors ${
                      isSelected
                        ? 'border-[#007eb4] bg-[#F4F6F8]'
                        : 'border-[#DFE3E8] hover:border-[#007eb4] bg-white'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-1 mb-1">
                      <span className={`text-[10px] font-bold uppercase px-1.5 py-0.5 rounded-[2px] text-white ${badgeColor}`}>
                        Rank #{rank}
                      </span>
                      <span className="text-[11px] font-semibold text-[#5B6770]">
                        Score: <strong>{cluster.score.toFixed(1)}</strong>
                      </span>
                    </div>

                    <h4 className="text-xs font-bold text-[#1A1A1A] line-clamp-1">
                      {cluster.label || `Cluster ${cluster.cluster_id}`}
                    </h4>

                    <div className="text-[11px] text-[#5B6770] mt-1 flex items-center justify-between">
                      <span>{cluster.n_accidents} crashes</span>
                      <span className="text-[#D32F2F] font-semibold">{cluster.killed} killed</span>
                      <span className="capitalize">{cluster.peak_time_bucket}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Bottom Section 1: Data Table with Sticky Header and CSV Export */}
        <div className="bg-white rounded-[4px] border border-[#DFE3E8] shadow-[0_1px_2px_rgba(0,0,0,0.03)] overflow-hidden space-y-0">
          <div className="p-4 border-b border-[#DFE3E8] flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-[#F4F6F8]">
            <div>
              <h3 className="text-sm font-bold text-[#1A1A1A] uppercase tracking-wider">
                {t('fieldActionPlan')}
              </h3>
              <p className="text-xs text-[#5B6770] mt-0.5">
                Targeted infrastructure remediation and patrol intervals prioritized by composite severity score.
              </p>
            </div>

            <button
              onClick={exportToCSV}
              className="px-3.5 py-1.5 bg-[#007eb4] hover:bg-[#005a82] text-white text-xs font-semibold rounded-[4px] flex items-center gap-1.5 self-start sm:self-auto transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export CSV</span>
            </button>
          </div>

          <div className="overflow-x-auto max-h-96 overflow-y-auto">
            <table className="w-full text-left text-xs border-collapse">
              {/* Sticky Table Header as required */}
              <thead className="sticky top-0 bg-[#F4F6F8] border-b border-[#DFE3E8] z-20 text-[#5B6770] uppercase font-bold text-[10px] tracking-wider">
                <tr>
                  <th
                    onClick={() => handleSort('rank_by_score')}
                    className="py-3 px-4 cursor-pointer hover:text-[#007eb4]"
                  >
                    <div className="flex items-center gap-1">
                      <span>{t('rank')}</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th className="py-3 px-4">{t('location')}</th>
                  <th
                    onClick={() => handleSort('n_accidents')}
                    className="py-3 px-4 cursor-pointer hover:text-[#007eb4]"
                  >
                    <div className="flex items-center gap-1">
                      <span>{t('accidents')}</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('killed')}
                    className="py-3 px-4 cursor-pointer hover:text-[#007eb4]"
                  >
                    <div className="flex items-center gap-1">
                      <span>{t('killed')}</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th className="py-3 px-4">{t('injured')}</th>
                  <th
                    onClick={() => handleSort('score')}
                    className="py-3 px-4 cursor-pointer hover:text-[#007eb4]"
                  >
                    <div className="flex items-center gap-1">
                      <span>{t('score')}</span>
                      <ArrowUpDown className="w-3 h-3" />
                    </div>
                  </th>
                  <th className="py-3 px-4">{t('peakTime')}</th>
                  <th className="py-3 px-4">{t('primaryVehicle')}</th>
                  <th className="py-3 px-4">{t('recommendedAction')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#DFE3E8] text-[#1A1A1A]">
                {sortedClusters.map((cluster) => {
                  const rank = cluster.rank_by_score || 1;
                  return (
                    <tr
                      key={cluster.cluster_id}
                      className="hover:bg-[#F4F6F8] transition-colors"
                    >
                      <td className="py-3 px-4 font-bold">
                        <span
                          className={`inline-block px-2 py-0.5 rounded-[2px] text-white text-[10px] ${
                            rank <= 3
                              ? 'bg-[#D32F2F]'
                              : rank <= 6
                              ? 'bg-[#F59E0B]'
                              : 'bg-[#007eb4]'
                          }`}
                        >
                          #{rank}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-semibold text-[#1A1A1A] max-w-xs">
                        {cluster.label}
                      </td>
                      <td className="py-3 px-4 font-bold">{cluster.n_accidents}</td>
                      <td className="py-3 px-4 font-bold text-[#D32F2F]">{cluster.killed}</td>
                      <td className="py-3 px-4 text-[#F59E0B] font-semibold">{cluster.injured}</td>
                      <td className="py-3 px-4 font-extrabold text-[#007eb4]">
                        {cluster.score.toFixed(1)}
                      </td>
                      <td className="py-3 px-4 capitalize font-medium">{cluster.peak_time_bucket}</td>
                      <td className="py-3 px-4 capitalize">{cluster.top_vehicle}</td>
                      <td className="py-3 px-4 text-xs text-[#5B6770] max-w-sm leading-relaxed">
                        {cluster.recommended_action || (rank === 1
                          ? 'Emergency arrester bed, high-friction rumble strips, and mandatory 20 km/h truck brake checkpoint at ghat entrance.'
                          : rank === 2
                          ? 'High-mast LED solar illumination, warning flashing beacons, and speed radar camera.'
                          : 'Bridge approach lane channelizers, chevron retroreflective signage, and regular evening patrolling.')}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Bottom Section 2: Citizen Reports Inbox with Approve/Reject */}
        <div className="bg-white rounded-[4px] border border-[#DFE3E8] shadow-[0_1px_2px_rgba(0,0,0,0.03)] overflow-hidden space-y-0">
          <div className="p-4 border-b border-[#DFE3E8] bg-[#F4F6F8] flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Inbox className="w-4 h-4 text-[#007eb4]" />
              <h3 className="text-sm font-bold text-[#1A1A1A] uppercase tracking-wider">
                {t('citizenInbox')}
              </h3>
            </div>
            <span className="text-xs text-[#5B6770]">
              {reports.filter((r) => r.status === 'pending').length} pending review
            </span>
          </div>

          <div className="p-5">
            {reports.length > 0 ? (
              <div className="divide-y divide-[#DFE3E8]">
                {reports.map((r) => (
                  <div key={r.id} className="py-4 first:pt-0 last:pb-0 flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-xs text-[#1A1A1A]">
                          Report #{r.id}: {r.landmark}
                        </span>
                        <span
                          className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-[2px] ${
                            r.status === 'approved'
                              ? 'bg-emerald-100 text-[#2E7D32]'
                              : r.status === 'rejected'
                              ? 'bg-rose-100 text-[#D32F2F]'
                              : 'bg-amber-100 text-[#F59E0B]'
                          }`}
                        >
                          {r.status}
                        </span>
                      </div>
                      <p className="text-xs text-[#5B6770] leading-relaxed">
                        {r.details || 'No detailed remarks provided.'}
                      </p>
                      <div className="text-[11px] text-[#5B6770]">
                        Submitted on {r.date} • Reporter: {r.citizen_name || 'Anonymous'} • Hazard: {r.hazard_type}
                      </div>
                    </div>

                    {r.status === 'pending' && (
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <button
                          onClick={() => handleReportAction(r.id, 'approved')}
                          className="px-3 py-1.5 bg-[#2E7D32] hover:bg-emerald-800 text-white text-xs font-semibold rounded-[4px] flex items-center gap-1 transition-colors"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>{t('approve')}</span>
                        </button>
                        <button
                          onClick={() => handleReportAction(r.id, 'rejected')}
                          className="px-3 py-1.5 bg-white border border-[#D32F2F] text-[#D32F2F] hover:bg-rose-50 text-xs font-semibold rounded-[4px] flex items-center gap-1 transition-colors"
                        >
                          <XCircle className="w-3.5 h-3.5" />
                          <span>{t('reject')}</span>
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-xs text-[#5B6770] text-center py-6">
                No citizen hazard reports currently in the review queue.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
