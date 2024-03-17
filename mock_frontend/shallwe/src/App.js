import React, { useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Cookies from 'js-cookie';

// Define the font size variable
const fontSize = '2em';

const PageWithBigText = ({ bgColor, pageTitle }) => (
  <div className="page" style={{ background: bgColor }}>
    <h1>{pageTitle}</h1>
    <p style={{ fontSize }}>MOCK: This page is for testing purposes only!</p>
  </div>
);

// Component for the Logout button
const LogoutButton = () => {
  const handleLogout = async () => {
    try {
      // Get CSRF token from cookies using js-cookie
      const csrfToken = Cookies.get('csrftoken');

      const response = await fetch('/api/rest/auth/logout/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json',
        },
        // credentials: 'include', // Include credentials for the logout request
      });
      if (response.ok) {
        // Perform any additional actions upon successful logout
        console.log('Logged out successfully.');
        // Reload the page
        window.location.reload(true); // Force a reload from the server
      } else {
        console.error('Logout failed.');
      }
    } catch (error) {
      console.error('An error occurred during logout:', error);
    }
  }

  return (
    <button onClick={handleLogout}>Logout</button>
  )
};

const Home = () => {
  useEffect(() => {
    // Function to handle the logic when the Home page loads
    const handleHomeLoad = async () => {
      // Check if 'code' exists in the URL parameters
      const urlParams = new URLSearchParams(window.location.search);
      const codeParam = urlParams.get('code');

      if (codeParam) {
        try {
          // Decode the code
          const decodedCode = decodeURIComponent(codeParam);

          // Perform POST request to the login endpoint with the code
          const response = await fetch('/api/rest/auth/login/google/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code: decodedCode }),
          });

          if (response.ok) {
            // Reload the page
            window.location.reload(true); // Force a reload from the server
          } else {
            console.error('POST request failed:', response.status);
          }
        } catch (error) {
          console.error('An error occurred:', error);
        }
      }
    };

    // Call the function when the Home page loads
    handleHomeLoad();
  }, []); // Empty dependency array ensures the effect runs only once on mount

  const handleTestGeneralCall = async () => {
    try {
      const response = await fetch('/api/rest/auth/test-api-unprotected/', {
        method: 'GET',
      });

      if (response.ok) {
        const responseData = await response.json();
        console.log('Test General API response:', responseData);
        // Process the response data as needed
      } else {
        console.error('Test General API request failed:', response.status);
      }
    } catch (error) {
      console.error('An error occurred during the request:', error);
    }
  };

  const redirectURI = process.env.REACT_APP_REDIRECT_URI;
  const googleAuthUri = `https://accounts.google.com/o/oauth2/v2/auth?redirect_uri=${redirectURI}&prompt=consent&response_type=code&client_id=143026764447-q4v3tsd826qj26jlnrivofl24m1vhpjm.apps.googleusercontent.com&scope=openid&access_type=online`
  
  return (
    <div>
      {/* Your existing Home page content */}
      <PageWithBigText bgColor="#FF6347" pageTitle="Home" />
      <a
        href={googleAuthUri}
        rel="noopener noreferrer"
      >
        <button>Google Login</button>
      </a>
      {/* Button to trigger the test-auth API request */}
      <button onClick={handleTestGeneralCall}>Test Unprotected API (see console)</button>
    </div>
  );
};

const Setup = () => {
  // Function to handle the test-auth API request
  const handleTestAuthCall = async () => {
    try {
      const token = localStorage.getItem('shallweuaLoginKey'); // Retrieve token from localStorage
      if (!token) {
        console.error('No token found in localStorage');
        return;
      }

      const response = await fetch('/api/rest/auth/test-api-protected/', {
        method: 'GET',
      });

      if (response.ok) {
        const responseData = await response.json();
        console.log('Test Auth API response:', responseData);
        // Process the response data as needed
      } else {
        console.error('Test Auth API request failed:', response.status);
      }
    } catch (error) {
      console.error('An error occurred during the request:', error);
    }
  };

  return (
    <div>
      <PageWithBigText bgColor="#7FFFD4" pageTitle="Setup" />
      <LogoutButton />
      {/* Button to trigger the test-auth API request */}
      <button onClick={handleTestAuthCall}>Test Token Protected API (see console)</button>
    </div>
  );
};

const Search = () => <PageWithBigText bgColor="#F0E68C" pageTitle="Search" />;

const Contacts = () => <PageWithBigText bgColor="#87CEEB" pageTitle="Contacts" />;

const Settings = () => (
  <div>
    <PageWithBigText bgColor="#FFA07A" pageTitle="Settings" />
    <LogoutButton />
  </div>
);

const App = () => (
  <Router>
    <div className="app">
      <Routes>
        <Route path="/" exact element={<Home/>} />
        <Route path="/setup" element={<Setup/>} />
        <Route path="/search" element={<Search/>} />
        <Route path="/contacts" element={<Contacts/>} />
        <Route path="/settings" element={<Settings/>} />
      </Routes>
    </div>
  </Router>
);

export default App;
