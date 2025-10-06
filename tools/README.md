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

### GitHub Pages 设置步骤

```
  - DNS 记录: 在 cchw.net 的 DNS 服务商后台添加 CNAME 记录，主机名 blog 指向 用户名.github.io（组织帐户则用 组织名.github.io）；等待
  生效。
  - Pages 配置: 进入仓库 Settings → Pages，在 Custom domain 填入 blog.cchw.net，保存；GitHub 会自动生成 CNAME 文件并启用 HTTPS。
  - 静态站点: 若你更喜欢随代码一起管理域名，可在 public/CNAME 写入 blog.cchw.net 并提交；Actions 构建时会把它带入 out/，Pages 会以该
  域名部署。这样 Pages 设置页会显示相同的域名（保存时别覆盖）。
  - 验证部署: 初次设置需几分钟，刷新 Pages 页面确保没有 DNS 错误提示，再访问 https://blog.cchw.net 验证是否指向新站点。
```
