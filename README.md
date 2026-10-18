# Higashihiroshima daily weather notification

At 07:00 Japan Standard Time, GitHub Actions fetches today's forecast and yesterday's observed high/low from Open-Meteo, then sends an iPhone push notification through ntfy.

## Setup

1. Install **ntfy** from the App Store and subscribe to a long, hard-to-guess topic name. Topic names are public; anyone who knows the name can publish/read notifications. Do not reuse a password or personal identifier.
2. Create a GitHub repository. For the simplest no-cost Actions setup, make it **Public** (the workflow code is public, but the topic is stored as a GitHub Actions secret). If you choose Private, check the current included Actions minutes for your account.
3. Add these files to the repository, preserving the `.github/workflows/daily-weather.yml` path.
4. In the repository, open **Settings → Secrets and variables → Actions → New repository secret**. Set the name to `NTFY_TOPIC` and the value to the exact topic you subscribed to in ntfy.
5. Open **Actions**, enable workflows if prompted, select **Daily weather notification**, and choose **Run workflow** to test. Confirm the notification arrives on the iPhone.
6. The scheduled run is `22:00 UTC`, which is `07:00 JST` on the following calendar day. GitHub may start scheduled workflows late during busy periods, and scheduled runs can be disabled after prolonged repository inactivity.

## Data and costs

- Open-Meteo's no-key API is free for non-commercial use, with fair-use limits; attribution is included in the notification.
- The previous-day comparison uses Open-Meteo's archive data (yesterday's observed daily high/low), not yesterday's forecast.
- GitHub Actions standard runners are free for public repositories. ntfy's hosted service and iOS app offer a free way to publish and subscribe; public topic names are not private.
- Weathernews does not currently provide a generally available free official API suitable for this personal workflow; this setup uses Open-Meteo.

## Coordinates

The script uses approximate city-center coordinates (34.426, 132.743). Change `LATITUDE` and `LONGITUDE` in `weather.py` if you want a specific neighborhood.
