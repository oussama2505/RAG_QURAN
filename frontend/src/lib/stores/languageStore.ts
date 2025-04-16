// Language management store
import { writable } from 'svelte/store';

// Define available languages
export type Language = 'en' | 'ar' | 'es';

// Define the translations interface
export interface Translations {
  [key: string]: {
    [lang in Language]: string;
  };
}

// Define all UI text translations
export const translations: Translations = {
  // Header and general UI
  'app_title': {
    en: 'Quran Knowledge Explorer',
    ar: 'مستكشف معرفة القرآن',
    es: 'Explorador de Conocimiento del Corán'
  },
  'app_subtitle': {
    en: 'Explore the wisdom of the Holy Quran through AI-assisted research',
    ar: 'استكشف حكمة القرآن الكريم من خلال البحث بمساعدة الذكاء الاصطناعي',
    es: 'Explore la sabiduría del Sagrado Corán a través de la investigación asistida por IA'
  },
  
  // Input field
  'ask_label': {
    en: 'Ask about the Quran',
    ar: 'اسأل عن القرآن',
    es: 'Pregunte sobre el Corán'
  },
  'ask_placeholder': {
    en: 'Enter your question about the Quran...',
    ar: 'أدخل سؤالك حول القرآن الكريم...',
    es: 'Ingrese su pregunta sobre el Corán...'
  },
  
  // Sidebar
  'api_key_setup': {
    en: 'API Key Setup',
    ar: 'إعداد مفتاح API',
    es: 'Configuración de clave API'
  },
  'api_key_label': {
    en: 'OpenAI API Key',
    ar: 'مفتاح API لـ OpenAI',
    es: 'Clave API de OpenAI'
  },
  'api_key_placeholder': {
    en: 'Enter your API key',
    ar: 'أدخل مفتاح API الخاص بك',
    es: 'Ingrese su clave API'
  },
  'save_for_future': {
    en: 'Save for future sessions',
    ar: 'حفظ للجلسات المستقبلية',
    es: 'Guardar para sesiones futuras'
  },
  'save_api_key': {
    en: 'Save API Key',
    ar: 'حفظ مفتاح API',
    es: 'Guardar clave API'
  },
  'system_status': {
    en: 'System Status',
    ar: 'حالة النظام',
    es: 'Estado del Sistema'
  },
  'system_online': {
    en: 'System Online',
    ar: 'النظام متصل',
    es: 'Sistema en Línea'
  },
  'system_offline': {
    en: 'System Offline',
    ar: 'النظام غير متصل',
    es: 'Sistema Fuera de Línea'
  },
  'sample_questions': {
    en: 'Sample Questions',
    ar: 'أسئلة نموذجية',
    es: 'Preguntas de Ejemplo'
  },
  'about': {
    en: 'About',
    ar: 'حول',
    es: 'Acerca de'
  },
  'about_text': {
    en: 'This application uses advanced AI technology to help you explore and understand the Holy Quran through authentic sources including Quranic verses and trusted tafsir (interpretations).',
    ar: 'يستخدم هذا التطبيق تقنية الذكاء الاصطناعي المتقدمة لمساعدتك على استكشاف وفهم القرآن الكريم من خلال مصادر موثوقة بما في ذلك آيات القرآن والتفاسير الموثوقة.',
    es: 'Esta aplicación utiliza tecnología avanzada de IA para ayudarlo a explorar y comprender el Sagrado Corán a través de fuentes auténticas que incluyen versículos coránicos e interpretaciones confiables (tafsir).'
  },
  
  // Filter
  'surah_filter': {
    en: 'Surah Filter',
    ar: 'تصفية السور',
    es: 'Filtro de Sura'
  },
  'select_surah': {
    en: 'Select a Surah',
    ar: 'اختر سورة',
    es: 'Seleccione una Sura'
  },
  'all_surahs': {
    en: 'All Surahs',
    ar: 'جميع السور',
    es: 'Todas las Suras'
  },
  'show_filters': {
    en: 'Show Filters',
    ar: 'إظهار التصفية',
    es: 'Mostrar Filtros'
  },
  'hide_filters': {
    en: 'Hide Filters',
    ar: 'إخفاء التصفية',
    es: 'Ocultar Filtros'
  },
  
  // Settings
  'settings': {
    en: 'Settings',
    ar: 'الإعدادات',
    es: 'Configuración'
  },
  'language': {
    en: 'Language',
    ar: 'اللغة',
    es: 'Idioma'
  },
  'theme': {
    en: 'Theme',
    ar: 'السمة',
    es: 'Tema'
  },
  'keyboard_shortcuts': {
    en: 'Keyboard Shortcuts',
    ar: 'اختصارات لوحة المفاتيح',
    es: 'Atajos de Teclado'
  },
  
  // Buttons
  'submit': {
    en: 'Submit',
    ar: 'إرسال',
    es: 'Enviar'
  },
  'loading': {
    en: 'Loading...',
    ar: 'جار التحميل...',
    es: 'Cargando...'
  },
  'clear': {
    en: 'Clear',
    ar: 'مسح',
    es: 'Limpiar'
  },
  
  // Status
  'searching': {
    en: 'Searching for relevant Quranic knowledge...',
    ar: 'جار البحث عن المعرفة القرآنية ذات الصلة...',
    es: 'Buscando conocimiento coránico relevante...'
  },
  'answer_generated': {
    en: 'Answer generated successfully',
    ar: 'تم إنشاء الإجابة بنجاح',
    es: 'Respuesta generada con éxito'
  },
  'failed_answer': {
    en: 'Failed to get answer',
    ar: 'فشل في الحصول على إجابة',
    es: 'No se pudo obtener respuesta'
  },
  'api_key_required': {
    en: 'Please set your API key first',
    ar: 'يرجى تعيين مفتاح API الخاص بك أولاً',
    es: 'Por favor, configure su clave API primero'
  }
};

// Initialize language from localStorage or use browser language or default to 'en'
const getBrowserLanguage = (): Language => {
  const browserLang = navigator.language.split('-')[0];
  return (browserLang === 'ar' || browserLang === 'es') ? browserLang as Language : 'en';
};

const getInitialLanguage = (): Language => {
  const storedLang = localStorage.getItem('quran_rag_language');
  if (storedLang === 'en' || storedLang === 'ar' || storedLang === 'es') {
    return storedLang as Language;
  }
  return getBrowserLanguage();
};

// Create the language store
const createLanguageStore = () => {
  const initialLanguage = getInitialLanguage();
  const { subscribe, set } = writable<Language>(initialLanguage);
  
  // Set document language attribute
  if (typeof document !== 'undefined') {
    document.documentElement.lang = initialLanguage;
    document.documentElement.dir = initialLanguage === 'ar' ? 'rtl' : 'ltr';
  }
  
  return {
    subscribe,
    setLanguage: (lang: Language) => {
      localStorage.setItem('quran_rag_language', lang);
      if (typeof document !== 'undefined') {
        document.documentElement.lang = lang;
        document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
      }
      set(lang);
    },
    translate: (key: string, language?: Language) => {
      const currentLang = language || initialLanguage;
      return translations[key]?.[currentLang] || key;
    }
  };
};

export const languageStore = createLanguageStore();

// Helper function to translate text
export function t(key: string): string {
  let currentLang: Language = 'en';
  // Get current language from store subscription (for component use)
  languageStore.subscribe(lang => {
    currentLang = lang;
  })();
  
  return translations[key]?.[currentLang] || key;
}