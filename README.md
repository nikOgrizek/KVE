# KalkulatorVetreneEnergije

KalkulatorVetrneEnergije je aplikacija namenjena izračunu potencialne proizvodnje električne energije. Njena uporaba je preprosta, saj mora uporabnik samo izbrati lokacijo(-e) ter nato izbrati turbine, za katere želi narediti izračun na lokaciji. Ta README datoteka služi kot predstavitev projekta, skupaj z navodili za namestitev in uporabo.

## Člani ekipe KalkulatorVetrneEnergije

- [Luka Majstorović](https://github.com/Majst0rL)
- [Niko Ogrizek](https://github.com/nikOgrizek)
- [Kristijan Stefanovski](https://github.com/Kiksa05)

## Kazalo vsebine projekta

1. Predstavitev projekta
2. Dokumentacija
    - Funkcionalnosti
    - Tehnološki nabor
    - Organizacija in način dela
    - Zasnova podatkovne strukture
    - Wireframe aplikacije (prototip izgleda)
3. Navodila za namestitev lokalno
4. Uporaba aplikacije
5. [Predstavitev

## 1. Predstavitev projekta

### Podroben opis projekta

Projekt "KalkulatorVetrneEnergije" je interaktivno orodje, zasnovano za ocenjevanje potencialne proizvodnje električne energije iz vetrnih turbin na podlagi izbranih lokacij na zemljevidu. Uporabniki lahko izbirajo med različnimi tipi turbin, dodajajo nove turbine in urejajo obstoječe, pri čemer aplikacija izračuna pričakovano proizvodnjo energije glede na specifične vetrovne pogoje vsake lokacije. Rezultati izračunov vključujejo podrobne podatke o letni proizvodnji energije, kar omogoča natančno analizo in načrtovanje. Končne podatke je možno shraniti in izvoziti v obliki PDF poročila, kar omogoča enostavno deljenje in arhiviranje rezultatov.

## 2. Dokumentacija

### Funkcionalnosti

- Izbira lokacij
- Izbira turbin
- Dodajanje turbin
- Urejanje turbin
- Izračun potencialne proizvodnje
- Prikaz rezultatov
- Shranjevanje rezultatov v PDF

### Tehnološki nabor

**Backend (zaledje)**  
Zaledje aplikacije je izdelano v programskem jeziku Python in je razdeljeno na več datotek, vsaka z jasno določeno odgovornostjo, kar omogoča modularnost in lažje vzdrževanje kode. Ena datoteka je zadolžena za pridobivanje vremenskih podatkov preko API-ja, druga za kalkuliranje potencialne proizvodnje energije, tretja pa za ustvarjanje in izvoz PDF poročil. Ta struktura zagotavlja, da je vsaka komponenta specializirana in neodvisna, kar omogoča boljšo organizacijo kode in lažje dodajanje novih funkcionalnosti.

**Frontend (pročelje)**  
Pročelje aplikacije je zasnovano v Tkinter, vgrajenem modulu za izdelavo grafičnih uporabniških vmesnikov (GUI) v Pythonu. Tkinter omogoča ustvarjanje vmesnika, kjer lahko uporabniki enostavno izbirajo lokacije na zemljevidu, dodajajo in urejajo podatke o vetrnih turbinah ter si ogledujejo in izvažajo rezultate izračunov. Tkinter zagotavlja, da je interakcija z aplikacijo tekoča in enostavna, kar izboljšuje uporabniško izkušnjo.

### Organizacija in način dela

**Komunikacija**  
Komunikacija med člani ekipe je potekala v namenskem Discord strežniku, v katerem so bili namenski kanali, ki so pomagali ločiti vsebino, ki smo jo potrebovali za razvoj aplikacije. Komunikacija s profesorjem ter naročnikom (DEM) je potekala preko e-pošte in MS Teams.

**Vodenje in deljenje dela**  
Vodenje dela je potekalo v spletni aplikaciji Trello, kjer so se ustvarili task-i, ki smo jih premikali iz TO-DO v DOING in DONE. K vsakemu task-u je bil dodeljen razvijalec ali več razvijalcev, prav tako pa je vsak task imel določeno stopnjo prioritete (NOT IMPORTANT, MEDIUM, IMPORTANT).

### Zasnova podatkovne strukture

Aplikacija za delovanje ne potrebuje veliko podatkov, ki bi se morali hraniti v PB. Za učinkovito delovanje se hranijo samo podatki o turbinah, ki so shranjeni v JSON datoteki poimenovani `turbines.json`. Primer zapisa:

```json
{
    "name": "SG 6.6-170 Rev. 2, AM-1",
    "speeds": ["3.0", "3.5", "4.0", "4.5", "5.0", "5.5"],
    "powers": ["46", "164", "325", "523", "765", "1052"]
}
```

## Wireframe aplikacije
S pomočjo spletnega orodja Figma smo izdelali prototip, kako bo aplikacija izgledala. S pomočjo prototipa smo nato naredili GUI.

![Posnetek zaslona 2024-06-09 124332](https://github.com/Majst0rL/KalkulatorVetreneEnergije/assets/162917010/ed8154de-4daa-4ae7-8c0b-3cc3363451f1)


## 3. Navodila za namestitev lokalno
## Testno lokalno okolje
Za namestitev aplikacije lokalno na vašem računalniku smo pripravili exe verzijo v posebnem repozitoriju, ki je dostopna na tej povezavi.

## Koraki za zagon
1. Prenesite exe datoteko iz repozitorija.
2. Zaženite exe datoteko.
3. Sledite navodilom na zaslonu za namestitev.

## 4. Uporaba aplikacije
Uporaba aplikacije je izjemno preprosta. Ob zagonu se nam odpre glavno okno poimenovano KALKULATOR, na katerem je možno izvajati kalkulacije. Na vrhu lahko dostopamo še do dveh oken: TURBINE in POROČILA.

### Zavihek TURBINE
V tem zavihku je mogoče dodajati nove turbine, urejati obstoječe ali pa turbino izbrisati iz seznama dodanih turbin. Za dodajanje turbine preprosto vpišemo naziv turbine, ter nato poljubno število kombinacij hitrosti vetra (WindSpeed[m/s]) ter moči (Power[kW]). Dodajanje zaključimo s pritiskom na gumb DODAJ TURBINO. Za urejanje/brisanje turbine preprosto izberemo turbino v seznamu in nato kliknemo na gumb Izberi turbino. Urejanje izvedemo v formi, dokončamo pa s pritiskom na gumb Posodobi podatke; brisanje pa izvedemo s klikom na gumb Izbriši turbino (turbino je potrebno najprej izbrati).

### Glavno okno aplikacije (KALKULATOR)
V glavnem oknu se nahaja zemljevid, na katerem izberemo lokacije za katere želimo narediti izračun. Ob kliku na lokacijo se odpre okno, v katerem s klikom označimo turbine, za katere želimo da se izvede izračun. Lokacijo uspešno dodamo ko izberemo turbine ter potrdimo z klikom na gumb Potrdi. Za izračun je mogoče dodati več lokacij. Pred izračunom vidimo tudi katere koordinate smo izbrali za kalkulacijo potencialne veterne proizvodnje. Kalkulacijo izvedemo s klikom na gumb IZRAČUNAJ. Izračun lahko traja nekaj trenutkov. Nato se rezultati izračuna prikažejo na desni strani v polju poročilo izračuna. Rezultate je možno shraniti v PDF poročilo, kjer dobimo še bolj podrobno analizo.

### Zavihek POROČILA
Zavihek omogoča pregled in iskanje ustvarjenih PDF poročil.

## 5. Predstavitev
Predstavitev in screenshoti aplikacije se nahajajo v datoteki _PROMOCIJA.
