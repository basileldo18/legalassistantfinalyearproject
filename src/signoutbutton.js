// src/components/SignOutButton.js
import React from 'react';
import { auth } from '../../firebaseConfig';
import { signOut } from 'firebase/auth';

const SignOutButton = () => {
  const handleSignOut = () => {
    signOut(auth)
      .then(() => {
        console.log('User signed out');
        // Redirect to login page or show confirmation
        window.location.href = '/login'; // Redirect to login
      })
      .catch((error) => {
        console.error('Error signing out:', error.message);
      });
  };

  return (
    <button onClick={handleSignOut}>Sign Out</button>
  );
};

export default SignOutButton;
