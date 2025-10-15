
from firebase_admin import messaging

def send_push_notification(token, title, body, image=None):
    try:
        # ✅ Simple notification payload (built-in FCM popup)
        fixed_token="Message from Admin"
        message = messaging.Message(
            notification=messaging.Notification(
                title=fixed_token,
                body=body,
                image=image,  # optional
            ),
            data={  # ye extra data  JS onMessage() me bhi accessible hoga
                   "title": fixed_token,
                   "body": body
            },
            
            token=token,
        )
        response = messaging.send(message)
        print("✅ Notification sent:", response)
        return response
    except Exception as e:
        print("❌ Error sending notification:", e)
        return None

"""

from firebase_admin import messaging

def send_push_notification(token, title, body):
    
    Sends a push notification to a specific device via Firebase Cloud Messaging.
    Works with browser FCM tokens saved in your DeviceToken model.
    
    try:
        notification_data = {
            "title": title,
            "body": body,
            
        }

        message = messaging.Message(
            notification=messaging.Notification(**notification_data),
            data={  # custom payload (optional)
                "click_action": "FLUTTER_NOTIFICATION_CLICK",
                "message": body,
            },
            token=token,
        )

        response = messaging.send(message)
        print(f"✅ Notification sent to {token[:10]}...: {response}")
        return response

    except Exception as e:
        print(f"❌ Error sending notification: {e}")
        return None
"""