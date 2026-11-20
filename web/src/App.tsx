import React, { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeLanguageProvider } from './context/ThemeLanguageContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { AdminDashboard } from './pages/AdminDashboard';
import { CitizenPortal } from './pages/CitizenPortal';

type Page = 'home' | 'admin' | 'citizen' | 'login';

const AppContent: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<Page>('home');
  const { isAuthenticated, isAdmin } = useAuth();

  const handleNavigate = (page: Page) => {
    if (page === 'admin' && (!isAuthenticated || !isAdmin)) {
      setCurrentPage('login');
    } else {
      setCurrentPage(page);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleLoginSuccess = (role: 'admin' | 'citizen') => {
    if (role === 'admin') {
      setCurrentPage('admin');
    } else {
      setCurrentPage('citizen');
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen flex flex-col bg-white text-[#1A1A1A]">
      <Navbar currentPage={currentPage} onNavigate={handleNavigate} />

      <main id="main-content" tabIndex={-1} className="flex-1 focus:outline-none">
        <AnimatePresence mode="wait">
          {currentPage === 'home' && (
            <motion.div
              key="home"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.18 }}
            >
              <LandingPage onNavigate={handleNavigate} />
            </motion.div>
          )}

          {currentPage === 'citizen' && (
            <motion.div
              key="citizen"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.18 }}
            >
              <CitizenPortal onNavigateHome={() => handleNavigate('home')} />
            </motion.div>
          )}

          {currentPage === 'admin' && (
            <motion.div
              key="admin"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.18 }}
            >
              <AdminDashboard onNavigateHome={() => handleNavigate('home')} />
            </motion.div>
          )}

          {currentPage === 'login' && (
            <motion.div
              key="login"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.18 }}
            >
              <LoginPage
                onSuccess={handleLoginSuccess}
                onNavigateHome={() => handleNavigate('home')}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <Footer />
    </div>
  );
};

export function App() {
  return (
    <ThemeProviderPlaceholder>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProviderPlaceholder>
  );
}

// Wrapper preserving context
const ThemeProviderPlaceholder: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <ThemeLanguageProvider>{children}</ThemeLanguageProvider>;
};

export default App;
