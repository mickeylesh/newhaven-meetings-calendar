# New Haven CT Government Meeting Calendar

Auto-generated iCalendar feed of New Haven, CT government meetings,
sourced daily from [Legistar](https://newhaven-ct.legistar.com/Calendar.aspx).

★ Full **Board of Alders** meetings are starred in the event title so they
stand out in any calendar app.

---

## Subscribe

**Calendar URL:**
```
https://<YOUR_GITHUB_USERNAME>.github.io/<YOUR_REPO_NAME>/calendar.ics
```
Replace the placeholders with your actual GitHub username and repository name
after completing the setup steps below.

| App | How to subscribe |
|-----|-----------------|
| Google Calendar | Settings → Add calendar → **From URL** |
| Apple Calendar | File → **New Calendar Subscription…** |
| Outlook (web) | Add calendar → **Subscribe from web** |
| Thunderbird | New Calendar → **On the Network** → iCalendar (ICS) |

---

## Setup

### 1. Create the repository

```bash
gh repo create newhaven-meetings-calendar --public --source=. --push
```

Or push this directory to a new GitHub repo manually.

### 2. Enable GitHub Pages

In the repository on GitHub:

1. **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / `(root)`
4. Click **Save**

After the first workflow run (or after manually triggering it), your calendar
will be live at:
```
https://<YOUR_GITHUB_USERNAME>.github.io/<YOUR_REPO_NAME>/calendar.ics
```

### 3. Trigger the first run

Either push a commit (the `calendar.ics` file is included in the initial
commit) or go to **Actions → Update Calendar → Run workflow**.

---

## How it works

| File | Purpose |
|------|---------|
| `generate_calendar.py` | Scrapes Legistar, writes `calendar.ics` |
| `.github/workflows/update-calendar.yml` | Runs the script daily at ~6 am ET and commits any changes |
| `calendar.ics` | Generated file served by GitHub Pages |

The workflow runs at **11:00 UTC** (6 am EST / 7 am EDT). You can also
trigger it manually from the Actions tab at any time.

---

## Local development

```bash
pip install -r requirements.txt
python generate_calendar.py
# → writes calendar.ics
```

Requires Python 3.9+.
