import { allAuthors } from 'contentlayer/generated'
import { coreContent } from 'pliny/utils/contentlayer'
import { genPageMetadata } from 'app/seo'
import AboutContent from './AboutContent'
import type { LanguageCode } from '@/lib/language'
import type { CoreContent } from 'pliny/utils/contentlayer'
import type { Authors } from 'contentlayer/generated'

export const metadata = genPageMetadata({ title: 'About' })

export default function Page() {
  const entries = allAuthors.filter((author) => author.translationKey === 'default')
  const translations: Partial<
    Record<LanguageCode, { content: CoreContent<Authors>; code: string }>
  > = {}

  entries.forEach((author) => {
    const language = author.language as LanguageCode
    translations[language] = {
      content: coreContent(author),
      code: author.body.code,
    }
  })

  return <AboutContent translations={translations} />
}
