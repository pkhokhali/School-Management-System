import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

const resources = {
  en: {
    translation: {
      login: 'Login',
      dashboard: 'Dashboard',
      students: 'Students',
      logout: 'Logout',
    },
  },
  ne: {
    translation: {
      login: 'लगइन',
      dashboard: 'ड्यासबोर्ड',
      students: 'विद्यार्थी',
      logout: 'लगआउट',
    },
  },
}

i18n.use(initReactI18next).init({
  resources,
  lng: 'en',
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
})

export default i18n
