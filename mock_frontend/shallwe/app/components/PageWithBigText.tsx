import React from 'react';

const fontSize = '2em';

interface PageWithBigTextProps {
  bgColor: string;
  pageTitle: string;
}

const PageWithBigText: React.FC<PageWithBigTextProps> = ({ bgColor, pageTitle }) => (
  <div className="page" style={{ background: bgColor }}>
    <h1>{pageTitle}</h1>
    <p style={{ fontSize: '2em' }}>MOCK: This page is for testing purposes only!</p>
  </div>
);

export default PageWithBigText;
