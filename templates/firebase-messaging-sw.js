// firebase-messaging-sw.js

importScripts("https://www.gstatic.com/firebasejs/10.7.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.7.0/firebase-messaging-compat.js");

firebase.initializeApp({
  apiKey: "AIzaSyCRCA4aoMiVMrTF8zhyb77VeDObjyVSeY4",
  authDomain: "my-expenses-chat.firebaseapp.com",
  projectId: "my-expenses-chat",
  storageBucket: "my-expenses-chat.firebasestorage.app",
  messagingSenderId: "112414536425",
  appId: "1:112414536425:web:310af2bd54389763a73678"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  console.log("📩 Background message received:", payload);

  const notificationTitle = payload.notification.title || "New Message";
  const notificationOptions = {
    body: payload.notification.body || "You have a new message",
    icon: "/static/images/chat-icon.png"
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});
