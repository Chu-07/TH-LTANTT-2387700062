const projectUrl = process.env.CI_PROJECT_URL;
const projectPath = projectUrl ? new URL(projectUrl).pathname.split('/').filter(Boolean).at(-1) : null;
const rootNamespace = process.env.CI_PROJECT_ROOT_NAMESPACE;
const githubRepo = process.env.GITHUB_REPOSITORY?.split('/');
const githubPages = process.env.GITHUB_PAGES === 'true';

module.exports = {
  title: 'Lab 06 – Bảo mật với DevSecOps',
  tagline: 'Lê Thị Hồng Thắm · MSSV 2387700062 · HUTECH',
  favicon: 'img/favicon.svg',
  url: process.env.DOCUSAURUS_URL || (githubPages && githubRepo ? `https://${githubRepo[0]}.github.io` : rootNamespace ? `https://${rootNamespace}.gitlab.io` : 'https://example.gitlab.io'),
  baseUrl: process.env.DOCUSAURUS_BASE_URL || (githubPages && githubRepo ? `/${githubRepo[1]}/` : projectPath ? `/${projectPath}/` : '/'),
  onBrokenLinks: 'throw',
  markdown: {hooks: {onBrokenMarkdownLinks: 'warn'}},
  presets: [
    ['classic', {
      docs: false,
      blog: false,
      theme: { customCss: require.resolve('./src/css/custom.css') },
    }],
  ],
  themeConfig: {
    navbar: {
      title: 'Lab 06',
      items: [{to: '/', label: 'Trang chủ', position: 'left'}],
    },
    footer: {style: 'dark', copyright: `© ${new Date().getFullYear()} Lê Thị Hồng Thắm · HUTECH`},
  },
};
