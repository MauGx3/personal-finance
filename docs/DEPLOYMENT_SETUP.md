# Documentation Deployment Setup

This guide explains how to set up automated documentation building and deployment using GitHub Pages.

## Setup Steps

### 1. Enable GitHub Pages

1. Go to your GitHub repository
2. Click on **Settings** → **Pages** (in the left sidebar)
3. Under **Source**, select **GitHub Actions**
4. The documentation workflow will now automatically deploy to GitHub Pages

### 2. Verify Workflow Permissions

1. Go to **Settings** → **Actions** → **General**
2. Under **Workflow permissions**, ensure **Read and write permissions** is selected
3. Check **Allow GitHub Actions to create and approve pull requests** if you want automated PRs

### 3. First Deployment

The documentation will be automatically built and deployed when you:
- Push changes to the `main` branch that affect the `docs/` folder
- Push changes to Python code that affects the API documentation
- Manually trigger the workflow from the Actions tab

### 4. Access Your Documentation

After the first successful deployment, your documentation will be available at:
```
https://yourusername.github.io/personal-finance/
```

Replace `yourusername` with your actual GitHub username.

## Local Development

### Build Documentation Locally

```bash
# Quick build (recommended)
./build-docs.sh

# Manual build
cd docs
make html
# Open docs/_build/html/index.html
```

### Live Reload During Development

```bash
cd docs
make livehtml
# Visit http://localhost:9000
```

## Workflow Details

The GitHub Actions workflow (`.github/workflows/docs.yml`) automatically:

1. **Triggers on**:
   - Push to `main` branch with changes in `docs/` or Python code
   - Pull requests affecting documentation
   - Manual workflow dispatch

2. **Build process**:
   - Sets up Python 3.11 environment
   - Installs dependencies from `requirements.txt` and `requirements-docs.txt`
   - Configures Django for documentation building
   - Builds Sphinx documentation
   - Uploads artifacts

3. **Deployment** (main branch only):
   - Deploys built HTML to GitHub Pages
   - Makes documentation available at the GitHub Pages URL

## Troubleshooting

### Build Fails Due to Django Setup

If the build fails because of Django configuration, check:
- Environment variables in the workflow
- Django settings module (`config.settings.local`)
- Database URL configuration

### Sphinx Build Errors

Common issues and solutions:
- **Import errors**: Ensure all dependencies are in `requirements-docs.txt`
- **Syntax errors in .rst files**: Use `doc8` to validate reStructuredText
- **Cross-reference errors**: Check that referenced sections exist

### GitHub Pages Not Updating

- Check the Actions tab for workflow status
- Verify GitHub Pages is configured to use GitHub Actions as source
- Clear browser cache or try incognito mode

## Manual Deployment Alternative

If you prefer manual control over deployments:

```bash
# Build documentation
./build-docs.sh

# Create gh-pages branch (first time only)
git checkout --orphan gh-pages
git rm -rf .
cp -r docs/_build/html/* .
git add .
git commit -m "Initial documentation"
git push origin gh-pages

# For updates
git checkout main
./build-docs.sh
git checkout gh-pages
rm -rf *
cp -r docs/_build/html/* .
git add .
git commit -m "Update documentation"
git push origin gh-pages
```

## Custom Domain (Optional)

To use a custom domain for your documentation:

1. Add a `CNAME` file to `docs/_static/` with your domain name
2. Configure DNS to point to `yourusername.github.io`
3. Update the workflow if needed to handle custom domain requirements