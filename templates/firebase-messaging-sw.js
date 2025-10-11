importScripts("https://www.gstatic.com/firebasejs/10.7.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.7.0/firebase-messaging-compat.js");

firebase.initializeApp({
  apiKey: "AIzaSyCRCA4oMiVMwrTF8zhyb77WeDobJvjSEY4",
  authDomain: "my-expenses-chat.firebaseapp.com",
  projectId: "my-expenses-chat",
  storageBucket: "my-expenses-chat.appspot.com",
  messagingSenderId: "112441534625",
  appId: "1:112441534625:web:31a0f2bd54389763a73678"
});

const messaging = firebase.messaging();
