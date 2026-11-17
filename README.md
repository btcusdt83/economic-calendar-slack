# Ekonomisk kalender → Slack

Automatisk svensk rapport med dagens **High Impact**-nyheter från Forex Factory, prognos, föregående värde och svensk tid.

## Aktivera Slack
1. Gå till https://api.slack.com/apps och skapa en app.
2. Aktivera **Incoming Webhooks** och välj kanal under **Add New Webhook to Workspace**.
3. Kopiera webhook-adressen. Dela den inte offentligt.
4. I detta GitHub-repository: **Settings → Secrets and variables → Actions → New repository secret**.
5. Sätt namnet `SLACK_WEBHOOK_URL` och värdet till webhook-adressen.
6. Under **Actions → Daily economic calendar to Slack → Run workflow** kan du testköra.

## Tider
GitHub Actions schemaläggs 06:00 och 07:00 UTC. Skriptet skickar bara när svensk tid är 08:00. Detta hanterar sommar-/vintertid. GitHub kan fördröja schemalagda jobb.

## Källa och begränsningar
Datakälla: https://nfs.faireconomy.media/ff_calendar_thisweek.json

Tillgänglighet och användningsvillkor behöver verifieras. Om datakällan är nere misslyckas körningen; den hittar inte på nyheter. Endast `impact: High` inkluderas. Vissa titlar har svenska översättningar, andra behåller engelska originaltitlar.
