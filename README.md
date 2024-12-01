**XM Playlist Scraper**

This is a simple scraper to automate the task of collecting how many plays a particular artist has had during a period.  
Artists and tracks can be added in the albums.py file.  
All that is required for authentication is to add a refresh token to your .env file. xmplaylist.com uses firebase authentication and their refresh tokens never expire. You can find a refresh token by logging in (through email authentication), and then checking the firebase storage with your dev tools and copying the refresh token.  
  
  
*Installation*
```
INSTALL VENV  
python3 -m venv venv
```
  
```
ACTIVATE VENV  
. venv/bin/activate
```
  
```
INSTALL REQUIREMENTS
pip install -r requirements.txt
```
  
```
RUN APP
python app.py
```
  