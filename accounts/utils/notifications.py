from firebase_admin import messaging

def send_push_notification(token, title, body):
    try:
        # ✅ Simple notification payload (built-in FCM popup)
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
        )
        response = messaging.send(message)
        print("✅ Notification sent:", response)
        return response
    except Exception as e:
        print("❌ Error sending notification:", e)
        return None
