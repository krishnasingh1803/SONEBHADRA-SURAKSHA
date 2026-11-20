import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Breadcrumb } from '../components/Breadcrumb';
import { Lock, Mail, AlertCircle, ArrowRight, ShieldCheck, UserCheck, Shield } from 'lucide-react';

interface LoginPageProps {
  onSuccess: (role: 'admin' | 'citizen') => void;
  onNavigateHome: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onSuccess, onNavigateHome }) => {
  const { login, isLoading } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email || !password) {
      setError('Please provide both official email address and password.');
      return;
    }

    try {
      const user = await login(email, password);
      onSuccess(user.role);
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    }
  };

  return (
    <div className="w-full">
      {/* Breadcrumb under nav on every inner page as required */}
      <Breadcrumb
        items={[
          { label: 'Home', onClick: onNavigateHome },
          { label: 'Authorized Portal Login', active: true },
        ]}
      />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-12">
        <div className="bg-white rounded-[4px] border border-[#DFE3E8] shadow-[0_1px_3px_rgba(0,0,0,0.05)] overflow-hidden grid grid-cols-1 md:grid-cols-12">
          {/* Left Column: Institutional Credentials & Authority */}
          <div className="md:col-span-5 bg-[#003B5C] text-white p-8 flex flex-col justify-between space-y-6">
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sky-300 text-xs font-bold uppercase tracking-wider">
                <Shield className="w-4 h-4" />
                <span>Authorized Agency Access</span>
              </div>

              <h2 className="text-xl font-bold text-white tracking-tight leading-snug">
                District Road Safety Surveillance System
              </h2>

              <p className="text-xs text-[#DFE3E8] leading-relaxed">
                Authorized entry for district traffic police officers, NHAI road safety inspectors, PWD engineers, and accredited citizen reporters in Sonbhadra District.
              </p>

              <div className="pt-2 space-y-2.5 text-xs text-[#DFE3E8]">
                <div className="flex items-start gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <span>Bcrypt encrypted credentials & JWT tokens</span>
                </div>
                <div className="flex items-start gap-2">
                  <UserCheck className="w-4 h-4 text-sky-300 flex-shrink-0 mt-0.5" />
                  <span>Role-based access controls (Police & Citizen)</span>
                </div>
                <div className="flex items-start gap-2">
                  <Lock className="w-4 h-4 text-amber-300 flex-shrink-0 mt-0.5" />
                  <span>Sliding-window authentication rate limiting</span>
                </div>
              </div>
            </div>

            <div className="pt-6 border-t border-white/20 text-[11px] text-[#DFE3E8]/80">
              Government of Uttar Pradesh • Sonbhadra District
            </div>
          </div>

          {/* Right Column: Sign In Form */}
          <div className="md:col-span-7 p-8 flex flex-col justify-center">
            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-bold text-[#1A1A1A]">
                  Sign In to Suraksha
                </h3>
                <p className="text-xs text-[#5B6770] mt-1">
                  Enter your authorized account credentials below.
                </p>
              </div>

              {/* Error Banner */}
              {error && (
                <div className="p-3 rounded-[4px] bg-rose-50 border border-[#D32F2F] text-xs text-[#D32F2F] flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-[#1A1A1A] uppercase tracking-wider mb-1.5">
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail className="w-4 h-4 text-[#5B6770] absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="officer@suraksha.gov.in"
                      className="w-full pl-9 pr-3 py-2 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[4px] text-xs text-[#1A1A1A] placeholder:text-[#5B6770] focus:outline-none focus:border-[#007eb4] focus:bg-white transition-colors"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#1A1A1A] uppercase tracking-wider mb-1.5">
                    Password
                  </label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-[#5B6770] absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••••••"
                      className="w-full pl-9 pr-3 py-2 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[4px] text-xs text-[#1A1A1A] placeholder:text-[#5B6770] focus:outline-none focus:border-[#007eb4] focus:bg-white transition-colors"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full py-2.5 bg-[#007eb4] hover:bg-[#005a82] text-white font-semibold text-xs rounded-[4px] transition-colors flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                >
                  <span>{isLoading ? 'Verifying Credentials...' : 'Sign In'}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </form>

            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
