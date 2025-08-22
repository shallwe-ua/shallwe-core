'use client';

import React from 'react';
import PageWithBigText from '../components/PageWithBigText';
import LogoutButton from '../components/LogoutButton';
import Cookies from 'js-cookie';
import { env } from "@/config/env";


const baseUrl = env.NEXT_PUBLIC_SHALLWE_API_BASE_URL_CLIENT || '';


const Search = () => {
    const handleTestAuthCall = async () => {
    try {
      const response = await fetch(`${baseUrl}/api/rest/auth/test-api-protected/`, {
        method: 'GET',
        credentials: 'include', // Include credentials
      });
      if (response.ok) {
        const responseData = await response.json();
        console.log('Test Auth API response:', responseData);
      } else {
        console.error('Test Auth API request failed:', response.status);
      }
    } catch (error) {
      console.error('An error occurred during the request:', error);
    }
  };

  const deleteAccountCall = async () => {
    const csrfToken = Cookies.get('csrftoken');
    const headers = new Headers();
    headers.append('X-CSRFToken', csrfToken || ''); // Ensure csrfToken is not undefined
    try {
      const response = await fetch(`${baseUrl}/api/rest/auth/user/`, {
        method: 'DELETE',
        headers: headers,
        credentials: 'include', // Include credentials
      });
      if (response.ok) {
        window.location.reload();
      } else {
        console.error('Delete request failed:', response.status);
      }
    } catch (error) {
      console.error('An error occurred during the request:', error);
    }
  };

  return (
    <div>
      <PageWithBigText bgColor="#F0E68C" pageTitle="Search" />
      <LogoutButton />
      <button onClick={handleTestAuthCall}>Test Token Protected API (see console)</button>
      <button onClick={deleteAccountCall}>Delete account</button>
    </div>
  );
}

export default Search;
