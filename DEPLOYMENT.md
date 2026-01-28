# Deployment Guide

## Two Deployment Modes

This add-in supports two deployment modes:

### 1. Local Development (Excel Desktop)
- **Manifest:** `manifest.xml`
- **Add-in URL:** https://localhost:3000
- **Dashboard URL:** https://claudecode-yuyingcrexcelribbon.streamlit.app
- **Use for:** Development and Excel Desktop testing

**Setup:**
```bash
npm run dev-server
```

### 2. Production (Excel Online & Desktop)
- **Manifest:** `manifest-online.xml`
- **Add-in URL:** https://yuyingcr25-discover.github.io/claudecode
- **Dashboard URL:** https://claudecode-yuyingcrexcelribbon.streamlit.app
- **Use for:** Excel Online and production deployments

**Deployment:**
The add-in automatically deploys to GitHub Pages when you push to the main branch.

## Deploying Updates

1. **Make your code changes**
2. **Build locally to test (optional):**
   ```bash
   npm run build
   ```
3. **Commit and push:**
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```
4. **GitHub Actions will automatically:**
   - Build the production version
   - Deploy to GitHub Pages at: https://yuyingcr25-discover.github.io/claudecode

5. **In Excel Online:**
   - Remove the old add-in (Insert → Add-ins → MY ADD-INS → Remove)
   - Upload `manifest-online.xml`
   - Or simply hard refresh (Ctrl + Shift + R)

## URLs Summary

| Component | Local (Dev) | Production |
|-----------|-------------|------------|
| Add-in Frontend | https://localhost:3000 | https://yuyingcr25-discover.github.io/claudecode |
| Dashboard | http://localhost:8501 | https://claudecode-yuyingcrexcelribbon.streamlit.app |
| Manifest | manifest.xml | manifest-online.xml |

## GitHub Pages Setup (One-Time)

To enable GitHub Pages for the first deployment:

1. Go to your GitHub repository: https://github.com/yuyingcr25-discover/claudecode
2. Click **Settings**
3. Click **Pages** (in the left sidebar)
4. Under **Source**, select **GitHub Actions**
5. The deployment will automatically run on the next push

## Troubleshooting

### Add-in doesn't load in Excel Online
- Ensure you're using `manifest-online.xml` (not `manifest.xml`)
- Clear your browser cache (Ctrl + Shift + Delete)
- Check GitHub Actions completed successfully
- Verify GitHub Pages is enabled in repository settings

### Changes not reflecting
- Check GitHub Actions workflow completed (green checkmark)
- Hard refresh Excel Online (Ctrl + F5)
- Remove and re-upload the manifest

### Analytics button not working
- Ensure the Streamlit app is running
- Check the URL in src/config.ts matches your Streamlit deployment
