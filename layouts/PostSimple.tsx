'use client'

import { ReactNode, useMemo } from 'react'
import { formatDate } from '@/lib/formatDate'
import { CoreContent } from 'pliny/utils/contentlayer'
import type { Blog } from 'contentlayer/generated'
import Comments from '@/components/Comments'
import Link from '@/components/Link'
import PageTitle from '@/components/PageTitle'
import SectionContainer from '@/components/SectionContainer'
import siteMetadata from '@/data/siteMetadata'
import ScrollTopAndComment from '@/components/ScrollTopAndComment'
import { useLanguage } from '@/components/LanguageProvider'
import { languageLocales, uiText } from '@/lib/i18n'
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

export default function PostLayout({
  content,
  next,
  prev,
  children,
  translations,
  translationNodes,
}: LayoutProps) {
  const { language } = useLanguage()
  const locale = languageLocales[language]
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
  const { path, slug, date, title } = activeContent

  return (
    <SectionContainer>
      <ScrollTopAndComment />
      <article>
        <div>
          <header>
            <div className="space-y-1 border-b border-gray-200 pb-10 text-center dark:border-gray-700">
              <dl>
                <div>
                  <dt className="sr-only">{uiText.publishedOn[language]}</dt>
                  <dd className="text-base leading-6 font-medium text-gray-500 dark:text-gray-400">
                    <time dateTime={date}>{formatDate(date, locale)}</time>
                  </dd>
                </div>
              </dl>
              <div>
                <PageTitle>{title}</PageTitle>
              </div>
            </div>
          </header>
          <div className="grid-rows-[auto_1fr] divide-y divide-gray-200 pb-8 xl:divide-y-0 dark:divide-gray-700">
            <div className="divide-y divide-gray-200 xl:col-span-3 xl:row-span-2 xl:pb-0 dark:divide-gray-700">
              <div className="prose dark:prose-invert max-w-none pt-10 pb-8">{activeNode}</div>
            </div>
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
        </div>
      </article>
    </SectionContainer>
  )
}
