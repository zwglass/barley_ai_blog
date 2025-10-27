# codex 翻译blog prompt

### 进入codex

```
export  CRS_OAI_KEY=key
codex
```

### 中文翻译为英文, 再从英文翻译为其他文字

```
请把 data/blog/vibecoding-game-pacman/zh.mdx 翻译为英文 data/blog/vibecoding-game-pacman/en.mdx; 再从 en.mdx 翻译为 de.mdx, fr.mdx, ja.mdx, ko.mdx;
请把 data/blog/vibecoding-arena-qlib-finrl/zh.mdx 翻译为英文 data/blog/vibecoding-arena-qlib-finrl/en.mdx; 再从 en.mdx 翻译为 de.mdx, fr.mdx, ja.mdx, ko.mdx;
```

### 翻译完成后测试和上传

```
# 测试
yarn dev

# 打包
yarn build

# 上传
git add .
git commit -m "add blog"
git push
```
