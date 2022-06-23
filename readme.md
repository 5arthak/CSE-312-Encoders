# Encoder's Grocery List
Created by Sarthak, Korey, Mausam, and Michelle

Check out our [demo](http://www.encoderlist.click)

## Inspiration
As college students living off-campus, we need to make our food. Balancing school along with time to buy ingredients to make healthy meals can often be a hassle.
- No time to restock pantries.
- Grocery trips are an inconvenience for those without cars.
- Coordinating what to buy with housemates.

## What it does
A sharable grocery list to easily store and view what groceries to buy. Instead of keeping one list, one sharable list allows better coordination. If somebody is shopping, they can pick up items for their housemates or friends without asking them specifically. Having a set list also results in shorter grocery trips.

Features:
1. User Accounts with Secure Authentication.
2. Real-time updated lists through WebSocket.
3. View all online users and send private messages to them.
4. Users are notified in real-time when pm is received and can reply.
5. Share deals by uploading a description and a corresponding image.

## Technology Used: 
Frontend: HTML, CSS, and Vanilla JS
Backend: Python (WebSocket, SocketServer), MongoDB
Deploy: Docker, AWS EC2, AWS Route 53

We took everything we learned from our Web App course to make this app. We decided not to use any framework such as Flask, Django, or React and built everything in pure Python and Javascript. We implemented low-level bit parsing and template engine in pure Python. This allowed us to have a better understanding of how these frameworks work and appreciate how they simplify web development for us.

## Challenges we ran into
The challenging part of creating this web app was with the WebSockets. We had to make sure that the WebSockets only communicated with the correct page and the correct user. Then the WebSocket must also send the data to MongoDB for storage such that the items will still there after the connection is lost.

## Accomplishments that we're proud of
We were working on the app towards the end of the semester. With finals and exams coming up, we're proud that we were able to coordinate our time to work on the project and finished it on time.

## What we learned
We learned how to Dockerize our web app with MongoDB and Nginx for deployment on a server. Some of us had built web apps before, but not on this level so we all learned a lot about the underlying technology of the web.

## What's next for Encoder's Grocery List
Adding an SSL certificate to the web app. Improving web UI and developing a mobile app. Video chats with WebRTC to allow in app video calls during a grocery trip. Improve list features such as sharing with specific people.