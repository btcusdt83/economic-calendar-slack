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
GitHub Actions schemaläggs dagligen kl. 08:00 med `timezone: Europe/Stockholm`, vilket automatiskt hanterar sommar- och vintertid. Försenade jobb skickar fortfarande rapporten. GitHub kan fördröja eller tappa schemalagda jobb; exakt leverans kl. 08:00 garanteras inte. I publika repositoryn stängs schemat av efter 60 dagar utan repositoryaktivitet.

## Källa och begränsningar
Datakälla: https://nfs.faireconomy.media/ff_calendar_thisweek.json

Tillgänglighet och användningsvillkor behöver verifieras. Om datakällan är nere misslyckas körningen; den hittar inte på nyheter. Endast `impact: High` inkluderas. Rapporten använder svenska rubriker och översättningar av vanliga ekonomiska händelser och visar tider i Europe/Stockholm. Händelser som saknar översättning behåller originaltiteln.
