// firebase-messaging-sw.js

// Import required Firebase scripts
importScripts("https://www.gstatic.com/firebasejs/10.7.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.7.0/firebase-messaging-compat.js");

//  Initialize Firebase
firebase.initializeApp({
  apiKey: "AIzaSyCRCA4oMiVMwrTF8zhyb77WeDobJvjSEY4",
  authDomain: "my-expenses-chat.firebaseapp.com",
  projectId: "my-expenses-chat",
  storageBucket: "my-expenses-chat.appspot.com",
  messagingSenderId: "112441534625",
  appId: "1:112441534625:web:31a0f2bd54389763a73678"
});

//  Get Messaging instance
const messaging = firebase.messaging();

//  Background notifications
messaging.onBackgroundMessage(function(payload) {
  console.log(" Background message received:", payload);

  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: "/static/icons/icon-192x192.png", // Make sure this file exists
    badge: "/static/icons/badge-72x72.png", // Optional: for small system tray icon
    requireInteraction: true,
    // Tag ensures no stacking duplicates
    tag: "message-notification",
    // Renotify ensures popup if already shown
    renotify: true,
    // Require interaction if you want the notification to stay
    requireInteraction: true,
  };

  //  Show popup notification
  self.registration.showNotification(notificationTitle, notificationOptions);
});
