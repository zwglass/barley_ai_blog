# 工具和部署说明

### tools 文件夹

```
tools 文件夹中的脚本功能: 
    修改图片, 生成博客 mdx 文件,
```

### Branch Setup(创建分支, 给GitHub Page 使用)  域名 blog.cchw.net

```
    - Create branch: git checkout -b gh-pages.
    - Build static assets (Next.js): yarn build && npx serve out. This generates out/ for GitHub Pages.
    - Commit + push: git add out && git commit -m "Prepare GitHub Pages" then git subtree push --prefix out origin gh-pages (or copy
    out/ contents to branch and push).

GitHub Pages Config

    - In repo settings → Pages, choose “Deploy from branch”.
    - Select branch gh-pages, folder / (or /out if you keep the build in-branch).
    - Save; wait for GitHub Pages to publish.

Tips

    - Automate with GitHub Action (actions/nextjs) if you prefer CI builds.
    - Remember to rebuild/export whenever you update main content before pushing to gh-pages.
```
