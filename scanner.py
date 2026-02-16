import cv2
from pyzbar.pyzbar import decode
import requests
import time


URL = "http://127.0.0.1:8000/mark-attendance/"


cap = cv2.VideoCapture(0)

print("Scanner started... Press 'q' to quit.")


last_scanned = ""
last_time = 0

while True:
    success, frame = cap.read()
    
  
    for code in decode(frame):
        student_id = code.data.decode('utf-8')
        
      
        if student_id != last_scanned or (time.time() - last_time) > 3:
            print(f"Detected ID: {student_id}")
            
           
            try:
                response = requests.get(f"{URL}{student_id}/")
                data = response.json()
                print(f"Server Response: {data['message']}")
            except Exception as e:
                print(f"Error connecting to server: {e}")

            last_scanned = student_id
            last_time = time.time()

   
    cv2.imshow('Attendance Scanner', frame)
    
  
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()












