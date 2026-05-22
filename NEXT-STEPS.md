# Next Steps — Quick Reference

> Things you (the project rep) need to do that I can't do for you.

## Right now (next 1 hour)

### 1. GitHub repo + first push

Open a terminal in this folder (`medicase-orchestrator/`) and run:

```bash
git init
git add .
git commit -m "Initial scaffold: README, docs, agent specs, demo script"
```

Then on github.com:
- Create a new **public** repo named `medicase-orchestrator`
- Don't add a README from the GitHub UI (we have one)
- Copy the "push existing repo" commands GitHub shows you, e.g.:

```bash
git remote add origin https://github.com/<your-user>/medicase-orchestrator.git
git branch -M main
git push -u origin main
```

After push, search the README and replace every `<your-user>` placeholder with your actual GitHub username.

### 2. Calendar these UiPath live sessions

All free, all in English, all online. Add to your calendar now so you don't miss them:

| Date | Session |
|---|---|
| **26 May 2026** | AgentHack General Overview & Logistics |
| **27 May 2026** | Connector Corner: Agent Builder |
| **28 May 2026** | Dev Dives: Coding Agents (Claude Code) |
| **9 Jun 2026** | AgentHack Winner Overview & Best Practices ⭐ |
| **15 Jun 2026** | AgentHack Office Hour ⭐ |
| **23 Jun 2026** | Connector Corner: Maestro Case Management |
| **25 Jun 2026** | Dev Dives: Troubleshoot Coding Agents |

Links in [docs/learning-path.md](docs/learning-path.md).

### 3. UiPath Academy enrollment

While waiting for Labs access (3 business days):

- Go to https://academy.uipath.com/learning-plans
- Search "Maestro" and "Agent Builder"
- Enroll in any introductory plans (all free)
- Aim for **2 hours/day** of viewing

## Within 3 business days (Labs access arrives)

When you get the email confirmation from `Andreea from the UiPath Community team`:

1. Log into the provided Cloud sandbox URL
2. Verify you can open UiPath Studio Web
3. Create your first Maestro Case (1-stage toy case) — just to feel the interface
4. Document any first impressions / blockers in `docs/journal.md` (create as you go)

## This week's milestones

- [ ] GitHub repo public, first commit pushed
- [ ] All `<your-user>` placeholders replaced in README
- [ ] All UiPath live sessions on calendar
- [ ] UiPath Academy: at least 2 intro modules completed
- [ ] Devpost project page: paste draft content from `submission/devpost-project-page.md` as **a draft** (you can keep updating until 29 Jun)

## Decisions still open (no rush)

- **Team:** Solo, or invite up to 3 others? (Max team size is 4. Adding someone changes the Labs access form behavior — must be done before access is granted, can't add later. If you want a team, decide in next 24 hours.)
- **Payment routing:** If you win, payment goes via W-8BEN form + bank transfer. Open a Wise or Payoneer account soon if you don't have one — saves time at prize delivery.

## Resources cheat sheet

| Need | Go to |
|---|---|
| Hackathon home | https://uipath-agenthack.devpost.com/ |
| Hackathon resources | https://uipath-agenthack.devpost.com/resources |
| Maestro Use Case Explorer | https://maestro-use-case.azurewebsites.net/ |
| UiPath Academy | https://academy.uipath.com/learning-plans |
| UiPath Forum (Q&A) | https://forum.uipath.com/ |
| UiPath Skills (Claude Code skills) | https://github.com/UiPath/skills |
| UiPath Python SDK | https://github.com/UiPath/uipath-python |
| UiPath CLI (npm) | https://www.npmjs.com/package/@uipath/cli |
