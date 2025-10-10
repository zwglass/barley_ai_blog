'use client'

import { useMemo } from 'react'
import { MDXLayoutRenderer } from 'pliny/mdx-components'
import AuthorLayout from '@/layouts/AuthorLayout'
import { useLanguage } from '@/components/LanguageProvider'
import { DEFAULT_LANGUAGE, type LanguageCode } from '@/lib/language'
import { uiText } from '@/lib/i18n'
import type { CoreContent } from 'pliny/utils/contentlayer'
import type { Authors } from 'contentlayer/generated'

type AuthorTranslation = {
  content: CoreContent<Authors>
  code: string
}

type Props = {
  translations: Partial<Record<LanguageCode, AuthorTranslation>>
}

export default function AboutContent({ translations }: Props) {
  const { language } = useLanguage()

  const active = useMemo(() => {
    return (
      translations[language] ||
      translations[DEFAULT_LANGUAGE] ||
      Object.values(translations).find((entry): entry is AuthorTranslation => Boolean(entry))
    )
  }, [language, translations])

  if (!active) {
    return null
  }

  const heading = uiText.aboutTitle[language] ?? uiText.aboutTitle[DEFAULT_LANGUAGE] ?? 'About'

  return (
    <AuthorLayout content={active.content} title={heading}>
      <MDXLayoutRenderer code={active.code} />
    </AuthorLayout>
  )
}
