import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';

// Define the font size variable
const fontSize = '2em';

const PageWithBigText = ({ bgColor, pageTitle }) => (
  <div className="page" style={{ background: bgColor }}>
    <h1>{pageTitle}</h1>
    <p style={{ fontSize }}>Bunch of different words with big letters</p>
  </div>
);

const Home = () => (
  <div>
    <PageWithBigText bgColor="#FF6347" pageTitle="Home" />
    <a
      href="https://accounts.google.com/o/oauth2/v2/auth?redirect_uri=http://127.0.0.1:8000&prompt=consent&response_type=code&client_id=143026764447-q4v3tsd826qj26jlnrivofl24m1vhpjm.apps.googleusercontent.com&scope=openid&access_type=online"
      rel="noopener noreferrer"
    >
      <button>Google Login</button>
    </a>
  </div>
);
const Setup = () => <PageWithBigText bgColor="#7FFFD4" pageTitle="Setup" />;
const Search = () => <PageWithBigText bgColor="#F0E68C" pageTitle="Search" />;
const Contacts = () => <PageWithBigText bgColor="#87CEEB" pageTitle="Contacts" />;
const Settings = () => <PageWithBigText bgColor="#FFA07A" pageTitle="Settings" />;

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
