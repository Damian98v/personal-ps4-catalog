# Personal PS4 Catalog

Persoonlijke catalogus voor de bestaande [PS4 Games Installer](https://github.com/e1z0/PS4-Games-Installer).
De PS4 downloadt toegestane packages rechtstreeks van de oorspronkelijke ontwikkelaar. Deze repository bevat geen PKG-bestanden.

**Games JSON URL:**

```text
https://damian98v.github.io/personal-ps4-catalog/games.json
```

## Aansluiten op je PS4

1. Activeer je bestaande GoldHEN-omgeving en open PS4 Games Installer. Gebruik een recente officiële versie met HTTPS-ondersteuning.
2. Ga naar **OPTIONS → Settings → Games JSON URL** en vul bovenstaande URL exact in.
3. Kies **Test connection**, daarna **Save settings**.
4. Kies **OPTIONS → Refresh library**. Open **Available** (L1/R1 wisselt Installed/Available).
5. Selecteer **PS4 2048** en druk **X** om de installatie te bevestigen.
6. Bekijk de voortgang onder **OPTIONS → Downloads**. Wacht op **Completed**.

De PS4 heeft internet nodig en moet zowel GitHub Pages als GitHub releasebestanden kunnen bereiken.
De juiste datum/tijd op de PS4 is nodig voor TLS. Je computer hoeft na publicatie niet aan te blijven.
HTTPS-packages worden door de installer eerst naar interne opslag gedownload. Houd de app tijdens het downloaden open en reserveer ruimte voor het package én de installatie.

**De catalogus is op afstand getest; een installatie op fysieke PS4-hardware is niet door Codex uitgevoerd.**

### Bekend probleem met installer r40

De nieuwste officiële download is momenteel r40. De gebundelde certificaten en algemene HTTPS-reparaties zijn echter pas **na r40** aan de officiële broncode toegevoegd. Een geslaagde catalogusparsertest op de computer bewijst daarom niet dat de r40-app GitHub via HTTPS kan bereiken.
Bij `Send request … Check the JSON endpoint` ondanks werkend internet: controleer de appversie (OPTIONS → About), volledige foutcode en PS4-klok. De gebruiker heeft deze fout met r40 gemeld. Pas hiervoor niet de PS4-systeemsoftware aan.
De handmatige Actions-workflow `Build installer with upstream HTTPS fixes` bouwt de ongewijzigde officiële broncode op revisie `f9212596bafd1011aec594cd8c5bd0d05cff938a`, draait upstreamtests en valideert het package. Dit is een eigen build van de bestaande app, geen officiële upstreamrelease; werking op de eigen PS4 moet nog worden getest. Het downloadbare artifact bevat het PKG, checksum, buildmanifest en de bijbehorende upstreambroncode.
De ongewijzigde upstream pc-tests hebben loggingproblemen en verouderde certificaatfixtures: een PS4-functie wordt in de hostfallback aangeroepen, de native HTTP-test linkt de logger niet en de HTTP-/opstartfixtures verwachten nog geen Let's Encrypt-certificaat. Alleen voor de pc-tests wordt dit na packaging aangepast; de patch wordt bijgeleverd en vóór packagehercontrole teruggedraaid. De PS4-binary bevat deze testaanpassingen niet.

**Build r48 is beschikbaar:** de [geslaagde build en download](https://github.com/Damian98v/personal-ps4-catalog/actions/runs/43461192199) bevat het artifact `ps4-installer-https-fixes` (30 dagen bewaard). Pak het ZIP-bestand uit en gebruik uitsluitend `PS4Game_installer-r48.pkg` als installatiebestand; de overige bestanden bevatten broncode, controles en herkomst.
Sluit de bestaande installer en installeer het PKG als app-update via je gebruikelijke PKG-installatiemethode (bijvoorbeeld USB of FTP). Verwijder de bestaande app niet vooraf. De Title ID blijft `PGIN00001`; packageversie is `00.48`. Open daarna de installer, bevestig bovenstaande Games JSON URL en gebruik Test connection, Save settings en Refresh library.
Deze build doorstond de volledige C++-/HTTP-testreeks en alle 19 Python-tests met de bijgeleverde host-testaanpassingen. Het package is opnieuw gevalideerd na herstel van de oorspronkelijke broncode. SHA-256: `d705be59668ac468dfb4360b9cd051f2ef7c280d5e12f83b41cb49841b54af37`. Installatie en verbinding op de eigen fysieke PS4 zijn nog niet bevestigd.

## Eerste inhoud

| Package | Packageversie | Grootte | Functie |
| --- | --- | ---: | --- |
| PS4 2048 | 1.00 | 35.454.976 bytes | Zelfstandig puzzelspel, officiële GitHub-release v1.0 |
| Apollo Save Tool | 02.40 | 22.806.528 bytes | Zelfstandig homebrewhulpmiddel voor je eigen savegames, release v2.4.0 |

Beide komen rechtstreeks van de ontwikkelaars en hebben geen commerciële gamebestanden nodig om te starten.
`SYSTEM_VER` is in beide packages nul; `min_fw` blijft daarom onbekend (`null`). Dit is geen claim dat elke firmware werkt.
De GitHub-release van 2048 is ouder dan de PKG-Zone-versie. PKG-Zone gaf tijdens de downloadcontrole HTTP 403 en is niet als werkende bron toegevoegd.
Apollo is een hulpmiddel, geen game; het staat in dezelfde lijst zodat één Games JSON URL volstaat.

## Voortaan via Codex

Open deze repository als project in Codex en zeg bijvoorbeeld:

> Voeg deze games toe aan mijn PS4-library: [namen]. Onderzoek toegestane bronnen en publiceer de gecontroleerde resultaten.

Of:

- “Voeg deze officiële homebrewrelease toe: [release-URL].”
- “Voeg dit package toe dat ik mag gebruiken: [directe PKG-URL], bron/toestemming: [uitleg].”
- “Controleer mijn PS4-library op kapotte links.”
- “Werk bestaande downloadlinks bij.”
- “Welke games kon je niet vinden?”
- “Controleer of er nieuwe homebrewversies zijn.”
- “Verwijder [titel] uit mijn catalogus.”

Codex leest `AGENTS.md`, onderzoekt de titels, controleert bron/toestemming en eventuele extra bestanden, en voert de scripts uit.
Onbekende titels worden niet blind uit zoekresultaten geïmporteerd: ze komen in `missing.json` totdat een passende geautoriseerde bron is onderzocht.
Een commerciële titel zonder geautoriseerde publieke PKG-bron kan daardoor ontbreken. Geef dan een eigen publieke downloadbron plus toestemming; accountlogins en tijdelijke ondertekende links worden niet gepubliceerd.

## Eenmalig op macOS

Installeer Git, Python **3.11+** en [GitHub CLI](https://cli.github.com/). Daarna:

```sh
gh auth login
gh repo clone Damian98v/personal-ps4-catalog
cd personal-ps4-catalog
python3 scripts/validate_catalog.py
```

Open die map in Codex. Er zijn geen Python-dependencies of draaiende servers nodig.
De eerste implementatie is op Windows uitgevoerd; dezelfde Python-scripts en GitHub Actions zijn bruikbaar vanaf macOS.

## Scripts

Bekende, onderzochte bronnen automatisch op naam oplossen en toevoegen:

```sh
python3 scripts/add_games.py 'PS4 2048' 'Apollo Save Tool'
python3 scripts/add_games.py 'Apollo Save Tool' --refresh
python3 scripts/validate_catalog.py
python3 scripts/validate_catalog.py --online --report reports/links.json
python3 -m unittest discover -s tests -v
python3 scripts/publish.py --message 'Update verified homebrew packages'
```

`--refresh` zoekt de nieuwste stabiele GitHub-release van de onderzochte bron en controleert het package opnieuw.
Dit wijzigt niet automatisch onbereikbare links. Nieuwe versies blijven aparte packages; dezelfde Content ID + packageversie + type wordt gededupliceerd.
Bij meerdere PKG-assets vereist de bron een specifiek `asset_pattern`, zodat geen PS5-build of ander package wordt gekozen.
`add_games.py` geeft exitcode 1 als een aanvraag ontbreekt of onbevestigd blijft; andere geldige aanvragen kunnen wel toegevoegd zijn. Lees de uitvoer en valideer daarna de volledige catalogus.

Nieuwe bronnen onderzoekt Codex via officiële projectwebsites/GitHub. Het script zoekt zelf ook GitHub-projectkandidaten voor onbekende namen en registreert ze in de reden van de ontbrekende aanvraag; zoekresultaten zijn geen toestemming.
Codex legt na onderzoek een bron vast in `sources.json` met `id`, naam/aliases, `repo` en `asset_pattern`, `authorization_url`, concrete `authorization`, `reviewed_on`, `standalone` en eventuele `requirements`.
Voor een eigen directe URL gebruikt de bron `allowed_urls: ["https://…/bestand.pkg"]` in plaats van `repo` en legt Codex jouw toestemming vast. Vervolgens:

```sh
python3 scripts/add_games.py 'Mijn homebrew' --source mijn-bron --url 'https://example.org/game.pkg'
```

`publish.py` voert tests en online controles uit, commit alleen bekende projectbestanden, pusht `main`, en controleert dat de publieke JSON exact overeenkomt.
Bij bestaande niet-gerelateerde wijzigingen stopt het script om die buiten de openbare commit te houden.
Als een push wel lukt maar publicatie nog niet bevestigd is, bekijk GitHub Actions en herhaal alleen:

```sh
python3 scripts/publish.py --verify-only
```

## Data en controles

- `games.json`: uitsluitend ondersteunde installer-velden in `{"DATA": {"directe-pkg-url": {...}}}`.
- `sources.json`: onderzochte toegestane bronnen en exacte URL/repositoryscope.
- `research.json`: bron, homebrewtype, release, benodigdheden en laatste succesvolle packagecontrole.
- `missing.json`: aanvragen zonder geschikte of verifieerbare bron.
- `reports/`: lokale/CI-rapporten; niet gecommit. Een slechte controle verwijdert geen bestaande data.

`homebrew` is onderzoeksmetadata; de installer verwacht voor `package_type` **game**, **update** of **dlc**.
Content ID, Title ID, packageversie en firmware komen waar mogelijk uit de openbare PKG-header/SFO.
Basisgame, update en DLC blijven afzonderlijke packages. Voor updates/DLC moet de passende basisgame aanwezig zijn.

De probe gebruikt anonieme HEAD en GET Range, maximaal 64 KiB per Range-request (header, laatste byte en begrensde publieke metadata).
Vereist: werkende redirects, HTTP 206 met correcte Content-Range, PS4-signatuur `7f434e54`, geldige Content ID, consistente HTTP-/headergrootte en bereikbare laatste byte.
HEAD 403/405/501 is alleen acceptabel als de Range-controles vervolgens slagen. Range die HTTP 200/HTML teruggeeft wordt afgewezen zonder het hele bestand te lezen.
Maximaal vijf redirects; geen credentials in URL's en geen HTTPS→HTTP-downgrade. Alleen persistente oorspronkelijke release-URL's worden opgeslagen; tijdelijke GitHub-redirecttokens niet.
Dit bewijst **niet** de integriteit van alle bytes, malwarevrijheid of installatie op hardware. Een volledige checksumcontrole vereist een volledige download en gebeurt niet standaard.

GitHub Actions valideert iedere push/PR en voert de **daadwerkelijke upstream C++-catalogusparser** uit op een vastgezette revisie; zie [compatibiliteit](docs/compatibility.md).
Na succes publiceert de workflow alleen `games.json` via GitHub Pages. De overige bestanden zijn zichtbaar in de openbare repository.
Iedere maandag om 07:23 UTC controleert een afzonderlijke workflow alle package-URL's. Het rapport is als Actions-artifact beschikbaar; bij fouten faalt de run zonder cataloguswijzigingen.

Geen tokens, wachtwoorden, persoonlijke bestanden of PKG-bestanden committen. Geen captcha's, betaalmuren of toegangscontroles omzeilen.
