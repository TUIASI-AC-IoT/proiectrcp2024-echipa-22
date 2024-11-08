#                                                               Implementare mDNS și DNS-SD. Documentație Tehnică 

Introducere:
Acest proiect implementează un sistem de descoperire a serviciilor folosind mDNS (Multicast DNS) și DNS-SD (DNS Service Discovery). Aplicația permite monitorizarea resurselor sistemului și expunerea lor ca servicii în rețeaua locală.

# Introducere:

1. **mDNS (Multicast DNS)**  este o tehnologie care permite realizarea operațiilor de tip DNS într-o rețea locală mică, fără a necesita un server DNS centralizat. Fiecare dispozitiv din rețea poate obține automat un nume unic de tipul „MyComputer.local”, făcând mai ușoară identificarea și comunicarea între dispozitivele conectate.


# Tipuri de mesaje mDNS
1. Query (Cerere):
Acest mesaj este trimis atunci când un dispozitiv dorește să afle informații despre un alt dispozitiv din rețea. De exemplu, dacă un dispozitiv vrea să cunoască adresa IP asociată unui anumit nume (ex. „MyComputer.local”), va trimite un mesaj de tip query. Query-urile sunt trimise către o adresă de multicast specială (de obicei, 224.0.0.251 pentru IPv4 sau FF02::FB pentru IPv6, 5353 port standard), astfel încât toate dispozitivele din rețea să le poată recepționa.
2. Response (Răspuns):
Atunci când un dispozitiv primește o cerere care îi corespunde, acesta trimite un răspuns mDNS. De exemplu, dacă un dispozitiv a primit o cerere pentru „MyComputer.local” și acesta este numele său, va răspunde cu adresa sa IP. Răspunsurile mDNS includ diferite tipuri de înregistrări DNS, cum ar fi A (pentru adresa IP), PTR (pentru servicii), SRV (pentru informații despre serviciu, port și protocol) și TXT (pentru date suplimentare despre serviciu). \
![Imagine1](https://github.com/TUIASI-AC-IoT/proiectrcp2024-echipa-22/blob/main/diverse/mDNS.png)

# DNS-SD (DNS-based Service Discovery)
2. **DNS-SD (DNS-based Service Discovery)** este o metodă prin care dispozitivele dintr-o rețea locală pot fi descoperite și identificate în funcție de serviciile pe care le oferă. Acest lucru permite dispozitivelor să colaboreze fără configurări complexe; de exemplu, un telefon poate trimite comanda de imprimare către o imprimantă din aceeași rețea, datorită faptului că ambele dispozitive se pot recunoaște reciproc și pot comunica direct. 

# Tipuri de înregistrări DNS folosite în DNS-SD
1. PTR (Pointer Record):
Aceste înregistrări indică prezența unui serviciu și direcționează către o înregistrare specifică de tip SRV. De exemplu, un serviciu de tip „_http._tcp.local” va avea un registru PTR care indică toate dispozitivele din rețea care rulează un server HTTP.
2. SRV (Service Record):
Înregistrările SRV oferă informații despre locația unui serviciu, inclusiv numele dispozitivului, portul pe care funcționează serviciul și protocolul (TCP sau UDP). Aceasta ajută dispozitivele să știe exact cum să acceseze serviciul respectiv.
3. TXT (Text Record):
Înregistrările TXT furnizează detalii suplimentare despre serviciu, cum ar fi versiunea software, funcționalități disponibile sau alte informații care pot fi utile pentru clienți. Acestea sunt transmise sub formă de perechi cheie-valoare.
4. A (Address Record):
Înregistrările A sunt folosite pentru a oferi adresa IP a unui dispozitiv, permițând accesul direct la serviciul găzduit pe dispozitivul respectiv. \
![Imagine2](https://github.com/TUIASI-AC-IoT/proiectrcp2024-echipa-22/blob/main/diverse/dns-ds.png)


# Cerințe Funcționale:

1.Utilizarea modulului socket pentru comunicație 
2.Implementarea structurii pachetelor mDNS/DNS-SD \
3.Monitorizarea resurselor sistemului (procesor, memorie, temperatură) \
4.Descoperirea serviciilor în rețeaua locală \
5.Implementarea mecanismului de caching \
6.Control TTL pentru monitorizare


# 1. Utilizarea modulului socket pentru comunicație
Primul pas în implementarea mDNS și DNS-SD este configurarea unui socket UDP care va trimite și va primi mesaje prin rețea folosind adrese multicast. Modulul socket din Python este ideal pentru acest tip de comunicație, fiind capabil să interacționeze cu rețelele de multicast.

1. Configurare Socket Multicast:
Creează un socket UDP configurat pentru comunicare multicast -> Se conectează la adresa multicast standard mDNS (224.0.0.251) și portul 5353 -> Configurează opțiunile necesare pentru multicast (TTL, loop-back

2. Creare Pachete DNS-SD:
    - Implementează structura standard a pachetelor DNS
    - Suportă atât pachete de tip query cât și response
    - Codifică corect numele serviciilor în format DNS
    - Include câmpurile PTR necesare pentru DNS-SD

3. Gestionare Serviciu:
    - Anunță periodic prezența serviciului în rețea
    - Răspunde la interogări despre serviciu
    - Menține TTL-ul serviciului

4. Monitorizare Rețea:
    - Ascultă continuu pentru interogări mDNS
    - Procesează pachetele primite
    - Răspunde automat la interogări relevante

# 2. Implementarea structurii pachetelor mDNS/DNS-SD
Pachetele DNS care sunt utilizate în mDNS și DNS-SD trebuie să respecte formatul specificat de RFC-urile 6762 și 6763. Aceste pachete pot include mai multe tipuri de înregistrări, cum ar fi SRV, PTR, A și TXT.

DNS-SD (DNS Service Discovery) folosește înregistrări DNS standard, dar într-un mod specific pentru descoperirea serviciilor. Iată structura principală:

1. Înregistrarea SRV (Service Record):
```
_serviciu._protocol.domeniu TTL IN SRV prioritate greutate port țintă
```
Unde:
- _serviciu: numele serviciului (ex: _http, _printer)
- _protocol: de obicei _tcp sau _udp
- prioritate: număr pentru prioritizare (0-65535)
- greutate: pentru load balancing (0-65535)
- port: portul pe care rulează serviciul
- țintă: numele host-ului care oferă serviciul

2. Înregistrarea PTR (Pointer Record):
```
_serviciu._protocol.domeniu TTL IN PTR nume_instanță._serviciu._protocol.domeniu
```
- Folosită pentru a enumera instanțele disponibile ale unui serviciu
- nume_instanță este un nume prietenos pentru serviciu

3. Înregistrarea A/AAAA:
```
host.domeniu TTL IN A adresa_IPv4
host.domeniu TTL IN AAAA adresa_IPv6
```
- Mapează numele host-ului la adresa IP

4. Înregistrarea TXT (opțională):
```
nume_instanță._serviciu._protocol.domeniu TTL IN TXT "cheie1=valoare1" "cheie2=valoare2"
```
- Conține metadate adiționale despre serviciu
- Format key-value pairs

Un exemplu complet pentru un server web:
```
# Înregistrare PTR pentru enumerare
_http._tcp.local. IN PTR WebServer._http._tcp.local.

# Înregistrare SRV pentru detalii conexiune
WebServer._http._tcp.local. IN SRV 0 0 80 host.local.

# Înregistrare A pentru rezolvare IP
host.local. IN A 192.168.1.100

# Înregistrare TXT pentru metadate
WebServer._http._tcp.local. IN TXT "version=1.0" "path=/"
```

Pentru mDNS (Multicast DNS):
- Folosește aceeași structură ca DNS normal
- Operează pe portul UDP 5353
- Folosește adresa multicast 224.0.0.251 pentru IPv4
- Numele de domeniu se termină în .local
- Pachetele sunt limitate la 9000 bytes
- Include câmpuri standard DNS header:
  - ID
  - Flags
  - Question count
  - Answer count
  - Authority count
  - Additional count

Aspecte importante:
1. TTL-urile sunt de obicei scurte pentru mDNS (câteva minute)
2. Răspunsurile pot include multiple înregistrări pentru eficiență
3. Se folosesc mecanisme de prevenire a coliziunilor pentru nume
4. Serviciile trebuie să răspundă la interogări multicast

Această structurare permite:
- Descoperirea automată a serviciilor în rețea
- Rezolvarea numelor fără server DNS central
- Actualizarea dinamică a informațiilor despre servicii
- Operare zero-configuration în rețele locale



# 3. Monitorizarea resurselor sistemului (procesor, memorie, temperatură)
Folosim funcțiile psutil pentru a colecta datele necesare, precum utilizarea CPU-ului, utilizarea memoriei sau temperaturile. Aceste informații vor fi expuse sub formă de servicii DNS-SD, permițând altor dispozitive să le acceseze prin rețea.\
Includerea informațiilor în pachetele de răspuns: Când un client solicită informații despre serviciu, vom adăuga datele de monitorizare în câmpurile TXT ale pachetului de răspuns mDNS/DNS-SD. Aceste câmpuri vor conține valorile metricilor colectate.Accesarea informațiilor de către clienți: Aplicațiile client care descoperă acest serviciu vor putea accesa și afișa informațiile de monitorizare din câmpurile TXT ale răspunsurilor mDNS/DNS-SD.


# 4. Descoperirea serviciilor în rețeaua locală
Pentru a descoperi serviciile disponibile în rețeaua locală, va trebui implementat un mecanism care trimite cereri multicast DNS. Aceste cereri vor solicita informații de la celelalte dispozitive din rețea care oferă servicii DNS-SD.

Pașii de implementare:

Trimiterea unor cereri mDNS pe portul 5353 către grupul multicast 224.0.0.251, care este utilizat pentru descoperirea serviciilor în rețea. \
Așteptarea de răspunsuri de la dispozitivele din rețea, care vor conține informații despre serviciile disponibile, incluzând tipurile de înregistrări SRV, PTR, A și TXT. \
Interpretarea răspunsurile primite și extragerea informațiilor relevante despre serviciile descoperite.

# 5. Implementarea mecanismului de caching

Un mecanism de caching este esențial pentru stocarea rezultatelor DNS pe o perioadă de timp determinată, în funcție de valoarea TTL (Time To Live). Acest cache va reduce numărul de cereri DNS repetate, optimizând astfel performanța aplicației.

Pașii de implementare:

Crearea unei structuri de date (de exemplu, un dicționar sau un obiect) pentru stocarea rezultatelor DNS. \
Asigurarea că fiecare înregistrare DNS din cache include un TTL asociat. Datele vor expira automat după intervalul de timp specificat. \
La expirarea TTL-ului unei înregistrări, aceasta va fi eliminată din cache sau actualizată.

# 6. Controlul valorii TTL pentru monitorizare

Pentru a oferi control asupra duratei de viață a înregistrărilor DNS, se va implementa o funcționalitate ce permite modificarea valorii TTL. Această opțiune ajută la gestionarea traficului de rețea și la utilizarea eficientă a resurselor sistemului.

Pașii de implementare:

La adăugarea unei înregistrări DNS în cache, se va permite configurarea unui TTL personalizat pentru fiecare înregistrare. \
Utilizatorii vor putea modifica valorile TTL-ului pentru fiecare resursă monitorizată, optimizând comportamentul aplicației conform nevoilor specifice.


# Resurse utile
Pentru a înțelege mai bine cum implementez aceste concepte,ne vom baza pe următoarele documente și resurse:

[RFC 6762 pentru detalii tehnice despre Multicast DNS (mDNS)](https://datatracker.ietf.org/doc/html/rfc6762) \
[RFC 6763 pentru informații despre DNS-based Service Discovery (DNS-SD)](https://datatracker.ietf.org/doc/html/rfc6763) \
[Documentația pentru socket în Python](https://docs.python.org/3/library/socket.html)
