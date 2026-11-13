# Personal PS4 Catalog — instructies voor Codex

## Doel en autorisatie

De gebruiker beheert zijn PS4-library vanuit Codex-chat. Maak de gevraagde cataloguswijzigingen concreet, test ze, commit en push ze automatisch naar `main` van `Damian98v/personal-ps4-catalog` en controleer publicatie. Deze workflow is door de gebruiker gevraagd; vraag geen nieuwe toestemming voor routinematige cataloguscommits/publicatie. Vraag wel tussenkomst als GitHub-authenticatie ontbreekt. Gebruik nooit force push en commit geen andere persoonlijke bestanden.

Openbare catalogus: https://damian98v.github.io/personal-ps4-catalog/games.json
Python 3.11+, alleen standaardbibliotheek. macOS: `python3`; Windows: `python`.
Lees README.md, games.json, sources.json, research.json en missing.json voor je wijzigingen maakt. Inspecteer Git-status/remotes en behoud niet-gerelateerde wijzigingen.

## Games of homebrew toevoegen

Bij “Voeg deze games toe aan mijn PS4”:

1. Identificeer elke exacte titel en of een PS4-versie bestaat. Zoek officiële ontwikkelaarssites en GitHub-releases; gebruik webonderzoek voor nieuwe bronnen. Het script kan GitHub-kandidaten vinden, maar bewijst geen PS4-release/toestemming.
2. Controleer distributietoestemming, PS4-platform, zelfstandige werking en benodigde extra bestanden. Geen ongeautoriseerde commerciële PKG's. Leg relevante bronlinks en jouw bevindingen vast. Vraag geen downloadlink als een officiële geschikte release vindbaar is.
3. Bekende onderzochte bron: `python3 scripts/add_games.py 'Titel'`. Nieuwe bron: leg naam, aliases, exact ontwikkelaarrepo + PS4 `asset_pattern`, authorization_url/authorization, reviewed_on, standalone/requirements, kind, package_type en optionele cover/firmware vast in sources.json. Bekijk README voor directe, door gebruiker toegestane URL's met exacte allowed_urls.
4. Gebruik het script om het package daadwerkelijk te controleren. Alleen geslaagde probes mogen nieuwe actieve items opleveren. Geen handmatige status “verified” verzinnen en geen schema-/Range-controles versoepelen om een bron te laten slagen.
5. Geen geschikte bron of onbekende toestemming: registreer/hergebruik een aanvraag in missing.json met titel, status, onderzoekslinks, reden en wat nog nodig is. Doe dit ook als je geen script kunt uitvoeren. Vertel welke eigen geautoriseerde bron ontbreekt.
6. Valideer de **hele** catalogus, voer tests uit en publiceer via `python3 scripts/publish.py --message 'Add verified …'`. Controleer GitHub Actions en het publiek gepubliceerde document. Alleen geslaagde push is geen bewijs van geslaagde Pages-publicatie.
7. Rapporteer toegevoegde titels, versies, ontbrekende aanvragen, uitgevoerde tests en PS4-URL. Claim nooit een hardware-installatie zonder echte hardwaretest.

## Andere chatopdrachten

- “Controleer kapotte links”: `python3 scripts/validate_catalog.py --online --report reports/links.json`; rapporteer fouten. Niet automatisch verwijderen, deactiveren of succesvolle controledatums overschrijven bij tijdelijke netwerkfouten. Een read-only controle vereist geen commit.
- “Werk downloadlinks bij”: onderzoek nieuwe persistente officiële URL's; werk alleen bij na succesvolle controle en toestemming. Bewaar eerdere records als de vervanging onbevestigd is.
- “Controleer nieuwe homebrewversies”: lees sources.json, query officiële stable releases en vergelijk release_tag/asset/APP_VER met research.json. Gebruik add_games.py --refresh voor geschikte nieuwe releases. Onderzoek gewijzigde vereisten; installeer niet blind een ander PS4/PS5-asset. Nieuwe packageversies mogen als aparte items blijven staan.
- “Verwijder deze game”: verwijder alleen de gevraagde URL(s) uit games.json én overeenkomstige research.json-records. Onderscheid basisgame/update/DLC als de opdracht specifiek is. Als de titel eenduidig is, voer verwijdering uit en publiceer. Dit verwijdert niets op de fysieke PS4.
- “Welke games kon je niet vinden”: lees missing.json en rapporteer; onderscheid tijdelijk onbevestigd van geen geautoriseerde bron.

