# Personal PS4 Catalog

Persoonlijke catalogus voor de bestaande [PS4 Games Installer](https://github.com/e1z0/PS4-Games-Installer).
De PS4 downloadt toegestane packages rechtstreeks van de oorspronkelijke ontwikkelaar. Deze repository bevat geen PKG-bestanden.

## Privébibliotheek via Google Drive op deze pc

Naast de openbare catalogus hieronder gebruikt de eigenaar een privébibliotheek op Google Drive. Rclone geeft de bestanden tijdens downloaden/installeren via de pc door aan de PS4. De volledige Apollo-testdownload is met de ontwikkelaarschecksum gecontroleerd; de eigenaar heeft vervolgens een geslaagde installatie op zijn PS4 gemeld. Andere packages vereisen hun eigen installatieproef.

De blijvende, ontdubbelde speellijst en downloadinventaris staan lokaal in `D:\PS4-bibliotheek\games-overzicht.json` en `games-overzicht.txt`, met een privékopie in de Drive-map `PS4-Library`. Basisgames, updates, DLC en editievoorkeuren worden apart bijgehouden. De privé-package-index is `%LOCALAPPDATA%\PS4Drive\library.json`; de startknop leest deze volledige index opnieuw, ook nadat lokale PKG-kopieën op verzoek zijn opgeruimd.

De start-/stopknoppen staan op het bureaublad in `PS4 Google Drive`. De juiste lokale Games JSON URL staat in `%LOCALAPPDATA%\PS4Drive\PS4-URL.txt`. De pc blijft aan tijdens downloaden/installeren. Google gebruikt een eigen client met beperkte `drive.file`-toegang; de Google-app staat voorlopig in testmodus, wat opnieuw aanmelden kan vereisen. Alleen via deze koppeling aangemaakte Drive-bestanden zijn voor deze beperkte toegang zichtbaar.

De persoonlijke inventaris, backups en aanmeldgegevens worden privé bewaard. Deze repository bevat de openbare ontwikkelaarscatalogus en projectdocumentatie.

## Openbare ontwikkelaarscatalogus

**Games JSON URL:**

```text
https://damian98v.github.io/personal-ps4-catalog/games.json
```

## Aansluiten op je PS4

1. Activeer je bestaande GoldHEN-omgeving en open PS4 Games Installer. Gebruik een recente officiële versie met HTTPS-ondersteuning.
2. Ga naar **OPTIONS → Settings → Games JSON URL** en vul bovenstaande URL exact in.
3. Kies **Test connection**, daarna **Save settings**.
4. Kies **OPTIONS → Refresh library**. Open **Available** (L1/R1 wisselt Installed/Available).
5. Selecteer een beschikbare game en druk **X** om de installatie te bevestigen. De catalogus is momenteel leeg na verwijdering van de testitems.
6. Bekijk de voortgang onder **OPTIONS → Downloads**. Wacht op **Completed**.

De PS4 heeft internet nodig en moet zowel GitHub Pages als GitHub releasebestanden kunnen bereiken.
De juiste datum/tijd op de PS4 is nodig voor TLS. Je computer hoeft na publicatie niet aan te blijven.
HTTPS-packages worden door de installer eerst naar interne opslag gedownload. Houd de app tijdens het downloaden open en reserveer ruimte voor het package én de installatie.

**De catalogus is op afstand getest; een installatie op fysieke PS4-hardware is niet door Codex uitgevoerd.**

### Bekend probleem met installer r40

De nieuwste officiële download is momenteel r40. De gebundelde certificaten en algemene HTTPS-reparaties zijn echter pas **na r40** aan de officiële broncode toegevoegd. Een geslaagde catalogusparsertest op de computer bewijst daarom niet dat de r40-app GitHub via HTTPS kan bereiken.
Bij `Send request … Check the JSON endpoint` ondanks werkend internet: controleer de appversie (OPTIONS → About), volledige foutcode en PS4-klok. De gebruiker heeft deze fout met r40 gemeld. Pas hiervoor niet de PS4-systeemsoftware aan.
De handmatige Actions-workflow `Build installer with upstream HTTPS fixes` bouwt de officiële broncode op revisie `f9212596bafd1011aec594cd8c5bd0d05cff938a` met een kleine response-headerreparatie, draait upstreamtests en valideert het package. Dit is een eigen build van de bestaande app, geen officiële upstreamrelease; werking op de eigen PS4 moet nog worden getest. Het downloadbare artifact bevat het PKG, checksum, buildmanifest, bijbehorende aangepaste broncode en de productiepatch.
De ongewijzigde upstream pc-tests hebben loggingproblemen en verouderde certificaatfixtures: een PS4-functie wordt in de hostfallback aangeroepen, de native HTTP-test linkt de logger niet en de HTTP-/opstartfixtures verwachten nog geen Let's Encrypt-certificaat. Alleen voor de pc-tests wordt dit na packaging aangepast; de patch wordt bijgeleverd en vóór packagehercontrole teruggedraaid. De PS4-binary bevat deze testaanpassingen niet.

**Oudere build r48 (vervangen door r49):** de [build en download](https://github.com/Damian98v/personal-ps4-catalog/actions/runs/43461192199) bevat het artifact `ps4-installer-https-fixes` (30 dagen bewaard). De onderstaande r49 verhelpt de daarna op de PS4 vastgestelde downloadfout.
Sluit de bestaande installer en installeer het PKG als app-update via je gebruikelijke PKG-installatiemethode (bijvoorbeeld USB of FTP). Verwijder de bestaande app niet vooraf. De Title ID blijft `PGIN00001`; packageversie is `00.48`. Open daarna de installer, bevestig bovenstaande Games JSON URL en gebruik Test connection, Save settings en Refresh library.
Deze build doorstond de volledige C++-/HTTP-testreeks en alle 19 Python-tests met de bijgeleverde host-testaanpassingen. Het package is opnieuw gevalideerd na herstel van de oorspronkelijke broncode. SHA-256: `d705be59668ac468dfb4360b9cd051f2ef7c280d5e12f83b41cb49841b54af37`. Installatie en verbinding op de eigen fysieke PS4 zijn nog niet bevestigd.

**Downloadfout na r48:** de gebruiker kan de catalogus inmiddels laden, maar PS4 2048 faalt bij `github.com (redirect 0)` met `0x80431073` en dezelfde waarde in errno. Dit is `HTTP_ERROR_TOO_LARGE_RESPONSE_HEADER`; de CA-store is geladen (`ca=123`, `ca_load=0`). Bij controle gaf GitHub ongeveer 5,8 KiB aan redirectheaders terug. De oorspronkelijke code begrenst zijn eigen parser op 64 KiB maar configureert de kleinere native ontvangstbuffer niet. `scripts/patch_installer_headers.py` stelt daarom via de bestaande HTTP-module `sceHttpSetResponseHeaderMaxSize` op 64 KiB in, voegt een native regressietest toe en houdt certificaatcontrole en de bestaande bovengrens intact. De workflow bouwt deze opvolger als r49; werking op de PS4 vereist een nieuwe downloadtest.

**Gebruik r49:** [geslaagde build en download](https://github.com/Damian98v/personal-ps4-catalog/actions/runs/43465027590), artifact `ps4-installer-https-fixes`, installatiebestand `PS4Game_installer-r49.pkg` (6.619.136 bytes). Appversie `00.49`, Title ID `PGIN00001`; SHA-256 `3f7295b3476da0fce97b3c909205607490c8aaab1984bf404a731b4a31118bb2`. Native HTTP-regressies inclusief grote redirectheaders, de overige C++-tests, HTTP-integratietests en alle 19 Python-tests slagen. Installeer als app-update, open Downloads en probeer PS4 2048 opnieuw met X. Succes op de eigen PS4 is nog niet bevestigd.

## Eerste testitems (verwijderd)

PS4 2048 en Apollo Save Tool zijn op verzoek uit de actieve catalogus verwijderd. `games.json` bevat momenteel een geldig leeg DATA-object. Hieronder staan alleen de historische testgegevens; verwijderen uit de catalogus verwijdert geen app op de PS4.

| Package | Packageversie | Grootte | Functie |
| --- | --- | ---: | --- |
| PS4 2048 | 1.00 | 35.454.976 bytes | Zelfstandig puzzelspel, officiële GitHub-release v1.0 |
| Apollo Save Tool | 02.40 | 22.806.528 bytes | Zelfstandig homebrewhulpmiddel voor je eigen savegames, release v2.4.0 |

Beide komen rechtstreeks van de ontwikkelaars en hebben geen commerciële gamebestanden nodig om te starten.
`SYSTEM_VER` is in beide packages nul; `min_fw` blijft daarom onbekend (`null`). Dit is geen claim dat elke firmware werkt.
De GitHub-release van 2048 is ouder dan de PKG-Zone-versie. PKG-Zone gaf tijdens de downloadcontrole HTTP 403 en is niet als werkende bron toegevoegd.
Apollo is een hulpmiddel, geen game; het staat in dezelfde lijst zodat één Games JSON URL volstaat.

## Aangevraagde games

De op 13 november 2026 opgegeven lijst bevat **31 unieke titels/bundels**. Vice City is ondergebracht bij GTA: The Trilogy; de gebruiker heeft bevestigd dat GTA V niet gewenst is. Voor alle 31 is een PS4-uitgave gevonden. Voor geen van deze aanvragen is tot nu toe een gecontroleerde, geautoriseerde directe PKG-download van de volledige basisgame gevonden. Er zijn dus geen nieuwe actieve items toegevoegd. De volledige onderzoeksgegevens staan in [missing.json](missing.json).

| # | Titel / officiele PS4-bron | Directe PKG-bron |
| --- | --- | --- |
| 1 | [Uncharted 4: A Thief's End](https://www.playstation.com/en-us/games/uncharted-4-a-thiefs-end/) | Nog nodig |
| 2 | [Call of Duty: Modern Warfare 2 Campaign Remastered](https://www.playstation.com/en-us/games/call-of-duty-modern-warfare-2-campaign-remastered/) | Nog nodig |
| 3 | [Marvel's Spider-Man](https://www.playstation.com/en-us/games/marvels-spider-man/) | Nog nodig |
| 4 | [Crash Bandicoot N. Sane Trilogy](https://www.playstation.com/en-us/games/crash-bandicoot-n-sane-trilogy/) | Nog nodig |
| 5 | [Grand Theft Auto: The Trilogy - The Definitive Edition](https://www.playstation.com/nl-nl/games/grand-theft-auto-trilogy-definitive-edition/) | Nog nodig |
| 6 | [Assassin's Creed IV: Black Flag](https://store.playstation.com/en-in/product/EP0001-CUSA00009_00-AC4GAMEPS4000001) | Nog nodig |
| 7 | [It Takes Two](https://www.playstation.com/en-us/games/it-takes-two/) | Nog nodig |
| 8 | [A Way Out](https://www.playstation.com/en-us/games/a-way-out/) | Nog nodig |
| 9 | [Gang Beasts](https://store.playstation.com/en-us/product/UP2154-CUSA04794_00-GANGBEASTSPS04NA) | Nog nodig |
| 10 | [Far Cry 3 Classic Edition](https://www.playstation.com/en-us/games/far-cry-3-classic-edition/) | Nog nodig |
| 11 | [The Witcher 3: Wild Hunt - Complete Edition](https://store.playstation.com/en-us/concept/204794) | Nog nodig |
| 12 | [Outlast](https://www.playstation.com/en-us/games/outlast/) | Nog nodig |
| 13 | [The Sims 4](https://www.playstation.com/en-us/games/the-sims-4/) | Nog nodig |
| 14 | [Stardew Valley](https://store.playstation.com/en-us/product/UP2456-CUSA06840_00-STARDEW00000SIEA) | Nog nodig |
| 15 | [Assassin's Creed Origins](https://store.playstation.com/en-us/product/UP0001-CUSA05855_00-GAMEACEMPIRE0000) | Nog nodig |
| 16 | [Far Cry 5](https://store.playstation.com/en-us/product/UP0001-CUSA05904_00-FARCRY5GAME00000) | Nog nodig |
| 17 | [Star Wars Jedi: Fallen Order](https://www.playstation.com/en-us/games/star-wars-jedi-fallen-order/) | Nog nodig |
| 18 | [Until Dawn](https://store.playstation.com/en-us/product/UP9000-CUSA00359_00-UNTILDAWN0000001) | Nog nodig |
| 19 | [Assassin's Creed: The Ezio Collection](https://www.playstation.com/en-ph/games/assassins-creed-the-ezio-collection/) | Nog nodig |
| 20 | [Spyro Reignited Trilogy](https://www.playstation.com/en-us/games/spyro-reignited-trilogy/) | Nog nodig |
| 21 | [Assassin's Creed Odyssey](https://www.playstation.com/en-us/games/assassins-creed-odyssey/) | Nog nodig |
| 22 | [South Park: The Fractured But Whole](https://www.playstation.com/en-us/games/south-park-the-fractured-but-whole/) | Nog nodig |
| 23 | [Dying Light 2 Stay Human](https://www.playstation.com/en-us/games/dying-light-2-stay-human/) | Nog nodig |
| 24 | [Dead Island 2](https://store.playstation.com/en-us/product/UP2047-CUSA01014_00-DI2MAINSIEAPS400) | Nog nodig |
| 25 | [Middle-earth: Shadow of Mordor](https://store.playstation.com/en-sa/product/EP1018-CUSA00053_00-SHADOWOFMORDOR01) | Nog nodig |
| 26 | [LEGO Jurassic World](https://www.playstation.com/en-us/games/lego-jurassic-world/) | Nog nodig |
| 27 | [Monopoly Plus](https://store.playstation.com/en-us/concept/202832) | Nog nodig |
| 28 | [Heavy Rain](https://www.playstation.com/en-us/games/heavy-rain/) | Nog nodig |
| 29 | [South Park: The Stick of Truth](https://www.playstation.com/en-ph/games/south-park-the-stick-of-truth/) | Nog nodig |
| 30 | [Star Wars Battlefront](https://store.playstation.com/en-us/product/UP0006-CUSA00640_00-BATTLEFRONT00000) | Nog nodig |
| 31 | [MX vs ATV Legends](https://store.playstation.com/en-us/concept/10000928/) | Nog nodig |

The Sims 4 is als basisgame gratis via de PlayStation Store, maar een Store-vermelding is geen directe PKG-bron. De gecontroleerde Monopoly Plus-vermelding is momenteel niet te koop in die Store-regio. Proefversies, Friend Passes en alleen-PS5-packages gelden niet als de gevraagde volledige PS4-game. Beschikbaarheid van een PS4-uitgave bevestigt niet dat die op de firmware van de gebruiker werkt.

### Aanvullende brede PKG-zoekronde

Voor alle 31 titels is ook buiten de officiele winkels expliciet op PS4-PKG gezocht. Er bestaan derdenvermeldingen van volledige games, maar die zijn niet automatisch gecontroleerd of geautoriseerd. De eerdere uitkomst betekent dus niet dat er nergens PKG-vermeldingen bestaan. De concrete netwerkcontroles hebben twee echte bestanden op Sony's publieke downloadserver opgeleverd:

| Titel | Gecontroleerd bestand | Bytes | Resultaat |
| --- | --- | ---: | --- |
| Assassin's Creed IV: Black Flag | Update 01.04, CUSA00009 | 2.313.158.656 | HTTP 206, geldige PS4-header/SFO, grootte en eindbyte gecontroleerd |
| Monopoly Plus | Update 01.01, CUSA00773 | 515.309.568 | HTTP 206, geldige PS4-header/SFO, grootte en eindbyte gecontroleerd |

De originele HTTP-links en de volledige controlebewijzen staan bij deze titels in missing.json. De HTTPS-variant van deze oudere Sony-host sloot de verbinding bij controle; de oorspronkelijke HTTP-links werken wel. Beide packages hebben SFO-categorie gp (patch), vereisen een passende basisgame/licentie en zijn geen vervanging voor een complete game. Ze zijn niet aan games.json toegevoegd. Installatie op de eigen PS4 is niet getest.

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
