# Manga Notifier
___
Manga Notifier checks for new manga chapters and
sends an email whenever there is an update.

## How It Works
___
1. Use BeautifulSoup to parse website data and check for new chapter.
2. Use Gmail API to send email about new chapter to client.
3. Optionally can be run as a service that starts on startup.
