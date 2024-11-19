# GuestPoast
Do you run a static Jekyll blog? Are you tired of using off-site services to build a guestbook for your visitors to sign, only to have to have ads, or intrusive elements that shouldn't be on your site, or even _worse_ ... styling that you can't edit? Well, do I have ... somewhat of a solution for you.

Preface: I've accomplished this by utilizing a domain attached to a VPS with HTTPS enabled. It won't work without HTTPS. Don't even try. Now, in my last piece of web development code, I was made aware that Github can actually be used as a personal VPS for free, with limitations on used seconds per month. I'm _assuming_ that you could maybe do that with this. I'm using my VPS, because it's where all of my active projects are running, and I pay for it.

*Note: I built this late at night, and although there are no errors on my end, it's possible you may run into one. Here's hoping I've written these instructions clearly enough for you.*

With that aside, let's get started.

First, we'll deal with the Jekyll side of things. Take both the "assets" and "pages" folder, and slap them into your Jekyll blog directory. Either think to "guestbook.css" in the head of your site, or add it to your _current_ css file. Whichever you choose is fine.

Take the button from the HTML fragment and place it somewhere on your page (unless you don't want to use a button?), then edit "comments.js" and supply the address to the server that'll be running the python and reverse proxy.

Give it a build and see how it looks. Like it? Okay.

We're finished with this part.

Now, the hard part.

Log onto your VPS/server, and create a folder. I'm running in the root home directory (you should probably create a user for this), so I created a folder called "guestbook." Inside, take comments.py and comments.json, and drop them in. Now create an environment. I went with bookenv.
```
python3 -m venv bookenv
```
Now activate it.
```
source bookenv/bin/activate
```
Install the requirements.
```
pip install flask flask-cors gunicorn
```
Next, create the gunicorn config.
```
nano gunicorn_config.py
```
And paste this into it.
```
bind = "0.0.0.0:5000"
workers = 3
```
Save and exit, then back out of the "guestbook" folder.
```
cd ..
```
Time to setup Nginx. If you don't already, you should be running this on a domain with HTTPS. I recommend using certbot to obtain your certificates. If you don't already have Nginx installed, do it.
```
sudo apt-get update
sudo apt-get install nginx
```
Now turn it on.
```
sudo systemctl start nginx.service
```
"Nova, are we freakin' done yet?" 

No, we're not.

Now you'll need to edit your Nginx configuration.
```
sudo nano /etc/nginx/sites-available/default
```
And put this in it.
```
server {
    listen 80;
    server_name your.server.address; # Replace with your domain

    # Redirect HTTP to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name your.server.address; # Replace with your domain

    ssl_certificate /etc/letsencrypt/live/your.server.address/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your.server.address/privkey.pem;

    root /var/www/html; # Default web root directory
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    location /comments {
        proxy_pass http://127.0.0.1:5000/comments;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

}
```
Voila, now you have a reverse proxy.

Now, you'll need the guestbook comment fetcher and store to be running at all times, so that people can comment, and your website can fetch and display them! So, we'll setup the workers.
```
sudo nano /etc/systemd/system/guestbook.service
```
Paste in this:
```
[Unit]
Description=Gunicorn instance to serve guestbook
After=network.target

[Service]
User=root #replace this with whatever user you're on
Group=root #replace this with the group your user is in
WorkingDirectory=/username/guestbook
Environment="PATH=/username/guestbook/bookenv/bin"
ExecStart=/username/guestbook/bookenv/bin/gunicorn --config gunicorn_config.py comments:app

[Install]
WantedBy=multi-user.target
```
NOW we're almost done. Exit out of the guestbook config, and then reload the daemon.
```
sudo systemctl daemon-reload
```
Then, for good measure, reload Nginx.
```
sudo systemctl reload nginx
```
It's time to set us up the geustbook service and runners.
```
sudo systemctl start guestbook
sudo systemctl enable guestbook
```
This will both start up the guestbook service, and enable it to run on system startup. But, we'll also want to test to see if it's actually running, so, type in this:
```
sudo systemctl status guestbook
```
If all went well, and you've configured this properly, you're done! The reverse proxy is running. The guestbook service is running. Your website is now ready to store and retrieve comments to your guestbook! Build your site to wherever you have it running live, and open up your browser's dev console to make sure you aren't getting CORS errors. If there isn't any red badness being thrown at you in that console, close it. Now, do a test comment! Once you've commented, refresh the page, and you should see the comment you made.

You can verify that it's being stored by navigating back to the server hosting the python, then into the "guestbook" directory, and type:
```
nano comments.json
```
And the test comment you just made on your website should be store inside of this file!

Whew! What a journey! But now you have a functional guestbook on your Jekyll blog that doesn't require any outside services aside from a server. And server's can be cheap, especially if you're only using it for a guestbook.
