'use client'

import { ReactNode, useMemo } from 'react'
import Image from '@/components/Image'
import Bleed from 'pliny/ui/Bleed'
import { CoreContent } from 'pliny/utils/contentlayer'
import type { Blog } from 'contentlayer/generated'
import Comments from '@/components/Comments'
import Link from '@/components/Link'
import PageTitle from '@/components/PageTitle'
import SectionContainer from '@/components/SectionContainer'
import siteMetadata from '@/data/siteMetadata'
import ScrollTopAndComment from '@/components/ScrollTopAndComment'
import { useLanguage } from '@/components/LanguageProvider'
import { uiText } from '@/lib/i18n'
import type { LanguageCode } from '@/lib/language'
import { DEFAULT_LANGUAGE } from '@/lib/language'
import type { TranslationSummaries } from '@/lib/posts'

interface LayoutProps {
  content: CoreContent<Blog>
  children?: ReactNode
  next?: { path: string; title: string }
  prev?: { path: string; title: string }
  translations?: TranslationSummaries
  translationNodes?: Partial<Record<LanguageCode, ReactNode>>
}

export default function PostMinimal({
  content,
  next,
  prev,
  children,
  translations,
  translationNodes,
}: LayoutProps) {
  const { language } = useLanguage()
  const activeContent = useMemo(() => {
    if (!translations) {
      return content
    }
    return (
      translations[language] ||
      translations[DEFAULT_LANGUAGE] ||
      Object.values(translations).find(Boolean) ||
      content
    )
  }, [translations, language, content])
  const activeNode = useMemo(() => {
    if (!translationNodes) {
      return children
    }
    return (
      translationNodes[language] ||
      translationNodes[DEFAULT_LANGUAGE] ||
      Object.values(translationNodes).find(Boolean) ||
      children
    )
  }, [translationNodes, language, children])
  const { slug, title, images } = activeContent
  const displayImage =
    images && images.length > 0 ? images[0] : 'https://picsum.photos/seed/picsum/800/400'

  return (
    <SectionContainer>
      <ScrollTopAndComment />
      <article>
        <div>
          <div className="space-y-1 pb-10 text-center dark:border-gray-700">
            <div className="w-full">
              <Bleed>
                <div className="relative aspect-2/1 w-full">
                  <Image src={displayImage} alt={title} fill className="object-cover" />
                </div>
              </Bleed>
            </div>
            <div className="relative pt-10">
              <PageTitle>{title}</PageTitle>
            </div>
          </div>
          <div className="prose dark:prose-invert max-w-none py-4">{activeNode}</div>
          {siteMetadata.comments && (
            <div className="pt-6 pb-6 text-center text-gray-700 dark:text-gray-300" id="comment">
              <Comments slug={slug} />
            </div>
          )}
          <footer>
            <div className="flex flex-col text-sm font-medium sm:flex-row sm:justify-between sm:text-base">
              {prev && prev.path && (
                <div className="pt-4 xl:pt-8">
                  <Link
                    href={`/${prev.path}`}
                    className="text-primary-500 hover:text-primary-600 dark:hover:text-primary-400"
                    aria-label={`${uiText.previousArticle[language]}: ${prev.title}`}
                  >
                    &larr; {prev.title}
                  </Link>
                </div>
              )}
              {next && next.path && (
                <div className="pt-4 xl:pt-8">
                  <Link
                    href={`/${next.path}`}
                    className="text-primary-500 hover:text-primary-600 dark:hover:text-primary-400"
                    aria-label={`${uiText.nextArticle[language]}: ${next.title}`}
                  >
                    {next.title} &rarr;
                  </Link>
                </div>
              )}
            </div>
          </footer>
        </div>
      </article>
    </SectionContainer>
  )
}
