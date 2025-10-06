'use client'

import { createContext, ReactNode, useContext, useMemo, useState } from 'react'
import { DEFAULT_LANGUAGE, LanguageCode } from '@/lib/language'

type LanguageContextValue = {
  language: LanguageCode
  setLanguage: (language: LanguageCode) => void
}

const LanguageContext = createContext<LanguageContextValue | undefined>(undefined)

export const LanguageProvider = ({ children }: { children: ReactNode }) => {
  const [language, setLanguage] = useState<LanguageCode>(DEFAULT_LANGUAGE)

  const value = useMemo(() => ({ language, setLanguage }), [language])

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
}

export const useLanguage = () => {
  const context = useContext(LanguageContext)

  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider')
  }

  return context
}

export const languageOptions: Record<LanguageCode, string> = {
  zh: '中文',
  en: 'English',
  ja: '日本語',
  ko: '한국어',
  fr: 'Français',
  de: 'Deutsch',
}
