'use client';

import React, { useEffect, useRef } from 'react';
import PageWithBigText from './components/PageWithBigText';
import { env } from "@/config/env";


const baseUrl = env.NEXT_PUBLIC_SHALLWE_API_BASE_URL_EXTERNAL || '';
const redirectURI = env.NEXT_PUBLIC_SHALLWE_OAUTH_REDIRECT_URI;
const googleClientID = env.NEXT_PUBLIC_SHALLWE_OAUTH_CLIENT_ID;


const Home = () => {
  const requestSent = useRef(false); // Track if the request has been sent

  useEffect(() => {
    const handleHomeLoad = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const codeParam = urlParams.get('code');

      if (codeParam && !requestSent.current) {
        const decodedCode = decodeURIComponent(codeParam);

        // Remove all query parameters from URL
        const newUrl = window.location.origin + window.location.pathname;
        window.history.replaceState({}, document.title, newUrl);

        requestSent.current = true; // Prevent subsequent requests

        try {
            const headers = new Headers();
            headers.append('Content-Type', 'application/json');

          const response = await fetch(`${baseUrl}/api/rest/auth/login/google/`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ code: decodedCode }),
            credentials: 'include', // Include credentials
          });

          if (response.ok) {
            console.log()
            const responseBody = await response.json();
            console.log(responseBody);
            window.location.reload(); // Force a reload from the server
          } else {
            console.error('POST request failed:', response.status);
            requestSent.current = false; // Allow retry in case of failure
          }
        } catch (error) {
          console.error('An error occurred:', error);
          requestSent.current = false; // Allow retry in case of error
        }
      }
    };

    handleHomeLoad();
  }, []);

  const handleTestGeneralCall = async () => {
    try {
      const response = await fetch(`${baseUrl}/api/rest/auth/test-api-unprotected/`, {
        method: 'GET',
        credentials: 'include', // Include credentials
      });
      if (response.ok) {
        const responseData = await response.json();
        console.log('Test General API response:', responseData);
      } else {
        console.error('Test General API request failed:', response.status);
      }
    } catch (error) {
      console.error('An error occurred during the request:', error);
    }
  };

  const googleAuthUri = `https://accounts.google.com/o/oauth2/v2/auth?redirect_uri=${redirectURI}&prompt=consent&response_type=code&client_id=${googleClientID}&scope=openid&access_type=offline`;

  return (
    <div>
      <PageWithBigText bgColor="#FF6347" pageTitle="Home" />
      <a href={googleAuthUri} rel="noopener noreferrer">
        <button>Google Login</button>
      </a>
      <button onClick={handleTestGeneralCall}>Test Unprotected API (see console)</button>
    </div>
  );
};

export default Home;
