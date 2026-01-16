# Návod: Registrace Microsoft aplikace pro Outlook integraci

## Krok 1: Vytvoření aplikace v Azure Portal

1. Jdi na https://portal.azure.com
2. Vyhledej **"App registrations"** nebo **"Registrace aplikací"**
3. Klikni **"New registration"** / **"Nová registrace"**

### Vyplň formulář:

| Pole | Hodnota |
|------|---------|
| **Name** | `AI-Kosik-Agent` (nebo libovolný název) |
| **Supported account types** | `Accounts in any organizational directory and personal Microsoft accounts` |
| **Redirect URI** | Vyber `Public client/native (mobile & desktop)` a zadej: `http://localhost` |

4. Klikni **"Register"**

## Krok 2: Získej Client ID

Po vytvoření aplikace uvidíš **Overview** stránku:

- **Application (client) ID** - toto je tvůj `MICROSOFT_CLIENT_ID`
- Zkopíruj ho

## Krok 3: Nastav oprávnění (API Permissions)

1. V levém menu klikni na **"API permissions"**
2. Klikni **"Add a permission"**
3. Vyber **"Microsoft Graph"**
4. Vyber **"Delegated permissions"**
5. Přidej tyto permissions:
   - `User.Read` ✅ (už by mělo být)
   - `Mail.Read`
   - `Mail.Send`
   - `Mail.ReadWrite`
   - `Calendars.Read`
   - `Calendars.ReadWrite`

6. Klikni **"Add permissions"**

> **Poznámka:** Pro osobní účty (outlook.com, hotmail.com) NEPOTŘEBUJEŠ admin consent.
> Pro firemní účty (Office 365) může být potřeba admin consent.

## Krok 4: Povol Public client flows

1. V levém menu klikni na **"Authentication"**
2. Sroluj dolů na **"Advanced settings"**
3. U **"Allow public client flows"** nastav **Yes**
4. Klikni **"Save"**

## Krok 5: Nastav credentials v .env

Přidej do `.env` souboru:

```
MICROSOFT_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

## Krok 6: Otestuj autentizaci

```bash
cd C:\Users\JakubMichna\WORK\AI-KOSIK\.claude\skills\outlook
python outlook_helper.py --auth
```

Měl bys vidět:
```
🔐 MICROSOFT AUTHENTICATION
============================================================

To sign in, use a web browser to open the page https://microsoft.com/devicelogin 
and enter the code XXXXXXXX to authenticate.
```

1. Otevři odkaz v prohlížeči
2. Zadej kód
3. Přihlas se svým Microsoft účtem
4. Potvrď oprávnění

## Hotovo! 🎉

Teď můžeš používat:
```bash
python outlook_helper.py --emails 5
python outlook_helper.py --calendar 7
```

---

## Alternativa: Firemní účet (Office 365)

Pro firemní účty potřebuješ:

1. Tenant ID (ID organizace)
2. Admin consent pro permissions

V tom případě změň v `outlook_helper.py`:
```python
AUTHORITY = "https://login.microsoftonline.com/{tenant-id}"
```

---

## Troubleshooting

### "AADSTS700016: Application not found"
- Zkontroluj CLIENT_ID v .env
- Počkej pár minut po vytvoření aplikace

### "AADSTS65001: User has not consented"
- Znovu spusť autentizaci a potvrď oprávnění

### "AADSTS7000218: Public client flows not enabled"
- Jdi do Authentication a povol "Allow public client flows"

### Token expiroval
- Spusť znovu: `python outlook_helper.py --auth`
- Tokeny vydrží typicky 1 hodinu, refresh token déle
