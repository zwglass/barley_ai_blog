import type { LanguageCode } from '@/lib/language'

export type HeaderNavLink = {
  href: string
  titles: Record<LanguageCode, string>
}

const headerNavLinks: HeaderNavLink[] = [
  {
    href: '/',
    titles: {
      zh: '首页',
      en: 'Home',
      ja: 'ホーム',
      ko: '홈',
      fr: 'Accueil',
      de: 'Startseite',
    },
  },
  {
    href: '/blog',
    titles: {
      zh: '博客',
      en: 'Blog',
      ja: 'ブログ',
      ko: '블로그',
      fr: 'Blog',
      de: 'Blog',
    },
  },
  {
    href: '/tags',
    titles: {
      zh: '标签',
      en: 'Tags',
      ja: 'タグ',
      ko: '태그',
      fr: 'Tags',
      de: 'Tags',
    },
  },
  {
    href: '/projects',
    titles: {
      zh: '项目',
      en: 'Projects',
      ja: 'プロジェクト',
      ko: '프로젝트',
      fr: 'Projets',
      de: 'Projekte',
    },
  },
  {
    href: '/about',
    titles: {
      zh: '关于',
      en: 'About',
      ja: '概要',
      ko: '소개',
      fr: 'À propos',
      de: 'Über mich',
    },
  },
]

export default headerNavLinks
