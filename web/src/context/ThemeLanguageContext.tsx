import React, { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark';
type Language = 'en' | 'hi';

interface ThemeLanguageContextType {
  theme: Theme;
  toggleTheme: () => void;
  lang: Language;
  toggleLanguage: () => void;
  t: (key: string) => string;
}

const translations: Record<Language, Record<string, string>> = {
  en: {
    brandName: 'SURAKSHA',
    brandHindi: 'सुरक्षा',
    tagline: 'Road safety intelligence for Sonbhadra',
    subTagline: 'Data-driven accident blackspot detection, risk modeling, and commuter safety intelligence for Sonbhadra district, UP.',
    home: 'Home',
    adminDashboard: 'Command Center',
    citizenPortal: 'Citizen Advisory',
    login: 'Sign In',
    logout: 'Sign Out',
    totalAccidents: 'Total News Incidents',
    activeBlackspots: 'Ranked Blackspots',
    totalCasualties: 'Reported Casualties',
    criticalWindow: 'High-Risk Shift',
    exploreMap: 'Explore Blackspot Map',
    reportHazard: 'Report a Hazard',
    howItWorks: 'How Suraksha Works',
    howStep1Title: 'News Sourcing & Ingestion',
    howStep1Desc: 'Extracts real accident incidents reported by regional newspapers (Amar Ujala, Dainik Jagran).',
    howStep2Title: 'Geocoding & Deduplication',
    howStep2Desc: 'Resolves exact geographic coordinates with bounding box gates and merges duplicate reports with Union-Find.',
    howStep3Title: 'DBSCAN Spatial Clustering',
    howStep3Desc: 'Groups repeating accident points within 300 meters into ranked blackspots weighted by casualties.',
    howStep4Title: 'Engineering & Patrol Action',
    howStep4Desc: 'Recommends targeted road safety fixes (rumble strips, high-mast lighting) for local traffic police and PWD.',
    dataLimitationsTitle: 'Important Data Limitations & Scope',
    limitation1: 'News Reporting Bias: Only news-reported accidents are analyzed; minor uninjured fender-benders are rarely published while severe and fatal collisions are over-represented.',
    limitation2: 'Descriptive Location Variance: Spatial precision depends on journalists\' landmark descriptions.',
    limitation3: 'Indicative Scope: Identifies recurring high-risk zones from news logs; does not establish mechanical or engineering causality.',
    footerText: 'Suraksha • Sonbhadra District Road Safety & Traffic Police Portal. Developed for empirical traffic hazard reduction.',
    rank: 'Rank',
    location: 'Location',
    accidents: 'Accidents',
    killed: 'Killed',
    injured: 'Injured',
    score: 'Severity Score',
    peakTime: 'Peak Time',
    primaryVehicle: 'Primary Vehicle',
    recommendedAction: 'Recommended Action',
    exportCsv: 'Export Patrol CSV',
    fieldActionPlan: 'Field Patrol Action Plan & Recommended Fixes',
    citizenInbox: 'Citizen Hazard Submissions',
    approve: 'Approve & Add to Analysis',
    reject: 'Dismiss',
    approved: 'Approved',
    pending: 'Pending Review',
    rejected: 'Rejected',
    filterByDate: 'Date Range',
    filterByTime: 'Time of Day',
    filterByVehicle: 'Vehicle Involved',
    minSeverity: 'Min Severity Score',
    welcomeCitizen: 'Commuter Road Hazard & Advisory Portal',
    liveWarning: 'CRITICAL HIGHWAY WARNING',
    liveWarningText: 'NH-39 Markundi Ghat & Hathinala curves: Extreme danger of heavy dumper brake failures between 9 PM and 4 AM.',
    submitReportTitle: 'Submit an Accident or Road Hazard Report',
    submitReportDesc: 'Spotted a dangerous pothole, blind turn, or witnessed a crash? Submit below to alert local traffic safety authorities.',
    nameOptional: 'Your Name (Optional)',
    contactOptional: 'Phone or Email (Optional)',
    landmarkRequired: 'Exact Landmark / Highway Milepost *',
    incidentType: 'Incident / Hazard Type *',
    vehiclesInvolved: 'Vehicles Involved (e.g. Dumper, Bike)',
    riskLevel: 'Perceived Danger Level',
    additionalDetails: 'Additional Description',
    submitButton: 'Submit Hazard Report',
    pickOnMap: 'Click anywhere on map to pin exact location',
    navHome: 'Home',
    navBlackspots: 'Blackspots & Map',
    navData: 'Surveillance Data',
    navReports: 'Publications & Reports',
    navCitizen: 'Citizen Hazard Reporting',
    portalSubheading: 'District Road Safety Authority • Sonbhadra',
    tabOverview: 'Overview',
    tabBlackspots: 'Identified Blackspots',
    tabPatterns: 'Temporal Patterns',
    tabMethodology: 'Surveillance Methodology',
    resourcesHeading: 'Data and Downloads',
    toolsHeading: 'Tools and Services',
    latestUpdatesHeading: 'Latest Surveillance Updates',
    reportsHeading: 'Reports and Publications',
    downloadPdf: 'Download Report',
    readSummary: 'Executive Summary',
    breadcrumbHome: 'Home',
    breadcrumbDashboard: 'Surveillance Dashboard',
    breadcrumbCitizen: 'Citizen Hazard Reporting',
    breadcrumbLogin: 'Authorized Portal Login',
  },
  hi: {
    brandName: 'सुरक्षा',
    brandHindi: 'SURAKSHA',
    tagline: 'सोनभद्र के लिए सड़क सुरक्षा और ब्लैकस्पॉट इंटेलिजेंस',
    subTagline: 'सोनभद्र जिले के लिए डेटा-आधारित दुर्घटना ब्लैकस्पॉट पहचान, जोखिम मॉडलिंग और यात्री सुरक्षा प्रणाली।',
    home: 'होम',
    adminDashboard: 'कमांड सेंटर',
    citizenPortal: 'नागरिक पोर्टल',
    login: 'लॉग इन',
    logout: 'लॉग आउट',
    totalAccidents: 'कुल दर्ज दुर्घटनाएं',
    activeBlackspots: 'चिह्नित ब्लैकस्पॉट',
    totalCasualties: 'हताहत नागरिक',
    criticalWindow: 'अत्यधिक जोखिम समय',
    exploreMap: 'ब्लैकस्पॉट मैप देखें',
    reportHazard: 'खतरे की सूचना दें',
    howItWorks: 'सुरक्षा प्रणाली कैसे कार्य करती है',
    howStep1Title: 'समाचार स्रोतों से डेटा संकलन',
    howStep1Desc: 'अमर उजाला, दैनिक जागरण जैसे स्थानीय समाचार पत्रों से सड़क दुर्घटनाओं का सत्यापित डेटा संकलित किया जाता है।',
    howStep2Title: 'जियोकोडिंग और डुप्लीकेट शुद्धिकरण',
    howStep2Desc: 'बाउंडिंग बॉक्स सत्यापन और यूनियन-फाइंड तकनीक से एक ही घटना के दोहराए गए समाचारों का सटीक मिलान।',
    howStep3Title: 'DBSCAN स्थानिक क्लस्टरिंग',
    howStep3Desc: '300 मीटर के भीतर बार-बार होने वाली दुर्घटनाओं को गंभीरता स्कोर के आधार पर ब्लैकस्पॉट में वर्गीकृत किया जाता है।',
    howStep4Title: 'इंजीनियरिंग और पुलिस पेट्रोलिंग कार्रवाई',
    howStep4Desc: 'यातायात पुलिस और लोक निर्माण विभाग (PWD) के लिए रंबल स्ट्रिप, सोलर ब्लिंकर जैसी लक्षित सिफारिशें।',
    dataLimitationsTitle: 'महत्वपूर्ण डेटा सीमाएं एवं स्पष्टीकरण',
    limitation1: 'समाचार पूर्वाग्रह: केवल समाचार-रिपोर्ट की गई दुर्घटनाओं का विश्लेषण किया गया है। गंभीर और घातक घटनाएं अधिक प्रमुखता से दर्ज हैं।',
    limitation2: 'स्थान विवरण भिन्नता: सटीकता इस बात पर निर्भर करती है कि रिपोर्टर ने स्थान का उल्लेख कैसे किया है।',
    limitation3: 'संकेतक प्रकृति: यह प्रणाली दुर्घटना के हॉटस्पॉट दर्शाती है, किसी दुर्घटना का यांत्रिक या इंजीनियरिंग कारण नहीं बताती।',
    footerText: 'सुरक्षा • सोनभद्र जिला सड़क सुरक्षा एवं यातायात पुलिस पोर्टल। अनुभवजन्य सड़क दुर्घटना निवारण हेतु समर्पित।',
    rank: 'रैंक',
    location: 'ब्लैकस्पॉट स्थान',
    accidents: 'दुर्घटनाएं',
    killed: 'मृत्यु',
    injured: 'घायल',
    score: 'गंभीरता स्कोर',
    peakTime: 'चरम समय',
    primaryVehicle: 'प्रमुख वाहन',
    recommendedAction: 'अनुशंसित इंजीनियरिंग/पुलिस कार्रवाई',
    exportCsv: 'फील्ड पेट्रोल CSV डाउनलोड',
    fieldActionPlan: 'फील्ड पेट्रोलिंग एवं सड़क सुरक्षा सुधार योजना',
    citizenInbox: 'नागरिकों द्वारा दर्ज खतरों की इनबॉक्स',
    approve: 'स्वीकृत करें व डेटासेट में जोड़ें',
    reject: 'अस्वीकृत करें',
    approved: 'स्वीकृत',
    pending: 'सत्यापन लंबित',
    rejected: 'खारिज',
    filterByDate: 'तिथि सीमा',
    filterByTime: 'समय खिड़की',
    filterByVehicle: 'शामिल वाहन',
    minSeverity: 'न्यूनतम गंभीरता स्कोर',
    welcomeCitizen: 'यात्री सड़क सुरक्षा एवं जन-सूचना पोर्टल',
    liveWarning: 'अति-महत्वपूर्ण सड़क चेतावनी',
    liveWarningText: 'NH-39 मारकुंडी घाटी और हाथीनाला मोड़: रात 9 बजे से सुबह 4 बजे के बीच भारी डंपर ब्रेक फेल होने का अत्यधिक खतरा। धीमी गति रखें।',
    submitReportTitle: 'सड़क दुर्घटना या खतरे की सूचना दर्ज करें',
    submitReportDesc: 'क्या आपने कोई खतरनाक गड्ढा, अंधा मोड़ या दुर्घटना देखी है? यातायात पुलिस को सूचित करने हेतु नीचे विवरण भरें।',
    nameOptional: 'आपका नाम (वैकल्पिक)',
    contactOptional: 'फोन या ईमेल (वैकल्पिक)',
    landmarkRequired: 'सटीक स्थान / मील का पत्थर *',
    incidentType: 'खतरे / घटना का प्रकार *',
    vehiclesInvolved: 'शामिल वाहन (उदा. डंपर, बाइक)',
    riskLevel: 'अनुमानित जोखिम स्तर',
    additionalDetails: 'अतिरिक्त विवरण',
    submitButton: 'खतरे की रिपोर्ट सबमिट करें',
    pickOnMap: 'सटीक स्थान चुनने के लिए मैप पर क्लिक करें',
    navHome: 'मुख्य पृष्ठ',
    navBlackspots: 'ब्लैकस्पॉट एवं मानचित्र',
    navData: 'निगरानी डेटा',
    navReports: 'प्रकाशन एवं रिपोर्ट',
    navCitizen: 'नागरिक जोखिम रिपोर्टिंग',
    portalSubheading: 'जिला सड़क सुरक्षा प्राधिकरण • सोनभद्र',
    tabOverview: 'अवलोकन',
    tabBlackspots: 'पहचाने गए ब्लैकस्पॉट',
    tabPatterns: 'सामयिक पैटर्न',
    tabMethodology: 'निगरानी कार्यप्रणाली',
    resourcesHeading: 'डेटा और डाउनलोड',
    toolsHeading: 'उपकरण एवं सेवाएं',
    latestUpdatesHeading: 'नवीनतम निगरानी अपडेट',
    reportsHeading: 'रिपोर्ट एवं प्रकाशन',
    downloadPdf: 'रिपोर्ट डाउनलोड करें',
    readSummary: 'कार्यकारी सारांश',
    breadcrumbHome: 'होम',
    breadcrumbDashboard: 'निगरानी डैशबोर्ड',
    breadcrumbCitizen: 'नागरिक जोखिम रिपोर्टिंग',
    breadcrumbLogin: 'अधिकृत पोर्टल लॉगिन',
  },
};

const ThemeLanguageContext = createContext<ThemeLanguageContextType | undefined>(undefined);

export const ThemeLanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<Theme>(() => (localStorage.getItem('suraksha_theme') as Theme) || 'light');
  const [lang, setLang] = useState<Language>(() => (localStorage.getItem('suraksha_lang') as Language) || 'en');

  useEffect(() => {
    localStorage.setItem('suraksha_theme', theme);
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  useEffect(() => {
    localStorage.setItem('suraksha_lang', lang);
  }, [lang]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  const toggleLanguage = () => {
    setLang((prev) => (prev === 'en' ? 'hi' : 'en'));
  };

  const t = (key: string): string => {
    return translations[lang][key] || translations.en[key] || key;
  };

  return (
    <ThemeLanguageContext.Provider value={{ theme, toggleTheme, lang, toggleLanguage, t }}>
      {children}
    </ThemeLanguageContext.Provider>
  );
};

export const useThemeLanguage = () => {
  const context = useContext(ThemeLanguageContext);
  if (!context) throw new Error('useThemeLanguage must be used within ThemeLanguageProvider');
  return context;
};
