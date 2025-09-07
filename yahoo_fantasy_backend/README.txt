Instructions:


1. Replace YOUR_REFRESH_TOKEN in app.py with your refresh token from Yahoo OAuth.
2. Push the folder to GitHub.
3. Deploy on Railway.
4. Update ai-plugin.json with Railway URL.
5. Install plugin in ChatGPT.
6. Access endpoints:
- /players
- /teams
- /matchups


The backend now automatically refreshes the access token using the refresh token, so you never need to manually update it.