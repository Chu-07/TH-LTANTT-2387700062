import React from 'react';
import Layout from '@theme/Layout';
import styles from './index.module.css';

export default function Home() {
  return (
    <Layout title="Trang chủ" description="Lab 06 – Bảo mật với DevSecOps">
      <main className={styles.main}>
        <section className={styles.hero}>
          <span className={styles.eyebrow}>HUTECH · Lập trình An ninh Thông tin</span>
          <h1>Lab 06: Bảo mật với DevSecOps</h1>
          <p>Xây dựng và kiểm thử CI/CD pipeline bằng GitLab, sau đó build và triển khai website Docusaurus lên GitLab Pages.</p>
          <p><strong>Lê Thị Hồng Thắm</strong> · MSSV 2387700062</p>
        </section>
        <section className={styles.grid}>
          <article><h2>6.2.1 · Pipeline đầu tiên</h2><p>Bốn job qua ba giai đoạn build, test và deploy. Job kiểm thử thứ hai mô phỏng thời gian chạy 20 giây.</p></article>
          <article><h2>6.2.2 · Pipeline Docusaurus</h2><p>Ba bước kiểm thử: job cơ bản, build website có artifacts, rồi triển khai GitLab Pages.</p></article>
          <article><h2>DevSecOps</h2><p>Pipeline an toàn cần quản lý bí mật, kiểm soát quyền truy cập, kiểm thử bảo mật và giám sát runner.</p></article>
        </section>
      </main>
    </Layout>
  );
}
