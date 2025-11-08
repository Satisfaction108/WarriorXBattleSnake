# Deploy Your Battlesnake to Render.com

This guide will walk you through deploying your Battlesnake to Render.com step-by-step.

## Prerequisites

- A GitHub account with this repository pushed to GitHub
- A Render.com account (free tier available)

## Step-by-Step Deployment Instructions

### Step 1: Push Your Code to GitHub

If you haven't already, push this repository to GitHub:

```bash
git add .
git commit -m "Initial Battlesnake setup"
git push origin main
```

### Step 2: Sign Up for Render.com

1. Go to [https://render.com](https://render.com)
2. Click **"Get Started"** or **"Sign Up"**
3. Sign up using your GitHub account (recommended for easier deployment)
4. Authorize Render to access your GitHub repositories

### Step 3: Create a New Web Service

1. Once logged in, click **"New +"** button in the top right
2. Select **"Web Service"** from the dropdown menu

### Step 4: Connect Your Repository

1. You'll see a list of your GitHub repositories
2. Find **"WarriorXBattleSnake"** (or your repository name)
3. Click **"Connect"** next to it

   **Note:** If you don't see your repository:
   - Click **"Configure account"** to grant Render access to more repositories
   - Select the repository and save
   - Return to Render and refresh

### Step 5: Configure Your Web Service

Fill in the following settings:

- **Name:** `warriorx-battlesnake` (or any name you prefer)
- **Region:** Choose the closest region to you (e.g., Oregon, Frankfurt, Singapore)
- **Branch:** `main` (or your default branch)
- **Root Directory:** Leave blank
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python main.py`

### Step 6: Select Free Plan

1. Scroll down to **"Instance Type"**
2. Select **"Free"** plan
   - Free tier includes:
     - 750 hours/month (enough for continuous running)
     - Automatic sleep after 15 minutes of inactivity
     - Wakes up automatically when accessed

### Step 7: Advanced Settings (Optional)

Click **"Advanced"** to expand advanced settings:

- **Auto-Deploy:** Leave enabled (recommended) - automatically deploys when you push to GitHub
- **Environment Variables:** The PORT variable is automatically set by Render

### Step 8: Deploy!

1. Click **"Create Web Service"** at the bottom
2. Render will now:
   - Clone your repository
   - Install dependencies from `requirements.txt`
   - Start your Battlesnake server
   - Assign you a public URL

3. Wait for the deployment to complete (usually 2-5 minutes)
4. You'll see logs in real-time showing the build and deployment process

### Step 9: Get Your Battlesnake URL

Once deployment is complete:

1. You'll see **"Your service is live 🎉"** at the top
2. Your Battlesnake URL will be displayed, something like:
   ```
   https://warriorx-battlesnake.onrender.com
   ```
3. Click the URL to test it - you should see your Battlesnake info JSON:
   ```json
   {"apiversion":"1","author":"","color":"#888888","head":"default","tail":"default"}
   ```

### Step 10: Register Your Battlesnake

1. Go to [https://play.battlesnake.com](https://play.battlesnake.com)
2. Sign in or create an account
3. Click **"Create Battlesnake"**
4. Fill in the form:
   - **Name:** WarriorX (or your preferred name)
   - **URL:** Your Render URL (e.g., `https://warriorx-battlesnake.onrender.com`)
   - **Description:** Optional description
5. Click **"Save"**
6. Your Battlesnake is now ready to play!

### Step 11: Test Your Battlesnake

1. On play.battlesnake.com, click **"Play Game"**
2. Select your Battlesnake
3. Choose game mode (Solo, Duel, or Custom)
4. Click **"Start Game"**
5. Watch your Battlesnake in action!

## Troubleshooting

### Service Won't Start

- Check the logs in Render dashboard for error messages
- Ensure `requirements.txt` has `Flask==2.3.2`
- Verify `main.py` and `server.py` are present

### Battlesnake Not Responding

- Make sure your service is not sleeping (free tier sleeps after 15 min of inactivity)
- Visit your Render URL in a browser to wake it up
- Check Render logs for any runtime errors

### Slow Response Times

- Free tier may have cold starts (takes a few seconds to wake up)
- Consider upgrading to a paid plan for always-on service
- Choose a Render region closer to Battlesnake game servers (Oregon recommended)

### Can't Find Repository

- Make sure you've pushed your code to GitHub
- Grant Render access to your repository in GitHub settings
- Try disconnecting and reconnecting your GitHub account in Render

## Updating Your Battlesnake

When you make changes to your code:

1. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Updated move logic"
   git push origin main
   ```

2. Render will automatically detect the changes and redeploy (if Auto-Deploy is enabled)

3. Wait for deployment to complete (check Render dashboard)

4. Your Battlesnake is now updated!

## Free Tier Limitations

- **Sleep after inactivity:** Service sleeps after 15 minutes of no requests
- **Wake-up time:** Takes 30-60 seconds to wake up from sleep
- **Monthly hours:** 750 hours/month (enough for continuous use)
- **Performance:** Shared resources, may be slower than paid tiers

**Tip:** For competitive play, consider upgrading to a paid plan ($7/month) for:
- Always-on service (no sleep)
- Faster response times
- More resources

## Next Steps

- Customize your Battlesnake appearance in `main.py` (`info()` function)
- Improve your move logic in `main.py` (`move()` function)
- Test locally before deploying
- Join the Battlesnake Discord community for tips and strategies

## Useful Links

- [Render Dashboard](https://dashboard.render.com/)
- [Battlesnake Play](https://play.battlesnake.com)
- [Battlesnake Docs](https://docs.battlesnake.com)
- [Battlesnake API Reference](https://docs.battlesnake.com/api)

---

**Happy Battling! 🐍**

