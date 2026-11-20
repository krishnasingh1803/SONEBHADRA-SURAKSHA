import React, { useState } from 'react';
import { Logo } from './Logo';
import { useAuth } from '../context/AuthContext';
import { useThemeLanguage } from '../context/ThemeLanguageContext';
import {
  Globe,
  LogIn,
  LogOut,
  ShieldAlert,
  UserCheck,
  Menu,
  X,
  AlertTriangle,
} from 'lucide-react';

interface NavbarProps {
  currentPage: 'home' | 'admin' | 'citizen' | 'login';
  onNavigate: (page: 'home' | 'admin' | 'citizen' | 'login') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentPage, onNavigate }) => {
  const { user, isAuthenticated, logout } = useAuth();
  const { lang, toggleLanguage, t } = useThemeLanguage();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <>
      {/* Skip to Content Accessible Link */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      {/* 1. Top Utility Bar */}
      <div className="w-full bg-[#F4F6F8] border-b border-[#DFE3E8] text-[#5B6770] text-xs py-1.5 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="font-medium text-[#1A1A1A]">
              Government of Uttar Pradesh
            </span>
            <span className="text-[#DFE3E8]" aria-hidden="true">•</span>
            <span className="hidden sm:inline">
              Sonbhadra District Road Safety & Traffic Management Cell
            </span>
          </div>

          <div className="flex items-center gap-4">
            {/* Language Toggle */}
            <button
              onClick={toggleLanguage}
              className="inline-flex items-center gap-1.5 py-0.5 px-2 rounded-[4px] border border-[#DFE3E8] bg-white hover:border-[#007eb4] hover:text-[#007eb4] focus-visible:outline-2 focus-visible:outline-[#007eb4] transition-colors"
              aria-label={`Switch language to ${lang === 'en' ? 'Hindi' : 'English'}`}
            >
              <Globe className="w-3.5 h-3.5 text-[#007eb4]" />
              <span className="font-semibold">{lang === 'en' ? 'हिन्दी' : 'English'}</span>
            </button>

            {/* Auth Link in Utility Bar */}
            {isAuthenticated ? (
              <div className="flex items-center gap-2 text-xs">
                <span className="hidden sm:inline text-[#5B6770]">
                  Signed in as <strong className="text-[#1A1A1A]">{user?.email}</strong>
                </span>
                <button
                  onClick={logout}
                  className="inline-flex items-center gap-1 text-[#D32F2F] hover:underline"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  <span>{t('logout')}</span>
                </button>
              </div>
            ) : (
              <button
                onClick={() => onNavigate('login')}
                className="inline-flex items-center gap-1 text-[#007eb4] hover:underline font-medium"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span>{t('login')}</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 2. Sticky Main Navigation */}
      <header className="sticky top-0 z-40 w-full bg-white border-b border-[#DFE3E8] shadow-[0_1px_3px_rgba(0,0,0,0.05)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-18">
            {/* Logo */}
            <button
              onClick={() => onNavigate('home')}
              className="focus-visible:outline-2 focus-visible:outline-[#007eb4] p-1 rounded-[4px] text-left"
              aria-label="Suraksha Home"
            >
              <Logo size={40} />
            </button>

            {/* Desktop Navigation Links */}
            <nav className="hidden md:flex items-center space-x-1 lg:space-x-2 text-sm font-medium text-[#1A1A1A]">
              <button
                onClick={() => onNavigate('home')}
                className={`px-3 py-2 rounded-[4px] border-b-2 transition-colors ${
                  currentPage === 'home'
                    ? 'border-[#007eb4] text-[#007eb4] font-semibold bg-[#F4F6F8]'
                    : 'border-transparent hover:text-[#007eb4] hover:bg-[#F4F6F8]'
                }`}
              >
                {t('navHome')}
              </button>

              <button
                onClick={() => onNavigate('citizen')}
                className={`px-3 py-2 rounded-[4px] border-b-2 transition-colors flex items-center gap-1.5 ${
                  currentPage === 'citizen'
                    ? 'border-[#007eb4] text-[#007eb4] font-semibold bg-[#F4F6F8]'
                    : 'border-transparent hover:text-[#007eb4] hover:bg-[#F4F6F8]'
                }`}
              >
                <AlertTriangle className="w-4 h-4 text-[#F59E0B]" />
                <span>{t('navCitizen')}</span>
              </button>

              <button
                onClick={() => onNavigate('admin')}
                className={`px-3 py-2 rounded-[4px] border-b-2 transition-colors flex items-center gap-1.5 ${
                  currentPage === 'admin'
                    ? 'border-[#007eb4] text-[#007eb4] font-semibold bg-[#F4F6F8]'
                    : 'border-transparent hover:text-[#007eb4] hover:bg-[#F4F6F8]'
                }`}
              >
                <ShieldAlert className="w-4 h-4 text-[#007eb4]" />
                <span>{t('adminDashboard')}</span>
              </button>
            </nav>

            {/* Desktop Right CTA / Login */}
            <div className="hidden md:flex items-center gap-3">
              {isAuthenticated ? (
                <div className="flex items-center gap-2">
                  <span className="text-xs px-2.5 py-1 bg-[#F4F6F8] border border-[#DFE3E8] rounded-[4px] text-[#5B6770] font-medium flex items-center gap-1.5">
                    <UserCheck className="w-3.5 h-3.5 text-[#2E7D32]" />
                    <span className="capitalize font-semibold text-[#1A1A1A]">{user?.role}</span>
                  </span>
                  <button
                    onClick={() => onNavigate(user?.role === 'admin' ? 'admin' : 'citizen')}
                    className="px-4 py-2 bg-[#007eb4] hover:bg-[#005a82] text-white text-xs font-semibold rounded-[4px] transition-colors"
                  >
                    Go to Dashboard
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => onNavigate('login')}
                  className="px-4 py-2 bg-[#007eb4] hover:bg-[#005a82] text-white text-xs font-semibold rounded-[4px] transition-colors flex items-center gap-1.5"
                >
                  <LogIn className="w-4 h-4" />
                  <span>{t('login')}</span>
                </button>
              )}
            </div>

            {/* Mobile Hamburger Button */}
            <div className="md:hidden flex items-center gap-2">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-2 border border-[#DFE3E8] rounded-[4px] text-[#1A1A1A] hover:bg-[#F4F6F8] focus-visible:outline-2 focus-visible:outline-[#007eb4]"
                aria-label="Toggle navigation menu"
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Dropdown Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-[#DFE3E8] bg-white px-4 pt-3 pb-5 space-y-2">
            <button
              onClick={() => {
                onNavigate('home');
                setMobileMenuOpen(false);
              }}
              className="w-full text-left px-3 py-2.5 rounded-[4px] text-sm font-medium text-[#1A1A1A] hover:bg-[#F4F6F8]"
            >
              {t('navHome')}
            </button>
            <button
              onClick={() => {
                onNavigate('citizen');
                setMobileMenuOpen(false);
              }}
              className="w-full text-left px-3 py-2.5 rounded-[4px] text-sm font-medium text-[#1A1A1A] hover:bg-[#F4F6F8] flex items-center gap-2"
            >
              <AlertTriangle className="w-4 h-4 text-[#F59E0B]" />
              <span>{t('navCitizen')}</span>
            </button>
            <button
              onClick={() => {
                onNavigate('admin');
                setMobileMenuOpen(false);
              }}
              className="w-full text-left px-3 py-2.5 rounded-[4px] text-sm font-medium text-[#1A1A1A] hover:bg-[#F4F6F8] flex items-center gap-2"
            >
              <ShieldAlert className="w-4 h-4 text-[#007eb4]" />
              <span>{t('adminDashboard')}</span>
            </button>

            <div className="pt-3 border-t border-[#DFE3E8]">
              {isAuthenticated ? (
                <div className="space-y-2">
                  <div className="text-xs text-[#5B6770]">
                    Signed in as <strong className="text-[#1A1A1A]">{user?.email}</strong> ({user?.role})
                  </div>
                  <button
                    onClick={() => {
                      logout();
                      setMobileMenuOpen(false);
                    }}
                    className="w-full py-2 text-center text-xs text-[#D32F2F] border border-[#DFE3E8] rounded-[4px] hover:bg-[#F4F6F8]"
                  >
                    {t('logout')}
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => {
                    onNavigate('login');
                    setMobileMenuOpen(false);
                  }}
                  className="w-full py-2.5 bg-[#007eb4] text-white text-xs font-semibold rounded-[4px] text-center"
                >
                  {t('login')}
                </button>
              )}
            </div>
          </div>
        )}
      </header>
    </>
  );
};
