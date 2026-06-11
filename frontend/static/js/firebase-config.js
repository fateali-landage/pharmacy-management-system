/**
 * firebase-config.js — Firebase Web SDK client-side configuration.
 *
 * These are PUBLIC web config values from Firebase Console > Project Settings > Web apps.
 * They are intentionally visible in the browser per Firebase's security model.
 * Access control is enforced via Firebase Security Rules, NOT by keeping these secret.
 *
 * To update: copy values from Firebase Console and replace below.
 */

const firebaseConfig = {
  apiKey:            "AIzaSyCFvbQU6h5-18NMKtWjgpCCoPWxpi76pBk",
  authDomain:        "pharmacy-managment-4b55f.firebaseapp.com",
  projectId:         "pharmacy-managment-4b55f",
  storageBucket:     "pharmacy-managment-4b55f.appspot.com",
  messagingSenderId: "473321404811",
  appId:             "1:473321404811:web:4707ce0075e069a80ad78e",
  measurementId:     "G-9EESYMDYQS"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

// Expose globally for use by login.html / signup.html
window.firebaseAuth = auth;
window.firebaseConfig = firebaseConfig;
