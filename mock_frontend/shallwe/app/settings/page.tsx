'use client';

import React from 'react';
import PageWithBigText from '../components/PageWithBigText';
import LogoutButton from '../components/LogoutButton';

const Settings = () => (
  <div>
    <PageWithBigText bgColor="#FFA07A" pageTitle="Settings" />
    <LogoutButton />
  </div>
);

export default Settings;
