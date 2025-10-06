'use client'

import Link from 'next/link'
import { useLanguage } from './LanguageProvider'
import { tagSlug, tagTranslations } from '@/lib/i18n'

interface Props {
  text: string
}

const Tag = ({ text }: Props) => {
  const { language } = useLanguage()
  const label = tagTranslations[text]?.[language] || text

  return (
    <Link
      href={`/tags/${tagSlug(text)}`}
      className="text-primary-500 hover:text-primary-600 dark:hover:text-primary-400 mr-3 text-sm font-medium uppercase"
      aria-label={`Tag: ${label}`}
    >
      {label}
    </Link>
  )
}

export default Tag