## Compatibiliteit en gegevens

Gebruik het FPKGi DATA-object: package-URL is de sleutel, ondersteunde metadata het object. Ondersteunde velden staan in scripts/catalog.py en docs/compatibility.md. Geen eigen type “homebrew” in package_type: gebruik game/update/dlc en sla kind in research.json op. Homebrew in Games is opzettelijk voor één configuratie-URL.
Behoud onbekende gegevens als null; firmware nul in SFO is geen bewezen firmwareminimum. Gebruik APP_VER uit het package, niet blind de releasetag. Regio niet afleiden uit een fictieve homebrew-publishercode. Bewaar bron/toestemming/controledatum buiten games.json.
Bewaar oorspronkelijke GitHub-release-URL's, nooit aflopende release-assets-redirects met tokens. Geen cookies of downloadcredentials. Geen volledige bestanden downloaden voor normale controles.
Let op: de officiële release r40 bevat niet de algemene HTTPS-reparaties uit de huidige main-branch. De gebruiker meldde r40 en Send request-fouten ondanks werkend internet. Controleer geïnstalleerde appversie en foutcode; claim niet dat r40 de gebundelde CA-store heeft. De handmatige build-installer.yml bouwt de bestaande ongewijzigde upstreamcode met fixes. Geen PS4-systeemfirmware-update voorstellen als oplossing.
Een r48-PKG is succesvol gebouwd in Actions-run 43461192199, met volledige upstream C++-/HTTP-tests en 19 Python-tests na gedocumenteerde testharnessaanpassingen. De PS4-binary is uit ongewijzigde upstreamcode gebouwd. De download en checksum staan in README.md; lokaal stond het package bij oplevering in C:/Users/Damian/Downloads/PS4-Installer-HTTPS-43461192199/. De gebruiker moet de hardware-update en verbinding nog testen. Claim niet dat het probleem al op de PS4 is opgelost.
Nieuwste hardwaremelding: gebruiker kan de catalogus laden, maar downloaden van PS4 2048 faalt op github.com bij redirect 0 met 0x80431073, errno=-2143088525, ca=123, ca_load=0, keepalive=1. Dit is een te kleine native response-headerbuffer. De nieuwe buildworkflow past scripts/patch_installer_headers.py toe (64 KiB native limiet, dezelfde bestaande parserlimiet, regressietest); deze PS4-broncode bevat dus een gedocumenteerde lokale reparatie naast upstream. r49 is daarvoor gereserveerd. Geen DNS-/firmwarewijziging adviseren voor deze aangetoonde fout; hardwarehertest blijft nodig.
r49 is succesvol gebouwd in Actions-run 43465027590. De nieuwe native regressietest en volledige upstreamtests (incl. 19 Python-tests) slagen. PKG en broncode staan in het Actions-artifact; lokaal C:/Users/Damian/Downloads/PS4-Installer-r49-43465027590/PS4Game_installer-r49.pkg. Checksum en instructies staan in README.md. De gebruiker moet nog bevestigen of downloaden/installeren op zijn PS4 werkt.
Voorkom dubbele JSON-sleutels en dubbele Content ID + versie + type; basisgame/update/DLC en echte nieuwe versies zijn verschillende packages.
Stuur geen berichten aan derden. Geen nieuwe PS4-app of zware infrastructuur bouwen.
