import React, { useEffect, useState } from 'react';
import { useThemeLanguage } from '../context/ThemeLanguageContext';
import { Breadcrumb } from '../components/Breadcrumb';
import { submitReportApi, getClustersApi } from '../services/api';
import type { Cluster } from '../types';
import { BlackspotMap } from '../components/BlackspotMap';
import {
  AlertTriangle,
  Clock,
  Send,
  MapPin,
  CheckCircle2,
  AlertCircle,
  Shield,
  Sun,
  Sunset,
  Moon,
  Info,
} from 'lucide-react';

interface CitizenPortalProps {
  onNavigateHome?: () => void;
}

export const CitizenPortal: React.FC<CitizenPortalProps> = ({ onNavigateHome }) => {
  const { t } = useThemeLanguage();
  const [clusters, setClusters] = useState<Cluster[]>([]);

  // Form states
  const [name, setName] = useState('');
  const [contact, setContact] = useState('');
  const [landmark, setLandmark] = useState('');
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [time, setTime] = useState('14:00');
  const [hazardType, setHazardType] = useState('Blind Curve');
  const [vehicles, setVehicles] = useState('');
  const [severity, setSeverity] = useState('High');
  const [details, setDetails] = useState('');
  const [selectedLocation, setSelectedLocation] = useState<{ lat: number; lon: number } | null>(null);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Time-of-day safety tip selector
  const [selectedTimeTip, setSelectedTimeTip] = useState<'morning' | 'afternoon' | 'evening' | 'night'>('night');

  useEffect(() => {
    getClustersApi()
      .then(setClusters)
      .catch((err) => console.error('Failed to load clusters', err));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitSuccess(null);
    setSubmitError(null);

    if (!landmark) {
      setSubmitError('Please enter a specific landmark or road stretch.');
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await submitReportApi({
        citizen_name: name || 'Anonymous Commuter',
        contact: contact || undefined,
        landmark,
        date,
        time,
        hazard_type: hazardType,
        vehicles: vehicles || 'unknown',
        severity,
        details: details || undefined,
        lat: selectedLocation?.lat || 24.6052,
        lon: selectedLocation?.lon || 83.0548,
      });

      setSubmitSuccess(
        `Report successfully registered with Reference ID #${res.id}. It has been forwarded to the District Traffic Safety review queue.`
      );
      // Reset form
      setLandmark('');
      setVehicles('');
      setDetails('');
      setSelectedLocation(null);
    } catch (err: any) {
      setSubmitError(err.message || 'Failed to submit report. Please check network connection.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleMapLocationPicked = (lat: number, lon: number) => {
    setSelectedLocation({ lat, lon });
  };

  return (
    <div className="w-full space-y-6 pb-16">
      {/* Breadcrumb under nav on every inner page as required */}
      <Breadcrumb
        items={[
          { label: 'Home', onClick: onNavigateHome },
          { label: 'Road Safety Intelligence', onClick: onNavigateHome },
          { label: 'Citizen Hazard Reporting', active: true },
        ]}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Header */}
        <div className="border-b border-[#DFE3E8] pb-4">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#007eb4]">
            <Shield className="w-4 h-4" />
            <span>Public Commuter Safety & Incident Notification</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#1A1A1A] mt-1">
            Citizen Hazard Reporting & Commuter Safety Portal
          </h1>
          <p className="text-xs text-[#5B6770] mt-0.5">
            Empowering residents and drivers in Sonbhadra District to directly flag road infrastructure hazards to traffic authorities.
          </p>
        </div>

        {/* Critical Highway Warning Banner (No emojis) */}
        <div className="p-4 bg-amber-50 border-l-4 border-[#F59E0B] rounded-[4px] text-[#1A1A1A] flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-[#F59E0B] flex-shrink-0 mt-0.5" />
          <div className="text-xs leading-relaxed">
            <strong className="block font-bold text-[#1A1A1A] mb-0.5">
              High-Risk Corridor Advisory: NH-39 Markundi Ghat & Chopan Sone Bridge
            </strong>
            Over 48% of catastrophic collisions occur between 21:00 and 04:00 hours. Heavy dumpers carrying mining aggregates experience brake fade on steep descent curves. Maintain a minimum 50-meter following distance and observe the 20 km/h ghat speed limit.
          </div>
        </div>

        {/* Time-of-Day Safety Guidelines */}
        <div className="bg-white p-6 rounded-[4px] border border-[#DFE3E8] shadow-[0_1px_2px_rgba(0,0,0,0.03)] space-y-4">
          <div className="flex items-center justify-between border-b border-[#DFE3E8] pb-3">
            <div>
              <h3 className="text-sm font-bold text-[#1A1A1A] uppercase tracking-wider">
                Corridor Safety Guidelines by Travel Time
              </h3>
              <p className="text-xs text-[#5B6770]">
                Select a time window to view historical collision risks and preventive driving measures.
              </p>
            </div>
          </div>

          {/* Time Selector Buttons */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <button
              onClick={() => setSelectedTimeTip('morning')}
              className={`p-3 rounded-[4px] border text-left transition-colors flex items-center gap-2.5 ${
                selectedTimeTip === 'morning'
                  ? 'border-[#007eb4] bg-[#F4F6F8] text-[#007eb4]'
                  : 'border-[#DFE3E8] bg-white text-[#5B6770] hover:border-[#007eb4]'
              }`}
            >
              <Sun className="w-4 h-4 flex-shrink-0" />
              <div>
                <div className="text-xs font-bold text-[#1A1A1A]">Morning</div>
                <div className="text-[10px]">06:00 – 11:59</div>
              </div>
            </button>

            <button
              onClick={() => setSelectedTimeTip('afternoon')}
              className={`p-3 rounded-[4px] border text-left transition-colors flex items-center gap-2.5 ${
                selectedTimeTip === 'afternoon'
                  ? 'border-[#007eb4] bg-[#F4F6F8] text-[#007eb4]'
                  : 'border-[#DFE3E8] bg-white text-[#5B6770] hover:border-[#007eb4]'
              }`}
            >
              <Clock className="w-4 h-4 flex-shrink-0" />
              <div>
                <div className="text-xs font-bold text-[#1A1A1A]">Afternoon</div>
                <div className="text-[10px]">12:00 – 16:59</div>
              </div>
            </button>

            <button
              onClick={() => setSelectedTimeTip('evening')}
              className={`p-3 rounded-[4px] border text-left transition-colors flex items-center gap-2.5 ${
                selectedTimeTip === 'evening'
                  ? 'border-[#007eb4] bg-[#F4F6F8] text-[#007eb4]'
                  : 'border-[#DFE3E8] bg-white text-[#5B6770] hover:border-[#007eb4]'
              }`}
            >
              <Sunset className="w-4 h-4 flex-shrink-0" />
              <div>
                <div className="text-xs font-bold text-[#1A1A1A]">Evening</div>
                <div className="text-[10px]">17:00 – 20:59</div>
              </div>
            </button>

            <button
              onClick={() => setSelectedTimeTip('night')}
              className={`p-3 rounded-[4px] border text-left transition-colors flex items-center gap-2.5 ${
                selectedTimeTip === 'night'
                  ? 'border-[#D32F2F] bg-rose-50 text-[#D32F2F]'
                  : 'border-[#DFE3E8] bg-white text-[#5B6770] hover:border-[#D32F2F]'
              }`}
            >
              <Moon className="w-4 h-4 flex-shrink-0 text-[#D32F2F]" />
              <div>
                <div className="text-xs font-bold text-[#D32F2F]">Night (High Risk)</div>
                <div className="text-[10px]">21:00 – 05:59</div>
              </div>
            </button>
          </div>

          {/* Active Tip Card */}
          <div className="p-4 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[4px] text-xs text-[#1A1A1A] leading-relaxed">
            {selectedTimeTip === 'morning' && (
              <div>
                <strong>Morning Hazard: High Pedestrian & Two-Wheeler Density around Schools/Towns.</strong>
                <p className="mt-1 text-[#5B6770]">
                  Peak agricultural tractors and school buses enter NH-39 near Robertsganj and Churk. Dense seasonal winter fog reduces sight distance to under 30 meters on the Son River approaches.
                </p>
              </div>
            )}
            {selectedTimeTip === 'afternoon' && (
              <div>
                <strong>Afternoon Hazard: Excessive Speed on Straight Rural Highway Stretches.</strong>
                <p className="mt-1 text-[#5B6770]">
                  Lighter mid-day traffic induces speeding between Hathinala and Duddhi. Watch for sudden cattle crossings and unmarked farm tractor egress points along SH-5A.
                </p>
              </div>
            )}
            {selectedTimeTip === 'evening' && (
              <div>
                <strong>Evening Hazard: Twilight Visibility Gap & Unlit Commercial Parked Vehicles.</strong>
                <p className="mt-1 text-[#5B6770]">
                  Commuters returning from industrial plants encounter disabled aggregate dumpers parked on highway shoulders without rear reflector tape or hazard flares.
                </p>
              </div>
            )}
            {selectedTimeTip === 'night' && (
              <div>
                <strong className="text-[#D32F2F]">Night Hazard (Critical): Intensive Mining Convoys & Driver Fatigue.</strong>
                <p className="mt-1 text-[#5B6770]">
                  Overloaded multi-axle tippers operate in dense convoys between Chopan stone quarries and Varanasi border. Heavy glare from unaligned high-beam lights causes temporary driver blindness on the Markundi Ghat hairpin turns.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Main Grid: Hazard Report Form (Left) & Map Location Picker (Right) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column (6 cols): Submission Form */}
          <div className="lg:col-span-6 bg-white p-6 rounded-[4px] border border-[#DFE3E8] shadow-[0_1px_2px_rgba(0,0,0,0.03)] space-y-5">
            <div>
              <h3 className="text-base font-bold text-[#1A1A1A] uppercase tracking-wider">
                {t('submitReportTitle')}
              </h3>
              <p className="text-xs text-[#5B6770] mt-0.5">
                {t('submitReportDesc')}
              </p>
            </div>

            {submitSuccess && (
              <div className="p-3.5 bg-emerald-50 border border-[#2E7D32] text-xs text-[#2E7D32] rounded-[4px] flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <span>{submitSuccess}</span>
              </div>
            )}

            {submitError && (
              <div className="p-3.5 bg-rose-50 border border-[#D32F2F] text-xs text-[#D32F2F] rounded-[4px] flex items-start gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <span>{submitError}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-[#1A1A1A] mb-1">
                    {t('nameOptional')}
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Ramesh Kumar"
                    className="w-full p-2 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[4px] focus:outline-none focus:border-[#007eb4]"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-[#1A1A1A] mb-1">
                    {t('contactOptional')}
                  </label>
                  <input
                    type="text"
                    value={contact}
                    onChange={(e) => setContact(e.target.value)}
                    placeholder="Phone or email"
                    className="w-full p-2 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[4px] focus:outline-none focus:border-[#007eb4]"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-[#1A1A1A] mb-1">
                  {t('landmarkRequired')}
                </label>
                <input
                  type="text"
                  required
                  value={landmark}
                  onChange={(e) => setLandmark(e.target.value)}
                  placeholder="e.g. NH-39 Markundi 3rd curve, near milepost 42"
                  className="w-full p-2 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[4px] focus:outline-none focus:border-[#007eb4]"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-[#1A1A1A] mb-1">
                    Date of Occurrence
                  </label>
                  <input
                    type="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    className="w-full p-2 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[4px] focus:outline-none focus:border-[#007eb4]"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-[#1A1A1A] mb-1">
                    Approximate Time
                  </label>
                  <input
                    type="time"
                    value={time}
                    onChange={(e) => setTime(e.target.value)}
                    className="w-full p-2 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[4px] focus:outline-none focus:border-[#007eb4]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-[#1A1A1A] mb-1">
                    {t('incidentType')}
                  </label>
                  <select
                    value={hazardType}
                    onChange={(e) => setHazardType(e.target.value)}
                    className="w-full p-2 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[4px] focus:outline-none focus:border-[#007eb4]"
                  >
                    <option value="Blind Curve">Blind Curve / Visibility Obstruction</option>
                    <option value="Pothole / Road Damage">Pothole / Road Surface Damage</option>
                    <option value="Vehicle Collision">Active Vehicle Collision</option>
                    <option value="Missing Signage / Light">Missing Lighting or Warning Signage</option>
                    <option value="Overloaded Truck Hazard">Overloaded / Broken Down Truck</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-[#1A1A1A] mb-1">
                    {t('riskLevel')}
                  </label>
                  <select
                    value={severity}
                    onChange={(e) => setSeverity(e.target.value)}
                    className="w-full p-2 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[4px] focus:outline-none focus:border-[#007eb4]"
                  >
                    <option value="High">High (Immediate Danger to Life)</option>
                    <option value="Medium">Medium (Potential Hazard)</option>
                    <option value="Low">Low (Maintenance Required)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-semibold text-[#1A1A1A] mb-1">
                  {t('vehiclesInvolved')}
                </label>
                <input
                  type="text"
                  value={vehicles}
                  onChange={(e) => setVehicles(e.target.value)}
                  placeholder="e.g. Dumper truck, motorcycle"
                  className="w-full p-2 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[4px] focus:outline-none focus:border-[#007eb4]"
                />
              </div>

              <div>
                <label className="block font-semibold text-[#1A1A1A] mb-1">
                  {t('additionalDetails')}
                </label>
                <textarea
                  rows={3}
                  value={details}
                  onChange={(e) => setDetails(e.target.value)}
                  placeholder="Provide any additional context, road conditions, or details..."
                  className="w-full p-2 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[4px] focus:outline-none focus:border-[#007eb4]"
                />
              </div>

              {selectedLocation && (
                <div className="p-2.5 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[4px] flex items-center justify-between text-[11px]">
                  <span>
                    Pinned Coordinates: <strong>{selectedLocation.lat.toFixed(5)}, {selectedLocation.lon.toFixed(5)}</strong>
                  </span>
                  <button
                    type="button"
                    onClick={() => setSelectedLocation(null)}
                    className="text-[#D32F2F] hover:underline"
                  >
                    Clear Pin
                  </button>
                </div>
              )}

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full py-2.5 bg-[#007eb4] hover:bg-[#005a82] text-white font-semibold rounded-[4px] flex items-center justify-center gap-2 transition-colors cursor-pointer disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{isSubmitting ? 'Registering Report...' : t('submitButton')}</span>
              </button>
            </form>
          </div>

          {/* Right Column (6 cols): Map Location Picker */}
          <div className="lg:col-span-6 bg-white p-6 rounded-[4px] border border-[#DFE3E8] shadow-[0_1px_2px_rgba(0,0,0,0.03)] space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-[#007eb4]" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-[#1A1A1A]">
                  Pin Hazard on Map
                </h3>
              </div>
              <span className="text-[11px] text-[#5B6770]">
                {t('pickOnMap')}
              </span>
            </div>

            <div className="p-2 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[4px] text-[11px] text-[#5B6770] flex items-center gap-2">
              <Info className="w-3.5 h-3.5 text-[#007eb4] flex-shrink-0" />
              <span>
                Click anywhere on the Sonbhadra map to capture precise GPS coordinates for the patrol dispatch team.
              </span>
            </div>

            <BlackspotMap
              clusters={clusters}
              interactivePick={true}
              onLocationPicked={handleMapLocationPicked}
              pickedLocation={selectedLocation}
              height="480px"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
