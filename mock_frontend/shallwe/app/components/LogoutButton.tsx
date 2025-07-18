import React from 'react';
import Cookies from 'js-cookie';
import { env } from "@/config/env";


const apiBaseUrl = env.NEXT_PUBLIC_SHALLWE_API_BASE_URL || '';


const LogoutButton = () => {
  const handleLogout = async () => {
    try {
      const csrfToken = Cookies.get('csrftoken');
      const headers = new Headers();
        headers.append('X-CSRFToken', csrfToken || ''); // Ensure csrfToken is not undefined
        headers.append('Content-Type', 'application/json');

      const response = await fetch(`${apiBaseUrl}/api/rest/auth/logout/`, {
        method: 'POST',
        headers: headers,
        credentials: 'include', // Include credentials
      });
      if (response.ok) {
        console.log('Logged out successfully.');
        window.location.reload();
      } else {
        console.error('Logout failed.');
      }
    } catch (error) {
      console.error('An error occurred during logout:', error);
    }
  };

  return <button onClick={handleLogout}>Logout</button>;
};

export default LogoutButton;
