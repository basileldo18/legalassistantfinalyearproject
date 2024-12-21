// src/firebaseConfig.js
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

// Your Firebase configuration (replace with your own Firebase credentials)
const firebaseConfig = {
    apiKey: "AIzaSyCcmVWGbaTeC2y7bRWOpaYywkO4x1YxQW8",
    authDomain: "ailegalassistant-f48f5.firebaseapp.com",
    projectId: "ailegalassistant-f48f5",
    storageBucket: "ailegalassistant-f48f5.firebasestorage.app",
    messagingSenderId: "275330427067",
    appId: "1:275330427067:web:0e4106c186f2d6bb69e19e",
    measurementId: "G-3LXKMYE3T2"
  };
// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication
const auth = getAuth(app);

export default  auth ;
